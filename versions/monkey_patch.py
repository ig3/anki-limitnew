# This is the original implementation of the add-on that integrates
# by monkey patching the Anki scheduler.
#
# This implementation supports only the V2 scheduler. It was initially
# developed for Anki 2.1.17. As of Anki version 2.1.26, a new
# implementation was developed with better performance.
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

origDeckNewLimitSingle = SchedulerV2._groupChildrenMain
SchedulerV2._groupChildrenMain = myGroupChildrenMain



# Wrap _deckNewLimitSingle

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
# This is not the same as the deck new card per day limit.
#
def myDeckNewLimitSingle(self, g):
    if g['dyn']:
        return self.dynReportLimit

    # Get the total number of cards due today
    due = self.col.db.scalar(
        """
select count() from (select 1 from cards where did in %s
and (queue = 1 or ( queue = 2 and due <= ?)))"""
        % ids2str(self.col.decks.allIds()),
        self.today
    )

    # Get total cards studied today
    studied, thetime = self.col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (self.col.sched.dayCutoff-86400)*1000)
    studied = studied or 0
    thetime = thetime or 0

    workload = studied + due

    workloadLimit = config.get('workloadLimit',200)
    workloadMax = config.get('workloadMax',250)
    scale = workloadMax - workloadLimit

    excess = max(0, workload - workloadLimit)

    # Get the configured perDay limit for this deck
    c = self.col.decks.confForDid(g['id'])
    perDay = c['new']['perDay']
    print("perDay = ", perDay)

    # Scale perDay according to workload excess
    if scale > 0:
        perDay = max(0, int(perDay * (1 - excess / scale)))
    elif excess > 0:
        perDay = 0

    # The limit is the lower of the limit calculated here
    # and the limit from the default _deckNewLimitSingle function
    # and the number of new cards already studied today is subtracted
    # to give the current limit on additional new cards today (not
    # the total for the day)
    limit = max(0, perDay - g["newToday"][1])

    return limit
    

origDeckNewLimitSingle = SchedulerV2._deckNewLimitSingle
SchedulerV2._deckNewLimitSingle = myDeckNewLimitSingle
