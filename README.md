# anki-limitnew
Limit the number of new cards in Anki based on workload.

If you have too many cards due, you cannot study them all on schedule. This
defeats the spaced repitition schedule. Adding more new cards only makes
the problem worse. You can manually edit your new card limit but this
add-on adjusts it automatically to keep a steady workload, adding as many
new cards as you can handle without being overloaded.

This add-on works only with Anki 2.1 and the V2 scheduler.

There are three implementations:
1. The original implementation for Anki 2.1.22
2. An implementation for Anki 2.1.22 through 2.1.27
3. The latest implementation for Anki 2.1.28

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

With this add-on you can limit the number of new cards you see based on
number of overdue cards, number of cards scheduled and number of cards
viewed and you can set limits for the totals of these across all decks
and for each deck individually. 

The limits work regardless of study order (new cards first, last or mixed
with reviews).

If you are coping well you will not have any overdue cards and the sum of
cards viewed and scheduled will be below the limits you set. In this case
you will see the full number of new cards you have configured as
`New cards/day` in you options for New Cards.

If you have overdue cards or the sum of scheduled and viewed cards exceeds
the limit you configure for this add-on, then the number of new cards you
see will be reduced. The reduction is gradual, reacing zero at the maximums
you set. Limits and maximums can be set for each deck and for totals across
all decks.

The objective is to studay as many new cards as possible without becoming
overloaded so that you can complete all scheduled reviews each day. If you
do become overloaded, then hold off new cards completely, until you catch
up with scheduled reviews.

New cards a limited based on number of overdue cards and `workload`: the
sum of cards scheduled and cards viewed for the day. This is an
approximation of the time and effort you are putting in to studying.

**Workload**: the number of cards due to be reviewed plus the number of
card views on the day.

If you view the same card several times (e.g. as it progresses through your
learning steps) then each view of the card contributes to workload. The
workload is not the number of unique cards, but the total number of card
views, regardless of which card. At the start of the day no cards have been
viewed, but some number of cards are due. By the end of the day, if you
complete review of all cards due, the remaining cards due is 0 but you will
have viewed some number of cards. The sum of due and viewed cards the the
approximation of workload. It tends to increase as you will view hard cards
more than once.

**Overdue**: the number of cards overdue for review is simpler. If you
complete all scheduled reviews each day, this number will be 0 but if you
don't complete all scheduled reviews then you will accumulate overdue
cards.

**OverdueMax**: the upper limit on overdue cards, beyond which no new
cards per day will be reduced to 0.

For the limit based on overdue cards there is one parameter: `OverdueMax`.
The new cards limit is reduced if there are any overdue cards. It is
reduced gradually, down to 0 when the number of overdue cards exceeds
`OverdueMax`. For example, if New cards/day is 20 and OverdueMax is 10,
then if you have 0 overdue cards you may see 20 new cards but if you have 5
overdue cards you may only see 10 new cards and if you have 10 or more
overdue cards you will not see any new cards.

For the limit based on workload there are two parameters: WorkloadLimit and
WorkloadMax. The new cards limit is reduced if the workload exceeds
WorkloadLimit. It is reduced gradually, down to 0 when the workload exceeds
WorkloadMax. Depending on your preference, WorkloadLimit and WorkloadMax
can be set equal for an abrupt cutoff of new cards, or WorkloadMax can be
set greater than WorkloadLimit for a gradual reduction.

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
   * totalOverdueMax
   * totalMinimumNew
   * defaultDeckWorkloadLimit
   * defaultDeckWorkloadMax
   * defaultDeckOverdueMax
   * defaultDeckMinimumNew

To change the configuration, start Anki and open Tools -> Add-ons, select
the limitnew add-on and click Configure. Set values for the two parameters,
then click OK.

### enableDeckLimits - default true

This parameter may be set to true or false.

If it is true, then new cards are limited per deck.
Three new parameters are added to the New tab of deck options:

   * Workload Limit
   * Workload Max
   * Overdue Max

These parameters are configured per option group. Each deck has an option
group configured. By creating multiple option groups, each deck can be
configured differently.

These parameters work as described above but the workload and overdue cards
are calculated separately for each deck. If decks are nested, then the
calculations include cards overdue, due and studied for a deck and its
sub-decks.


### enableTotalLimits - default true

This parameter may be set to true or false.

If it is true then new cards are limited based on total workload: the sum
of cards due and studied across all decks, and total number of overdue
cards.

The limits are configured in add-on configuration parameters
totalWorkloadLimit, totalWorkloadMax and totalOverdueMax. These work as
described above.

### mode - default min

