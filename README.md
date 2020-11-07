# anki-limitnew
Limit the number of new cards in Anki when you have too many cards due.

If you have too many cards due, you cannot study them all on schedule. This
defeats the spaced repitition schedule. Adding more new cards only makes
the problem worse. You can manually edit your new card limit but this
add-on adjusts it automatically to keep a steady workload, adding as many
new cards as you can handle without being overloaded.

This add-on works only with Anki 2.1 and the V2 scheduler.

There are two implementations: one that works on Anki 2.1.22 and later and
an earlier, simpler implementation that works on releases at least as old
as 2.1.17.

## Installation

* Download limitnew.ankiaddon
* Start Anki and open Tools -> Add-ons
* Drag the downloaded .ankiaddon file onto the add-ons list
* Restart Anki

GitHub: https://github.com/ig3/anki-limitnew

## Concepts

Ideally, you will complete study of all due cards every day. If you do, you
will see your review cards according to the spaced repition algorithm. If
you don't, your reviews of some cards will be delayed and learning will not
be as effective. If you are unable to study for a few days, you may have
more reviews due than you can complete in a day and adding more new cards
will only make the problem worse. You need some time without any more new
cards to catch up, then you can study new cards again. Otherwise, you may
be perpetually overloaded and not learning effectively, going into a
downward spiral of failure.

Each deck has a limit on new cards per day. This is a fixed number and if
you complete your study each day, you will see this number of new cards
each day. That's great, as long as you don't get overloaded and fall
behind. You make steady progress.

Reality is, some cards are easier than others and some days are better than
others. On a good day with easy cards, you could study many new cards and
still complete all due reviews. On a bad day or with more difficult cards,
adding too many new cards will make you fall behind and if you have limited
time to study, you may not be able to complete all due reviews. If you fall
behind for other reasons (i.e. you are unable to study for a few days)
adding new cards before you are caught up just makes it harder to catch up.

But Anki shows the same number of new cards every day, regardless of your
workload and how well you are coping.

One simple solution is to set your new card limit to 0 then add new cards
by custom study. This way you can add as many new cards as you want,
whenever you have capacity but not add any when you are overloaded.
Effectively, you manage the number of new cards manually.

Another is to edit your deck options to reduce your new card limit when you
are overloaded and increase it when you are not. Again, you are managing
the number of new cards manually.

Yet another is to set Anki scheduling options to show new cards after
reviews. If you don't complete your reviews, you will not see any new
cards. This is *automatic* but you will see all your new cards together, at
the end of your study and each deck is handled separately. If you have
multiple decks, you may spend time studying new cards in one deck, then not
have time to finish all the cards due when studying a subsequent deck.

With this add-on you can limit the number of new cards you see across all
decks and regardless of study order (new cards first, last or mixed with
reviews). The limit is adjusted according to your workload. If you are
coping well and your workload is light, more new cards will be shown. If
your workload increases, fewer new cards will be shown. If your workload is
too much, no new cards will be shown.

The objective is to show as many new cards as possible, maintain a steady
overall workload and avoid overload so that you can complete all scheduled
reviews most days.

New cards are limited based on workload, which is an approximation of the
time and effort you are putting into studying on a given day. If workload
is low, then new cards are available, up to your configured new card limit.
If workload is high, the number of new cards is limited, so you don't get
overloaded with new cards until you learn the cards already studied well
enough to reduce your workload. If workload is too high, you will not see
any new cards until you catch up and your workload is reduced.

**Workload**: the number of cards due to be reviewed plus the number of
card views on the day.

Each time you view a card, the calculation of workload is increased. If you
view the same card several times (e.g. as it progresses through your
learning steps) then each view of the card contributes to workload. The
workload is not the number of unique cards, but the total number of card
views, regardless of which card. At the start of the day no cards have been
viewed, but some number of cards are due. By the end of the day, if you
complete review of all cards due, the remaining cards due is 0 but you will
have viewed cards some number of time.

There are two parameters: WorkloadLimit and WorkloadMax. The new cards
limit is reduced if the workload exceeds WorkloadLimit. It is reduced
gradually, down to 0 when the workload exceeds WorkloadMax. Depending on
your preference, WorkloadLimit and WorkloadMax can be made equal for an
abrupt cutoff of new cards, or WorkloadMax can be made greater than
WorkloadLimit for a gradual reduction.

**WorkloadLimit**: the lower limit, beyond which new cards per day begins
to be reduced from its configured value.

**WorkLoadMax**: the upper limit, beyond which the new cards per day is
reduced to 0.

## Configuration

The add-on has the following configuration parameters:

   * enableDeckLimits
   * enableTotalLimits
   * mode
   * totalWorkloadLimit
   * totalWorkloadMax
   * defaultDeckWorkloadLimit
   * defaultDeckWorkloadMax

To change the configuration, start Anki and open Tools -> Add-ons, select
the limitnew add-on and click Configure. Set values for the two parameters,
then click OK.

### enableDeckLimits - default true

This parameter may be set to true or false.

If it is true, then new cards are limited per deck.
Two new parameters are added to the New tab of deck options:

   * Workload Limit
   * Workload Max

These parameters are configured per option group. Each deck has an option
group configured. By creating multiple option groups, each deck can be
configured differently.

These parameters work as described above but the workload is calculated
separately for each deck. If decks are nested, then the calculation of
workload for a deck includes cards due and studied in the deck itself and
in its sub-decks.


### enableTotalLimits - default true

This parameter may be set to true or false.

If it is true then new cards are limited based on total workload: the sum
of cards due and studied across all decks.

The limits are configured in add-on configuration parameters
totalWorkloadLimit and totalWorkloadMax. These work as described above.

### mode - default min

This parameter may be set to min or max.

