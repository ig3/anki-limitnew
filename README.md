# anki-limitnew
Limit the number of new cards in Anki.

This addon works only with Anki 2.1 and the V2 scheduler.

It limits the number of new cards, based on the number of new and review
cards scheduled and the number of cards studied.

Too many new cards causes overload. The number of cards to be studied each
day increases until it is impossible to study all cards on time. This
defeats the spaced repition schedule and learning becomes less effective.

Manually adjusting the new card limit can avoid such overload, but new
cards are provided at a fixed rate, regardless of how learning is
progressing.

This addon adjusts the number of new cards based on how many cards you have
to study each day - the total workload. When the workload is low, new cards
are presented, up to the deck's limit of new cards per day. But when the
workload is higher, the number of new cards is reduced. If the workload is
very high, no new cards are presented. This allows you to progress quickly
when you are learning quickly but automatically slow down if you are
progressing more slowly.

## Installation

* Download limitnew.ankaddon
* Start Anki and open Tools -> Add-ons
* Drag the downloaded .ankiaddon file onto the add-ons list
* Restart Anki

## Configuration

There are two configuration parameters: workloadLimit and sensitivity.

To change the configuration, start Anki and open Tools -> Add-ons, select
the limitnew addong and click Configure. Set values for the two parameters,
then click OK.

### workloadLimit - default 200

Workload is the sum of total cards studied on the day across all decks,
plus the numbers of review and learning cards remaining for the current deck.

These numbers will change as you progress through your study for the day.
The total cards studied will increase and the number of review and learning
cards remaining will decrease, until there are none left to study.

The limit of new cards will be reduced when workload exceeds the
workloadLimit.

Recommendation: Set your workloadLimit to the number of cards you can study
in a couple of hours, or however much time you have available to study each
day. If you need only a few seconds per card, you might set your limit to
2,000 or higher. If you spend more like 30 seconds per card, then you might
set your limit to about 200.

### sensitivity - default 1.0

The sensitivity determines how quickly the new card limit is reduced when the
workload exceeds the workloadLimit.

If sensitivity is 1.0, the new card limit will be reduced to 0 when the
workload exceeds the workloadLimit by 100%. If your workloadLimit is 200,
then the new card limit will not be reduced to 0 until your workload
reaches 400.

If sensitivity is 10.0, the new card limit will be reduced to 0 when the
workload exceeds the workloadLimit by 10%. If your workloadLimit is 200,
then the new card limit will be reduced to 0 when your workload reaches
220.

Recommendation: Set sensitivity to 1.0 if you want the number of new cards
to be reduced gradually and you don't mind your workload going up to double
your workloadLimit if your learning is slow. Set sensitivity to 10.0 or
higher if you want your workload to be kept closer to your workloadLimit.
