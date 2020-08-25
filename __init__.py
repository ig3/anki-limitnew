# This Anki add-on limits the number of new cards, depending on the
# days "workload", which is the number of cards studied plus the
# nubers or new and review cards scheduled for the day.
#
# It only works with the V2 scheduler.
#
import itertools
from aqt import mw
from anki.schedv2 import Scheduler as SchedulerV2
from anki.utils import ids2str

# For new deck options
from anki.hooks import wrap
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf

config = mw.addonManager.getConfig(__name__)

def updateConfig(newConfig):
    global config
    config = newConfig

mw.addonManager.setConfigUpdatedAction(__name__,updateConfig)


# Monkey patch _groupChildrenMain to use _deckNewLimitSingle to get
# the new card limit for a deck, rather than reading the deck config
# directly. This is necessary because this add-on modifies
# _deckNewLimitSingle to reduce the limit according to workload
def myGroupChildrenMain(self, grps):
    tree = []
    # group and recurse
    def key(grp):
        return grp[0][0]
    for (head, tail) in itertools.groupby(grps, key=key):
        tail = list(tail)
        did = None
        rev = 0
        new = 0
        lrn = 0
        children = []
        for c in tail:
            if len(c[0]) == 1:
                # current node
                did = c[1]
                rev += c[2]
                lrn += c[3]
                new += c[4]
            else:
                # set new string to tail
                c[0] = c[0][1:]
                children.append(c)
        children = self._groupChildrenMain(children)
        # tally up children counts
        for ch in children:
            lrn += ch[3]
            new += ch[4]
        # limit the counts to the deck's limits
        conf = self.col.decks.confForDid(did)
        deck = self.col.decks.get(did)
        if not conf['dyn']:
#                new = max(0, min(new, conf['new']['perDay']-deck['newToday'][1]))
            new = max(0, min(new, self._deckNewLimitSingle(deck)))
# deck new card limit rather than calling self._deckNewLimitSingle,
        tree.append((head, did, rev, lrn, new, children))
    return tuple(tree)

origGroupChildrenMain = SchedulerV2._groupChildrenMain
SchedulerV2._groupChildrenMain = myGroupChildrenMain


# Returns the new card limit for deck g
# based on workload for all decks in deckIds
def newCardLimit(self, g, decks, workloadLimit, workloadMax):
    # print("newCardLimit for ", g['name'], decks, workloadLimit, workloadMax)

    due = self.col.db.scalar(
        """
select count() from (select 1 from cards where did in %s
and (queue = 1 or ( queue = 2 and due <= ?)))"""
        % ids2str(decks),
        self.today
    )
    # print("due ", due);

    # Get total cards studied today
    studied, time = self.col.db.first("""
select count(), sum(time)/1000 from revlog
where
  id > ? and
  cid in (select id from cards where did in %s)""" % ids2str(decks),
    (self.col.sched.dayCutoff-86400)*1000)

    studied = studied or 0
    time = time or 0

    # print("studied ", studied)

    workload = studied + due
    # print("workload ", workload)

    scale = workloadMax - workloadLimit
    # print("scale ", scale)

    excess = max(0, workload - workloadLimit)
    # print("excess ", excess)

    # Get the configured perDay limit for this deck
    c = self.col.decks.confForDid(g['id'])
    perDay = c['new']['perDay']
    # print("perDay = ", perDay)

    # Scale perDay according to workload excess
    if scale > 0:
        perDay = max(0, int(perDay * (1 - excess / scale)))
    elif excess > 0:
        perDay = 0

    # Finally, subtract from perDay the number of new cards already
    # studied today, to get the current limit on additional new cards
    limit = max(0, perDay - g["newToday"][1])

    return limit


# In a deck (e.g. g)
#  newToday is a list: [ days_since_deck_creation, new_cards_today ]
#  revToday is a list: [ days_since_deck_creation, rev_cards_today ]
#  lrnToday is a list: [ days_since_deck_creation, lrn_cards_today ]
#  timeToday is a list: [ days_since_deck_creation, ms_on_cards_today ]

# This is a bit funky when there are subdecks because anki
# limits new cards to the lower limit of the deck or the parent deck
# So, if the parent deck has a limit of 0, then so does the subdeck.
# Then, in the decks display, the counts of a deck are the sum of the
# counts of the deck itself and its subdecks. So, with a low but not
# 0 limit, a deck can end up with more new cards than its new limit.
# But, when one goes to study a parent deck, then the decks new limit
# is applied, so the number of New cards might be less than that in
# the deck list, which is inconsistent and confusing.
#
# What we really want is for the new limit to be determined by the
# deck being studied/considered, but new cards selected from this
# deck and/or its children. But this would require a more significant
# revision of the scheduler.

# This returns the limit on new cards for the current deck,
# considering the new cards that have been viewed today.
#
# This is not the same as the deck new card per day limit.
# The new card per day limit is a fixed number. This limit
# decreases as the number of cards studied increases.
#
def myDeckNewLimitSingle(self, g):
    if g['dyn']:
        return self.dynReportLimit

    # print("g ", g)
    # print("self ", self)

    # Get the configuration for the deck
    c = self.col.decks.confForDid(g['id'])

    limit = max(0, c['new']['perDay'] - g['newToday'][1])
    # print("limit ", limit)

    enablePerDeckLimits = config.get('enablePerDeckLimits', True)
    enableTotalLimits = config.get('enableTotalLimits', True)

    if enablePerDeckLimits:
        # Get the set of decks to be considered: current deck plus any children
        decks = [ g['id'] ] + [
            did for (name, did) in self.col.decks.children(g['id'])
        ]
        deckWorkloadLimit = c['new'].get('workloadLimit',
                config.get('defaultDeckWorkloadLimit', 200))
        deckWorkloadMax = c['new'].get('workloadMax',
                config.get('defaultDeckWorkloadMax', 250))
        deckLimit = newCardLimit(self, g, decks,
            deckWorkloadLimit, deckWorkloadMax)

    if enableTotalLimits:
        totalWorkloadLimit = config.get('totalWorkloadLimit', 200)
        totalWorkloadMax = config.get('totalWorkloadMax', 250)

        totalLimit = newCardLimit(self, g, self.col.decks.allIds(),
            totalWorkloadLimit, totalWorkloadMax)

    if enablePerDeckLimits and enableTotalLimits:
        # print("deckLimit ", deckLimit)
        # print("totalLimit ", totalLimit)
        if config.get('mode', 'min') == 'min':
            limit = min(deckLimit, totalLimit)
        else:
            limit = max(deckLimit, totalLimit)
    elif enablePerDeckLimits:
        limit = deckLimit
    elif enableTotalLimits:
        limit = totalLimit
    else:
        limit = max(0, c['new']['perDay'] - g['newToday'][1])

    # Ensure limit isn't negative
    limit = max(0, limit)
    # print("limit ", limit)

    return limit

    
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
    f = self.form
    c = self.conf["new"]
    f.workloadLimit.setValue(c.get('workloadLimit', 200))
    f.workloadMax.setValue(c.get('workloadMax', 250))


def save_conf(self):
    f = self.form
    c = self.conf["new"]
    c['workloadLimit'] = f.workloadLimit.value()
    c['workloadMax'] = f.workloadMax.value()

def initializeOptions():
    dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setupUI)
    DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
    DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')


if config.get('enablePerDeckLimits', False):
    initializeOptions()

origDeckNewLimitSingle = SchedulerV2._deckNewLimitSingle
SchedulerV2._deckNewLimitSingle = myDeckNewLimitSingle