If both enableDeckLimits and enableTotalLimits are true, then this
parameter determines whether the number of new cards for a given deck is
the maximum of the two limits or the minimum of them.

### totalWorkloadLimit - default 200

This parameter may be set to an integer.

The workloadLimit is the workload beyond which the new card limit will
be reduced. The total workload is calculated by summing the cards studied
and reviews and learning cards scheduled across all decks.

Recommendation: Set workloadLimit to the number of cards you can study
in a couple of hours, or however much time you have available to study each
day. If you need only a few seconds per card, you might set your limit to
2,000 or higher. If you spend more like 30 seconds per card, then you might
set your limit to about 200.


### totalWorkloadMax - default 250

This parameter may be set to an integer.

The workloadMax is the workload beyond which the new card limit will be
reduced to 0. The total workload is calculated by summing the cards studied
and reviews and learning cards scheduled across all decks.

If workloadMax is greater than workloadLimit then the new
card limit will be gradually reduced as workload increases from
workloadLimit to workloadMax.

Recommendation: Set workloadMax to the workload beyond which you don't want
to see any new cards. If you want your new cards to be all-or-nothing, set
workloadMax to the same value as WorkloadLimit.

### defaultDeckWorkloadLimit - default 200

This parameter may be set to an integer.

If enableDeckLimits is set to true, then this parameter sets the default
value of the option group Workload Limit parameter.

### defaultDeckWorkloadMax - default 250

This parameter may be set to an integer.

If enableDeckLimits is set to true, then this parameter sets the default
value of the option group Workload Max parameter.

## Per-Deck Limits

If `enableDeckLimits` is set to true, then deck options will include two
new parameters: `Workload Limit` and `Workload Max`. These values will not
appear in the add-on configuration file. They only appear in the deck
options. They work the same as the add-on WorkloadLimit and WorkloadMax
parameters, except the workload is that of the specific deck and its
sub-decks, if there are any. Workload in another deck will not affect
limits based on these per-deck parameters.

## Custom Study - increase today's new card limit

[Custom study](https://docs.ankiweb.net/#/filtered-decks?id=custom-study)
allows you to increase the number of new cards for the day. This alters
the deck, rather than creating a filtered deck. The implementation doesn't
actually change the new card limit. Instead, it adjusts the count of new
cards studied. If you allow 10 more new cards, the new card limit is
unchanged but the count of new cards studied is reduced by 10, possibly to
a negative number. Then, as you study more new cards, the count of new
cards studied is increased. You can study more new cards until the count
reaches the new card limit.

When your workload is less than your WorkloadLimit, this should work as
expected but when the add-on has reduced your new card limit, the result
can be a bit confusing.

Consider if your new card limit is 20 cards and you study 20 new cards.
Then your count of new cards is 20, your limit is 20 and Anki will not show
you any more new cards. If you continue to study so that your total number
of reviews exceeds your WorkloadMax, then this add-on will reduce your new
card limit to 0. Now, your new card limit is 0, but your count of new cards
is still 20. If you then add 10 more new cards by custom study, your new
card limit is still 0 and your count of new cards is reduced to 10, but 10
is still more than 0 so you will not see any more new cards. If you then
allow another 15 new cards, your count of new cards studied is reduced to
-5 (these adjustments are cumulative). Since -5 is less than 0, you will
see 5 more new cards. 

## Filtered decks

[Filtered decks](https://docs.ankiweb.net/#/filtered-decks?id=filtered-decks-amp-cramming)
are for study outside the normal spaced repitition algorithm and deck
configuration.

This add-on does not limit new cards in filtered decks. This includes
filtered decks you create manually and those created by custom study.

Filtered decks do have reviews due and studying a filtered deck contributes
to the count of card views - increasing the total workload for the day.
This will not affect per-deck limits (assuming the filtered deck is not a
sub-deck of the deck being studied) but it will affect the limits based on
total workload.

## Sub-decks

The new card limit of a sub-deck cannot be more than the limit of its
parent deck. This limitation is imposed by the Anki v2 scheduler. This is
true even if one studies only the sub-deck. This add-on may reduce the new
card limit of the parent deck and as a result limit the new card limit of
the sub-deck, regardless of the configuration of the sub-deck.

## Anki versions older than 2.1.22

The latest implementation uses hook scheduler_new_limit_for_single_deck,
introduced with Anki 2.1.22. For older versions, the old monkey patch
integration is used. This version of the add-on is much simpler.

### Configuration

The old implementation has only two configuration parameters:

   * workloadLimit (default 200)
   * workloadMax (default 250)

These are applied to workload calculated across all decks. There is no
support for per-deck workload limits.

For example, you can set configuration to:

```
{
  "workloadLimit": 200,
  "workloadMax": 250
}
```

Any other configuration parameters will be ignored.


## Change Log

### 2 Sep 2020

Comment out print statements.

### 31 Aug 2020

A major rewrite to address some performance issues.

For Anki 2.1.22 and later, the scheduler_new_limit_for_single_deck hook is
used for integration.  Neither _groupChildrenMain nor _deckNewLimitSingle
are monkey patched. For older versions of Anki, the old implementation is
still used - monkey patching _groupChildrenMain and _deckNewLimitSingle.

The new implementation supports workload limits per deck, with
configuration in deck options, and total workload limit with configuration
in add-on options.

Database queries to determine workload (cards due and cards studied) are
rewritten to improve performance and results are cached to avoid re-running
them unnecessarily. The cache is cleared when cards are reviewed.

#### hooks

##### scheduler_new_limit_for_single_deck

This pylib hook is used to reduce the limit on new cards per deck, based on
workload.

##### reviewer_did_answer_card

This GUI hook is used to clear the cache of number of cards due and studied
when a card is answered. 

