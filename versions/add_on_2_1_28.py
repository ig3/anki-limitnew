# This Anki add-on limits the number of new cards, depending on the
# days "workload", which is the number of cards studied plus the
# nubers or new and review cards scheduled for the day.
#
# This only works with the V2 scheduler.
#
# This implementation accommodates changes with release 2.1.28, which
# moved parts of card counts to the back end rust code, where there
# are no hooks and no monkey patching possible.
#
# This forced a complete refactor of the implementation. The result is
# simpler and, I think, more correct. It does database queries on start
# and after each answer. They are quick enough on my small collection
# of decks but might be problematic for users with very large revlog.
#
# This was developed primarily against Anki 2.1.35. An earlier iteration
# was tested against 2.1.28. Nothing after 2.1.35 has been tested.
#
import itertools
from aqt import mw
from anki.schedv2 import Scheduler as SchedulerV2
from anki.utils import ids2str

# For new deck options
from anki.hooks import wrap
from aqt import gui_hooks
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf

# totalCount is the sum of all new and review cards due today
# and all new and review cards studied today (including repeats)
totalCount = 0

config = mw.addonManager.getConfig(__name__)

def updateConfig(newConfig):
    #print("updateConfig")
    global config
    config = newConfig

mw.addonManager.setConfigUpdatedAction(__name__,updateConfig)

    
def setupUI(self, Dialog):

    label1 = QLabel(self.tab)
    label1.setText("Workload Limit")
    label2 = QLabel(self.tab)
    label2.setText("cards")
    self.workloadLimit = QSpinBox(self.tab)
    self.workloadLimit.setMinimum(0)
    self.workloadLimit.setMaximum(9999)
    label3 = QLabel(self.tab)
    label3.setText("Workload Max")
    label4 = QLabel(self.tab)
    label4.setText("cards")
    self.workloadMax = QSpinBox(self.tab)
    self.workloadMax.setMinimum(0)
    self.workloadMax.setMaximum(9999)
    rows = self.gridLayout.rowCount()
    self.gridLayout.addWidget(label1, rows, 0, 1, 1)
    self.gridLayout.addWidget(self.workloadLimit, rows, 1, 1, 1)
    self.gridLayout.addWidget(label2, rows, 2, 1, 1)
    self.gridLayout.addWidget(label3, rows+1, 0, 1, 1)
    self.gridLayout.addWidget(self.workloadMax, rows+1, 1, 1, 1)
    self.gridLayout.addWidget(label4, rows+1, 2, 1, 1)



def load_conf(self):
    #print("load_conf")
    f = self.form
    c = self.conf["new"]
    f.workloadLimit.setValue(c.get('workloadLimit', 200))
    f.workloadMax.setValue(c.get('workloadMax', 250))


def save_conf(self):
    #print("save_conf")
    f = self.form
    c = self.conf["new"]
    c['workloadLimit'] = f.workloadLimit.value()
    c['workloadMax'] = f.workloadMax.value()

def initializeOptions():
    dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setupUI)
    DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
    DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')



# Card is like:
# card  <anki.cards.Card object at 0x7f5d444d2ca0> {'data': '', 'did': 1556071573193, 'due': 1620703464, 'factor': 1450, 'flags': 0, 'id': 1562347790990, 'ivl': 1, 'lapses': 3, 'lastIvl': 3, 'left': 4004, 'mod': 1620703274, 'nid': 1449636990402, 'odid': 0, 'odue': 0, 'ord': 1, 'queue': 1, 'reps': 34, 'type': 3, 'usn': -1}

def reviewerDidAnswerCard(reviewer, card, ease):
    global totalCount
    print("************")
    print("reviewerDidAnswerCard")
    # print("card ", card)
    # print("ease ", ease)
    totalCount += 1
    deck_id = card.did
    tree = mw.col.sched.deck_due_tree()
    for did in [deck_id] + [x["id"] for x in mw.col.decks.parents(deck_id)]:
        print("deck id ", did)
        limitDeck(did, tree)
    