This parameter is only used by the older implementations. Implementation
for Anki 2.1.28 and later ignores it.

This parameter may be set to min or max.

If both enableDeckLimits and enableTotalLimits are true, then this
parameter determines whether the number of new cards for a given deck is
the maximum of the two limits or the minimum of them.

This parameter only works for the older implementations. For the current
implementation (Anki 2.1.28 and later) the number of new cards is always
the minimum.

### totalWorkloadLimit - default 200

This parameter may be set to an integer.

If enableTotalLimits is true, this is the total workload beyond which the
new card limit will be reduced. The total workload is calculated by summing
the cards studied and reviews and learning cards scheduled across all
decks.

Recommendation: Set workloadLimit to the number of cards you can study
in a couple of hours, or however much time you have available to study each
day. If you need only a few seconds per card, you might set your limit to
2,000 or higher. If you spend more like 30 seconds per card, then you might
set your limit to about 200.


### totalWorkloadMax - default 250

This parameter may be set to an integer.

If enableTotalLimits is true, this is the workload beyond which the new
card limit will be reduced to totalMinimumNew. The total workload is
calculated by summing the cards studied and reviews and learning cards
scheduled across all decks.

If workloadMax is greater than workloadLimit then the new
card limit will be gradually reduced as workload increases from
workloadLimit to workloadMax.

Recommendation: Set totalWorkloadMax to the workload beyond which you don't
want to see any new cards. If you want your new cards to be all-or-nothing,
set totalWorkloadMax to the same value as totalWorkloadLimit.

### totalOverdueMax - default 20

This parameter may be set to an integer.

If enableTotalLimits is true, this is the number of overdue cards beyond
which the new card limit will be reduced to totalMinimumNew.

Recommendation: Set totalOverdueMax low. You will only have overdue cards
if you fail to study all scheduled reviews. This is a strong indicator that
you are overloaded, in which case adding more new cards will not be
helpful.

### totalMinimumNew - default 1

This parameter may be set to an integer.

If enableTotalLimits is true, this is the minimum that new cards will be
reduced to based on total workload and overdue cards.

Recommendation: Set this to the number of new cards you want to see every
day, regardless of your overall workload. It should be low enough that even
when you are seriously overloaded, you will be able to recover reasonably
quickly.

### defaultDeckWorkloadLimit - default 200

This parameter may be set to an integer.

If enableDeckLimits is true, this is the default value of the option group
Workload Limit parameter.

### defaultDeckWorkloadMax - default 250

This parameter may be set to an integer.

If enableDeckLimits is true, this is the default value of the option group
Workload Max parameter.

### defaultDeckOverdueMax - default 20

This parameter may be set to an intenger.

If enableDeckLimits is true, this is the default value of the option group
Overdue Max parameter.

### defaultDeckMinimumNew - default 1

This parameter may be set to an integer.

If enableDeckLimits is true, this is the default value of the option group
Minimum New parameter.

## Per-Deck Limits

If `enableDeckLimits` is set to true, then deck options will include three
new parameters: `Workload Limit`, `Workload Max`, `Overdue Max` and
`Minimum New`. These values will not appear in the add-on configuration
file. They only appear in the deck options. They work the same as the
corresponding `total` parameters in the add-on configuration, except the
workload and overdue cards are for the partucular deck. However, if you
have nested decks, then the number for the parent deck include those of the
sub-decks.

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
With the older implementations, your count of new cards is 20, your limit
is 20 and Anki will not show you any more new cards. If you continue to
study so that your total number of reviews exceeds your WorkloadMax, then
this add-on will reduce your new card limit to 0. Now, your new card limit
is 0, but your count of new cards is still 20. If you then add 10 more new
cards by custom study, your new card limit is still 0 and your count of new
cards is reduced to 10, but 10 is still more than 0 so you will not see any
more new cards. If you then allow another 15 new cards, your count of new
cards studied is reduced to -5 (these adjustments are cumulative). Since -5
is less than 0, you will see 5 more new cards. 

The latest implementation is different. It changes the number of new cards
you will see by changing the number of new cards seen, rather than the
limit on new cards. Thus, it works consistently with how custom study
works: to make Anki believe you have studied more or less new cards than
you actually have. Being consistent with how custom study works, it will,
hopefully, be a little less confusing if you do custom study.

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

### 14 May 2021

A new implementation that works with Anki 2.1.28 and later.

Added limit on overdue cards as an alternative basis for limiting new
cards. Having overdue cards is a strong indication that you are overloaded.
While your number of scheduled and viewed cards are likely to be high in
such a case, you might want to limit new cards purely on the basis of
overdue cards, regardless of workload.

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

