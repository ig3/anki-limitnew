# anki-limitnew
Limit the number of new cards in Anki.

This addon works only with Anki 2.1 and the V2 scheduler.

It limits the number of new cards, based on the number of new and review
cards scheduled and the number of cards studied.

Too many new cards causes overload. The number of cards to be studied each
day increases until it is impossible to study all cards on time. This
defeats the spaced repition schedule and learning becomes less effective.

This addon limits the number of new cards when the number of cards due plus
card reviews exceeds the configured limit.

## Installation

* Download limitnew.ankaddon
* Start Anki and open Tools -> Add-ons
* Drag the downloaded .ankiaddon file onto the add-ons list
* Restart Anki

GitHub: https://github.com/ig3/anki-limitnew

## Configuration

There are two configuration parameters: workloadLimit and workloadMax.

To change the configuration, start Anki and open Tools -> Add-ons, select
the limitnew addong and click Configure. Set values for the two parameters,
then click OK.

### workloadLimit - default 200

The workloadLimit is the workload beyond which the new card limit will
be reduced.

Workload is the sum of total cards studied on the day across all decks,
plus the numbers of review and learning cards remaining for the current deck.

Recommendation: Set workloadLimit to the number of cards you can study
in a couple of hours, or however much time you have available to study each
day. If you need only a few seconds per card, you might set your limit to
2,000 or higher. If you spend more like 30 seconds per card, then you might
set your limit to about 200.

### workloadMax - default 250

The workloadMax is the workload beyond which the new card limit will be
reduced to 0. If workloadMax is greater than workloadLimit then the new
card limit will be gradually reduced as workload increases from
workloadLimit to workloadMax.

Recommendation: Set workloadMax to the workload beyond which you don't want
to see any new cards. If you want your new cards to be all-or-nothing, set
workloadMax to the same valueas WorkloadLimit.