def limitDeck(deck_id, tree):
    print("limitDeck ", deck_id)
    enablePerDeckLimits = config.get('enablePerDeckLimits', True)
    enableTotalLimits = config.get('enableTotalLimits', True)
    conf = mw.col.decks.confForDid(deck_id)
    # print("deck config ", conf)
    newPerDay = conf['new']['perDay']
    maxNew = newPerDay
    # print("newPerDay ", newPerDay)
    if enableTotalLimits:
        totalWorkloadLimit = config.get('totalWorkloadLimit', 200)
        #print("totalWorkloadLimit ", totalWorkloadLimit)
        totalWorkloadMax = config.get('totalWorkloadMax', 250)
        #print("totalWorkloadMax ", totalWorkloadMax)
        print("totalCount ", totalCount)
        excess = totalCount - totalWorkloadLimit
        print("excess ", excess)
        if excess > 0:
            range = totalWorkloadMax - totalWorkloadLimit
            ratio = excess / range
            #print("ratio ", ratio)
            maxNew = max(0, min(maxNew, int(round(newPerDay * (1 - ratio)))))
            #print("maxNew ", maxNew)

    node = mw.col.decks.find_deck_in_tree(tree, deck_id)
    print("node ", node)
    if enablePerDeckLimits:
        deckWorkloadLimit = conf['new'].get('workloadLimit',
                config.get('defaultDeckWorkloadLimit', 200))
        #print("deckWorkloadLimit ", deckWorkloadLimit)
        deckWorkloadMax = conf['new'].get('workloadMax',
                config.get('defaultDeckWorkloadMax', 250))
        #print("deckWorkloadMax ", deckWorkloadMax)
        dids = [deck_id]
        for name, id in mw.col.decks.children(deck_id):
            dids.append(id)
        print("dids ", dids)
        cardsStudied = mw.col.db.scalar(
            f"""
select count() from revlog join cards on cards.id = revlog.cid
where revlog.id > ? and cards.did in """ + ids2str(dids),
            (mw.col.sched.dayCutoff - 86400) * 1000
        )
        print("cardsStudied ", cardsStudied)
        workload = cardsStudied or 0
        if node:
            #print("add workload from counts")
            workload += node.learn_count + node.new_count + node.review_count
        print("deck workload ", workload)
        excess = workload - deckWorkloadLimit
        print("excess ", excess)
        if excess > 0:
            range = deckWorkloadMax - deckWorkloadLimit
            print("range ", range)
            ratio = excess / range
            print("ratio ", ratio)
            print("x ", newPerDay * (1 - ratio))
            print("x ", int(round(newPerDay * (1-ratio))))
            maxNew = max(0, min(maxNew, int(round(newPerDay * (1 - ratio)))))
            print("maxNew ", maxNew)

    print("maxNew ", maxNew, " Vs ", newPerDay)
    if node and node.new_count > maxNew:
        print("new_count ", node.new_count)
        delta = node.new_count - maxNew
        print("delta ", delta)
        mw.col.sched.update_stats(deck_id, new_delta=delta)


def onCollectionDidLoad(col):
    global totalCount
    enablePerDeckLimits = config.get('enablePerDeckLimits', True)
    enableTotalLimits = config.get('enableTotalLimits', True)

    # the due tree gives us cards due today
    tree = col.sched.deck_due_tree()
    print("tree ", tree)

    if enableTotalLimits:
        # We need total workload: studied + scheduled
        # The root of the tree has scheduled cards for all decks
        totalCount = tree.learn_count + tree.new_count + tree.review_count
        # For studied cards, a database query seems to be the only way
        cardsStudied = mw.col.db.scalar(
            "select count() from revlog where id > ? ",
            (mw.col.sched.dayCutoff - 86400) * 1000
        )
        cardsStudied = cardsStudied or 0
        print("cardsStudied ", cardsStudied)
        totalCount += cardsStudied
        print("totalCount ", totalCount)


    # For each deck, we need the total of cards scheduled + cards studied
    # This is the workload for the deck. We also need total scheduled + 
    # total studied. The totals are the sums of the per-deck totals, for top
    # level decks only.
    print("iterate over all decks")
    for x in col.decks.all_names_and_ids():
        limitDeck(x.id, tree)


if config.get('enablePerDeckLimits', False):
    initializeOptions()

gui_hooks.reviewer_did_answer_card.append(reviewerDidAnswerCard)
gui_hooks.collection_did_load.append(onCollectionDidLoad)
