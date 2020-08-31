# anki-limitnew
Limit the number of new cards in Anki.

This addon works only with Anki 2.1 and the V2 scheduler.

There are two implementations: one that works on Anki 2.1.22 and later and
an earlier, simpler implementation that works on releases at least as old
as 2.1.17.

It limits the number of new cards, based on the number of new and review
cards scheduled and the number of cards studied.

Too many new cards causes overload. The number of cards to be studied each
day increases until it is impossible to study all cards on time. This
defeats the spaced repition schedule and learning becomes less effective.

This addon limits the number of new cards when the number of cards due plus
card reviews exceeds the configured limit. Limits may be based on total
numbers for all decks or per deck.

There are two parameters: WorkloadLimit and WorkloadMax. The workload is
the sum of cards due for review plus the number of cards reviewed on the
day. If this total exceeds WorkloadLimit then the number of new cards is
reduced, down to 0 new cards if the total exceeds WorkloadMax. Setting
WorkloadLimit and WorkloadMax to the same value will result in
all-or-nothing behaviour: either all of New cards/day or none. Setting
WorkloadMax greater than WorkloadLimit will cause the number of new cards
to be gradually reduced as the workload increases from WorkloadLimit to
WorkloadMax.

A sub-deck cannot have more new cards than its parent deck(s).
This limitation is imposed by the Anki v2 scheduler. This is true even if
one studies only the sub-deck. 

## Installation

* Download limitnew.ankaddon
* Start Anki and open Tools -> Add-ons
* Drag the downloaded .ankiaddon file onto the add-ons list
* Restart Anki

GitHub: https://github.com/ig3/anki-limitnew

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
the limitnew addong and click Configure. Set values for the two parameters,
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
maximum of the two limits.

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

