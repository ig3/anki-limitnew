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
from anki.consts import *

# For new deck options
from anki.hooks import wrap
from aqt import gui_hooks
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf

# totalCount is the sum of all new and review cards due today
# and all new and review cards studied today (including repeats)
totalCount = 0
# Overdue cards only change at day rollover so we keep track of the 
# current day and check for overdue cards only if/when the day changes.
lastDay = 1

config = mw.addonManager.getConfig(__name__)

def updateConfig(newConfig):
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

    label5 = QLabel(self.tab)
    label5.setText("OverdueMax")
    label6 = QLabel(self.tab)
    label6.setText("cards")
    self.overdueMax = QSpinBox(self.tab)
    self.overdueMax.setMinimum(0)
    self.overdueMax.setMaximum(9999)

    label7 = QLabel(self.tab)
    label7.setText("Minimum New")
    label8 = QLabel(self.tab)
    label8.setText("cards")
    self.minimumNew = QSpinBox(self.tab)
    self.minimumNew.setMinimum(0)
    self.minimumNew.setMaximum(9999)

    rows = self.gridLayout.rowCount()
    # workloadLimit
    self.gridLayout.addWidget(label1, rows, 0, 1, 1)
    self.gridLayout.addWidget(self.workloadLimit, rows, 1, 1, 1)
    self.gridLayout.addWidget(label2, rows, 2, 1, 1)
    # workloadMax
    self.gridLayout.addWidget(label3, rows+1, 0, 1, 1)
    self.gridLayout.addWidget(self.workloadMax, rows+1, 1, 1, 1)
    self.gridLayout.addWidget(label4, rows+1, 2, 1, 1)
    # overdueMax
    self.gridLayout.addWidget(label5, rows+2, 0, 1, 1)
    self.gridLayout.addWidget(self.overdueMax, rows+2, 1, 1, 1)
    self.gridLayout.addWidget(label6, rows+2, 2, 1, 1)
    # minimumNew
    self.gridLayout.addWidget(label7, rows+3, 0, 1, 1)
    self.gridLayout.addWidget(self.overdueMax, rows+3, 1, 1, 1)
    self.gridLayout.addWidget(label8, rows+3, 2, 1, 1)


def load_conf(self):
    f = self.form
    c = self.conf["new"]
    f.workloadLimit.setValue(c.get('workloadLimit', 200))
    f.workloadMax.setValue(c.get('workloadMax', 250))
    f.overdueMax.setValue(c.get('overdueMax', 20))
    f.minimumNew.setValue(d.get('minimumNew', 1))


def save_conf(self):
    f = self.form
    c = self.conf["new"]
    c['workloadLimit'] = f.workloadLimit.value()
    c['workloadMax'] = f.workloadMax.value()
    c['overdueMax'] = f.overdueMax.value()
    c['minimumNew'] = f.minimumNew.value()

def initializeOptions():
    dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setupUI)
    DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
    DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')



# Card is like:
# card  <anki.cards.Card object at 0x7f5d444d2ca0> {'data': '', 'did': 1556071573193, 'due': 1620703464, 'factor': 1450, 'flags': 0, 'id': 1562347790990, 'ivl': 1, 'lapses': 3, 'lastIvl': 3, 'left': 4004, 'mod': 1620703274, 'nid': 1449636990402, 'odid': 0, 'odue': 0, 'ord': 1, 'queue': 1, 'reps': 34, 'type': 3, 'usn': -1}

def reviewerDidAnswerCard(reviewer, card, ease):
    global lastDay
    global totalCount
    global totalOverdue
    currentDay = mw.col.sched.today
    totalCount += 1
    deck_id = card.did
    tree = mw.col.sched.deck_due_tree()
    enableTotalLimits = config.get('enableTotalLimits', True)
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
        totalCount += cardsStudied
        # Overdue can only increase on day rollover
        if lastDay != mw.col.sched.today:
            overdue = mw.col.db.scalar(
                f"""
select count() from cards
where queue = {QUEUE_TYPE_REV} and due < ?""",
                mw.col.sched.today
            )
            overdue = overdue or 0
            print("total overdue ", overdue)
            totalOverdue = overdue

    for did in [deck_id] + [x["id"] for x in mw.col.decks.parents(deck_id)]:
        limitDeck(did, tree)
    lastDay = currentDay
    

