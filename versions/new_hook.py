# This implementation uses the new hook scheduler_new_limit_for_single_deck
# introduced with Anki 2.1.22. For older versions, use the monkey patch
# implementation.
#
# This was developed agains Anki 2.1.26 and may not work for versions
# 2.1.22 through 2.1.25 - I haven't tested it.
#
# This implementation uses a monkey patch for _groupChildrenMain. There
# is no hook for this method and it is not used as of Anki 2.1.28, so
# this implementation will not have a very long lifetime. An implementation
# for the new tree has not yet been developed.
#
# This version supports per-deck configuration and workload calculations
# and has a more efficient implementation of workload.
#
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
from anki import hooks
from aqt import gui_hooks
from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf


import time
import traceback

cache = {}

config = mw.addonManager.getConfig(__name__)

def updateConfig(newConfig):
    print("updateConfig")
    global config
    config = newConfig

mw.addonManager.setConfigUpdatedAction(__name__,updateConfig)


# This is no longer used
# groupChildren was removed by commit 769bf04f753f6d415501d9230a200955fb5881a5
# Comment indicates it was already unused by this commit
#
## # Monkey patch _groupChildrenMain to use _deckNewLimitSingle to get
## # the new card limit for a deck, rather than reading the deck config
## # directly. This is necessary because this add-on modifies
## # _deckNewLimitSingle to reduce the limit according to workload
## def myGroupChildrenMain(self, grps):
##     print("myGroupChildrenMain ", self)
##     #print(traceback.format_stack())
##     start = time.perf_counter()
##     print(grps)
##     tree = []
##     # group and recurse
##     def key(grp):
##         return grp[0][0]
##     for (head, tail) in itertools.groupby(grps, key=key):
##         tail = list(tail)
##         did = None
##         rev = 0
##         new = 0
##         lrn = 0
##         children = []
##         for c in tail:
##             if len(c[0]) == 1:
##                 # current node
##                 did = c[1]
##                 rev += c[2]
##                 lrn += c[3]
##                 new += c[4]
##             else:
##                 # set new string to tail
##                 c[0] = c[0][1:]
##                 children.append(c)
##         children = self._groupChildrenMain(children)
##         # tally up children counts
##         for ch in children:
##             lrn += ch[3]
##             new += ch[4]
##         # limit the counts to the deck's limits
##         conf = self.col.decks.confForDid(did)
##         deck = self.col.decks.get(did)
##         if not conf['dyn']:
## #                new = max(0, min(new, conf['new']['perDay']-deck['newToday'][1]))
##             new = max(0, min(new, self._deckNewLimitSingle(deck)))
## # deck new card limit rather than calling self._deckNewLimitSingle,
##         tree.append((head, did, rev, lrn, new, children))
##     print("myGroupChildrenMain elapsed ", (time.perf_counter() - start))
##     return tuple(tree)
## 
## # _groupChildrenMain uses _deckNewLimitSingle since Dec 2019
## # https://github.com/ankitects/anki/pull/363
## # so no need to monkey patch it in 2.1.22 (18 Mar 2020).
## # origGroupChildrenMain = SchedulerV2._groupChildrenMain
## # SchedulerV2._groupChildrenMain = myGroupChildrenMain

# return total workload (all decks)
def totalWorkload(sched):
    # print("totalWorkload ")
    # start = time.perf_counter()

    if not 'total' in cache:
        decks = ids2str(sched.col.decks.allIds())
        cache['total'] = decksWorkload(sched, decks)
    # print("totalWorkload elapsed ", (time.perf_counter() - start))
    return cache['total']


# return workload for a specific deck, including sub-decks
def deckWorkload(sched, deck):
    # print("deckWorkload for ", deck['name'])
    # start = time.perf_counter()

    if not deck['id'] in cache:
        decks = ids2str(
            [ deck['id'] ] +
            [ did for (name, did) in sched.col.decks.children(deck['id']) ]
        )
        cache[deck['id']] = decksWorkload(sched, decks)

    # print("deckWorkload elapsed ", (time.perf_counter() - start))
    return cache[deck['id']]

