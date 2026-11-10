# Practice round deep dive — `practice-20261107T0301-bd8406dc.jsonl.gz`, 10405 tables, 123 teams with >= 20 tables

Pooled over the group's seat-hands (not medians of teams). Preflop rates are per hand in which the seat acted.

| metric | top 10 | top 30 | all | bottom 30 | us (v0) |
|---|---|---|---|---|---|
| pts/table | 22.0 | 19.1 | 13.0 | 6.5 | 8.7 |
| teams | 10 | 30 | 123 | 30 | 1 |
| VPIP | 38% | 31% | 33% | 48% | 75% |
| open-raise / hand | 26% | 21% | 17% | 16% | 26% |
| limp / hand | 2% | 1% | 5% | 15% | 27% |
| call-raise / hand | 7% | 5% | 7% | 10% | 13% |
| 3-bet / hand | 3% | 2% | 3% | 4% | 6% |
| 4-bet+ / hand | 0% | 0% | 1% | 2% | 3% |
| fold unopened / hand | 28% | 33% | 33% | 24% | 5% |
| open size median (x BB) | 2.5 | 2.5 | 2.5 | 2.5 | 2.5 |
| open size <=2.2x | 16% | 15% | 10% | 15% | 0% |
| open size 2.2-3.5x | 78% | 73% | 78% | 79% | 100% |
| open size 3.5-6x | 5% | 11% | 11% | 6% | 0% |
| open size >6x | 0% | 0% | 0% | 0% | 0% |
| open = shove (of opens) | 18% | 19% | 16% | 11% | 5% |
| shove / hand at <=7bb | 31% | 28% | 15% | 7% | 52% |
| shove / hand at 7-12bb | 30% | 26% | 18% | 12% | 39% |
| shove / hand at 12-20bb | 16% | 12% | 7% | 4% | 5% |
| shove / hand at 20-40bb | 7% | 5% | 4% | 3% | 3% |
| shove / hand at >40bb | 3% | 2% | 2% | 4% | 2% |
| call shove at <=7bb | 19% (n=1766) | 14% (n=8198) | 10% (n=43240) | 7% (n=11203) | 42% (n=542) |
| call shove at 7-12bb | 15% (n=3377) | 12% (n=13407) | 11% (n=46920) | 13% (n=7793) | 40% (n=1402) |
| call shove at 12-20bb | 14% (n=5519) | 13% (n=18249) | 12% (n=55941) | 13% (n=10123) | 22% (n=3512) |
| call shove at 20-40bb | 18% (n=11157) | 15% (n=29686) | 14% (n=86916) | 17% (n=17229) | 23% (n=7544) |
| call shove at >40bb | 17% (n=16851) | 15% (n=45033) | 18% (n=180173) | 23% (n=54881) | 28% (n=28549) |
| c-bet flop (as aggressor) | 74% | 72% | 61% | 58% | 68% |
| postflop bet / decision | 37% | 34% | 27% | 24% | 30% |
| postflop raise / decision | 2% | 3% | 4% | 5% | 6% |
| fold facing bet | 55% | 49% | 46% | 50% | 57% |
| raise facing bet | 6% | 8% | 11% | 14% | 17% |
| bet size <0.4 pot | 24% | 17% | 12% | 8% | 2% |
| bet size 0.4-0.7 | 48% | 55% | 62% | 63% | 66% |
| bet size 0.7-1.1 | 24% | 24% | 22% | 24% | 32% |
| bet size >1.1 pot | 4% | 3% | 4% | 5% | 0% |
| bets that are all-in | 6% | 8% | 8% | 8% | 3% |
| shoves preflop : postflop | 29767 : 5204 | 81164 : 15288 | 220302 : 62110 | 41790 : 20634 | 11010 : 6587 |
| survive to table end | 30% | 22% | 13% | 7% | 12% |
| bust hand median | 79 | 81 | 61 | 33 | 23 |
| busts in level 1 | 10% | 11% | 23% | 39% | 46% |
| busts in level 2 | 11% | 12% | 15% | 16% | 21% |
| busts in level 3 | 14% | 13% | 12% | 11% | 12% |
| busts in level 4 | 16% | 15% | 12% | 10% | 7% |
| busts in level 5 | 16% | 15% | 13% | 11% | 5% |
| busts level 6+ | 33% | 36% | 25% | 13% | 9% |
| mean stack at hand 21 (x start, survivors) | 1.24 | 1.23 | 1.25 | 1.31 | 1.56 |
| mean stack at hand 41 (x start, survivors) | 1.53 | 1.47 | 1.49 | 1.56 | 2.20 |
| mean stack at hand 61 (x start, survivors) | 1.92 | 1.79 | 1.76 | 1.83 | 2.89 |
| mean stack at hand 81 (x start, survivors) | 2.47 | 2.24 | 2.10 | 2.12 | 3.53 |
| mean stack at hand 101 (x start, survivors) | 3.19 | 2.82 | 2.60 | 2.66 | 3.99 |
| shown after own open: pair | 35% | 40% | 40% | 36% | 33% |
| shown after own open: two broadway | 27% | 28% | 30% | 35% | 46% |
| shown after own open: ace-x | 9% | 9% | 10% | 11% | 13% |
| shown after own open: suited other | 10% | 8% | 7% | 6% | 2% |
| shown after own open: other | 18% | 14% | 13% | 13% | 5% |
| shown (all): pair | 33% | 37% | 32% | 26% | 25% |
| shown (all): two broadway | 27% | 27% | 28% | 29% | 34% |
| shown (all): ace-x | 10% | 9% | 10% | 11% | 12% |
| shown (all): suited other | 11% | 9% | 10% | 10% | 8% |
| shown (all): other | 19% | 18% | 20% | 24% | 21% |
| exposed the higher kept card | 28% | 24% | 20% | 12% | 0% |

## Top 10 teams

| team | pts/table | tables | VPIP | open/hand | open size | 3-bet | shove/hand | c-bet | fold v bet | survive | bust median |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Always Folds | 23.82 | 576 | 38% | 27% | 2.5 | 2% | 6% | 71% | 52% | 31% | 87 |
| Team 72 | 23.58 | 609 | 38% | 27% | 2.6 | 1% | 3% | 74% | 58% | 34% | 80 |
| TeamBallHog | 23.35 | 540 | 40% | 28% | 2.9 | 2% | 9% | 87% | 57% | 33% | 76 |
| 2 Curry | 22.44 | 533 | 47% | 35% | 2.0 | 9% | 6% | 95% | 59% | 35% | 68 |
| Team 82 | 22.17 | 571 | 25% | 20% | 2.3 | 1% | 6% | 66% | 41% | 24% | 97 |
| AZ | 21.95 | 596 | 40% | 29% | 2.5 | 5% | 10% | 74% | 59% | 34% | 66 |
| one in a krillion | 21.66 | 578 | 35% | 23% | 2.5 | 1% | 4% | 85% | 59% | 30% | 76 |
| Amazing humans | 21.03 | 581 | 40% | 24% | 2.5 | 0% | 0% | 43% | 49% | 25% | 86 |
| pocket rockets | 20.08 | 612 | 48% | 22% | 2.6 | 4% | 2% | 72% | 56% | 29% | 67 |
| Beam | 19.44 | 588 | 35% | 23% | 2.3 | 1% | 12% | 55% | 64% | 24% | 81 |