def limitDeck(deck_id, tree):
    print("limitDeck ", deck_id)
    global totalCount
    global totalOverdue
    global lastDay
    enablePerDeckLimits = config.get('enablePerDeckLimits', True)
    enableTotalLimits = config.get('enableTotalLimits', True)
    conf = mw.col.decks.confForDid(deck_id)
    newPerDay = conf['new']['perDay']
    maxNew = newPerDay
    if enableTotalLimits:
        totalWorkloadLimit = config.get('totalWorkloadLimit', 200)
        totalWorkloadMax = config.get('totalWorkloadMax', 250)
        totalOverdueMax = config.get('totalOverdueMax', 50)
        totalMinimumNew = config.get('totalMinimumNew', 1)
        # Check workload
        if totalCount > totalWorkloadMax:
            maxNew = totalMinimumNew
        elif totalCount > totalWorkloadLimit:
            excess = totalCount - totalWorkloadLimit
            range = totalWorkloadMax - totalWorkloadLimit
            if range > 0:
                ratio = excess / range
                maxNew = max(totalMinimumNew, min(maxNew, int(round(newPerDay * (1 - ratio)))))
            else:
                maxNew = totalMinimumNew
        # Check overdue once per day
        # During a day, number of overdue cards can only go down, never up
        if lastDay != mw.col.sched.today:
            print("total overdue ", totalOverdue)
            if totalOverdue > totalOverdueMax:
                maxNew = totalMinimumNew
            elif totalOverdue > 0 and totalOverdueMax > 0:
                ratio = totalOverdue / totalOverdueMax
                maxNew = max(totalMinimumNew, min(maxNew, int(round(newPerDay * (1 - ratio)))))

    node = mw.col.decks.find_deck_in_tree(tree, deck_id)
    if enablePerDeckLimits:
        deckWorkloadLimit = conf['new'].get('workloadLimit',
                config.get('defaultDeckWorkloadLimit', 200))
        deckWorkloadMax = conf['new'].get('workloadMax',
                config.get('defaultDeckWorkloadMax', 250))
        deckOverdueMax = conf['new'].get('overdueMax',
                conf.get('defaultDeckOverdueMax', 50))
        deckMinimumNew = conf['new'].get('minimumNew',
                conf.get('defaultDeckMinimumNew', 1))
        # Check workload
        dids = [deck_id]
        for name, id in mw.col.decks.children(deck_id):
            dids.append(id)
        cardsStudied = mw.col.db.scalar(
            f"""
select count() from revlog join cards on cards.id = revlog.cid
where revlog.id > ? and cards.did in """ + ids2str(dids),
            (mw.col.sched.dayCutoff - 86400) * 1000
        )
        workload = cardsStudied or 0
        if node:
            workload += node.learn_count + node.new_count + node.review_count
        if workload > deckWorkloadMax:
            maxNew = deckMinimumNew
        elif workload > deckWorkloadLimit:
            excess = workload - deckWorkloadLimit
            range = deckWorkloadMax - deckWorkloadLimit
            if range > 0:
                ratio = excess / range
                maxNew = max(deckMinimumNew, min(maxNew, int(round(newPerDay * (1 - ratio)))))
            else:
                maxNew = deckMinimumNew
        # Check overdue only when the day rolls over
        # During a day, number of overdue cards can only go down, never up
        if lastDay != mw.col.sched.today:
            overdue = mw.col.db.scalar(
                f"""
select count() from cards
where queue = {QUEUE_TYPE_REV} and due < ? and did in """ + ids2str(dids),
                mw.col.sched.today
            )
            overdue = overdue or 0
            print("deck overdue ", deck_id, overdue)
            if overdue > deckOverdueMax:
                maxNew = deckMinimumNew
            elif deckOverdueMax > 0:
                ratio = overdue / deckOverdueMax
                maxNew = max(deckMinimumNew, min(maxNew, int(round(newPerDay * (1 - ratio)))))

    print('maxNew ', maxNew, node)
    if node and node.new_count > maxNew:
        delta = node.new_count - maxNew
        print("reducing new from ", node.new_count, " to ", maxNew)
        mw.col.sched.update_stats(deck_id, new_delta=delta)


def onCollectionDidLoad(col):
    global totalCount
    global totalOverdue
    global lastDay
    enablePerDeckLimits = config.get('enablePerDeckLimits', True)
    enableTotalLimits = config.get('enableTotalLimits', True)

    # the due tree gives us cards due today
    tree = col.sched.deck_due_tree()

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
        totalCount += cardsStudied
        overdue = mw.col.db.scalar(
            f"""
select count() from cards
where queue = {QUEUE_TYPE_REV} and due < ?""",
            mw.col.sched.today
        )
        overdue = overdue or 0
        print("total overdue ", overdue)
        totalOverdue = overdue


    # For each deck, we need the total of cards scheduled + cards studied
    # This is the workload for the deck. We also need total scheduled + 
    # total studied. The totals are the sums of the per-deck totals, for top
    # level decks only.
    for x in col.decks.all_names_and_ids():
        limitDeck(x.id, tree)

    lastDay = mw.col.sched.today
    print("initialization complete")


if config.get('enablePerDeckLimits', False):
    initializeOptions()

gui_hooks.reviewer_did_answer_card.append(reviewerDidAnswerCard)
gui_hooks.collection_did_load.append(onCollectionDidLoad)