# return workload for the given set of decks
# This function is slow - it does two database queries
def decksWorkload(sched, decks):
    # print("decksWorkload for ", decks)
    # start = time.perf_counter()

    # due is the total number of cards due to be studied today
    # across all decks in the array decks
    due = sched.col.db.scalar(
        """
select count() from cards where did in %s
and (queue = 1 or ( queue = 2 and due <= ?))"""
        % decks,
        sched.today
    )

    # Get total cards studied today

    # studied is the total number of cards studied today
    # across all the decks in array decks. This query requires
    # a sub-query because revlog does not record the deck ID
    # so it is necessary to get all card IDs for the given
    # decks then filter revlog based on the possibly very long
    # list. Maybe a join would be more efficient than a sub-query???
    start = time.perf_counter()
    studied = sched.col.db.scalar("""
select count()
from
    revlog
    join cards on cards.id = revlog.cid and
    cards.did in %s
where
  revlog.id > ?
    """ % decks,
    (sched.col.sched.dayCutoff-86400)*1000)

    studied = studied or 0

    workload = studied + due

    # print("decksWorkload elapsed ", (time.perf_counter() - start))
    return workload


# Returns the new card limit for deck g
def newCardLimit(self, g, workload, workloadLimit, workloadMax):
    # print("newCardLimit for ", g['name'], workload, workloadLimit, workloadMax)
    # start = time.perf_counter()

    scale = workloadMax - workloadLimit

    excess = max(0, workload - workloadLimit)

    # Get the configured perDay limit for this deck
    c = self.col.decks.confForDid(g['id'])
    perDay = c['new']['perDay']

    # Scale perDay according to workload excess
    if scale > 0:
        perDay = max(0, int(perDay * (1 - excess / scale)))
    elif excess > 0:
        perDay = 0

    # Finally, subtract from perDay the number of new cards already
    # studied today, to get the current limit on additional new cards
    limit = max(0, perDay - g["newToday"][1])

    # print("newCardLimit elapsed ", (time.perf_counter() - start))
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
    # print("myDeckNewLimitSingle ", g['name'])
    # start = time.perf_counter()
    if g['dyn']:
        return self.dynReportLimit

    # Get the configuration for the deck
    c = self.col.decks.confForDid(g['id'])

    limit = max(0, c['new']['perDay'] - g['newToday'][1])

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
        deckLimit = newCardLimit(self, g, 
            deckWorkload(self, g),
            deckWorkloadLimit, deckWorkloadMax)

    if enableTotalLimits:
        totalWorkloadLimit = config.get('totalWorkloadLimit', 200)
        totalWorkloadMax = config.get('totalWorkloadMax', 250)

        totalLimit = newCardLimit(self, g, 
            totalWorkload(self),
            totalWorkloadLimit, totalWorkloadMax)

    if enablePerDeckLimits and enableTotalLimits:
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

    # print("myDeckNewLimitSingle elapsed ", (time.perf_counter() - start))
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
    print("load_conf")
    f = self.form
    c = self.conf["new"]
    f.workloadLimit.setValue(c.get('workloadLimit', 200))
    f.workloadMax.setValue(c.get('workloadMax', 250))


def save_conf(self):
    print("save_conf")
    f = self.form
    c = self.conf["new"]
    c['workloadLimit'] = f.workloadLimit.value()
    c['workloadMax'] = f.workloadMax.value()

def initializeOptions():
    dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setupUI)
    DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
    DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')


# This is registered as hook for scheduler_new_limit_for_single_deck
# It reduces the limit on new cards for the deck based on workload
# It returns the lower of the default limit and the limit calculated
# by the plugin.
def schedulerNewLimitForSingleDeck(limit, deck):
    # print("schedulerNewLimitForSingleDeck - hook function - ", limit,
    #     deck['name'])
    # start = time.perf_counter()
    newLimit = myDeckNewLimitSingle(mw.col.sched, deck)
    if newLimit < limit:
        # print("reduce limit from ", limit, " to ", newLimit)
        limit = newLimit
    # print("schedulerNewLimitForSingleDeck elapsed ", (time.perf_counter() - start))
    return limit


def reviewerDidAnswerCard(reviewer, card, ease):
    print("reviewerDidAnswerCard")
    print("card ", card)
    # Force re-calculation of workloads
    if 'total' in cache:
        del cache['total']
    deck = mw.col.decks.get(card.did)
    print("deck ", deck)
    for g in [deck] + mw.col.decks.parents(card.did):
        print("clear workload for deck ", g['name'])
        if g['id'] in cache:
            del cache[g['id']]
    print("cache ", cache)

if config.get('enablePerDeckLimits', False):
    initializeOptions()

hooks.scheduler_new_limit_for_single_deck.append(schedulerNewLimitForSingleDeck)
gui_hooks.reviewer_did_answer_card.append(reviewerDidAnswerCard)

