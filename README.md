# Hanabi

Python implementation of Hanabi for exploring strategies and AI possibilities.

## Experiments

### Omniscient AI

**Player Count:** 4

By creating an AI that knows what cards it has, we can roughly determine the
percentage of games that are winnable.

#### Playable Cards

Our first approach was to play any playable card and discard the first card in
the hand if there were no playable cards. This yielded the following results:

```
Ran 100,000 trials in 33.03 seconds.
	Average score: 20.97
	Wins: 3,228 (3.23%)
```

#### Smarter Discards

To improve on this method, we can be more intelligent about how we discard
cards. If a card has a lesser value than the stack for the card's color, it is
no longer useful and can be discarded. With this improvement, we now see the
following results:

```
Ran 100,000 trials in 32.26 seconds.
	Average score: 23.04
	Wins: 22,007 (22.01%)
```

#### Looking at "Killed" Cards

In theory, we could improve on this method by improving our heuristic for a 
card's usefulness. If a card is no longer playable because the color has been 
killed due to the discarding of all of a lower number of that color, the card is
no longer useful. For example, if we have a green 4 but all the green 3s were
discarded, then the green 4 is no longer useful.

It turns out this "improvement" did not impact either the average score or
number of wins in any significant manner. We did not expect a change to the
winning percentage because if we have killed a color through too many discards,
then the game is not winnable by definition. However, we did expect the average
score to improve more. The results we see are below:

```
Ran 100,000 trials in 37.04 seconds.
	Average score: 23.07
	Wins: 22,083 (22.08%)
```

#### Improved Probability Fallback

Inspecting the logs from some of the games showed that the fallback of
discarding the first card in the player's hand if none of the cards are useless
was backfiring sometimes. For example, if we have a 5 at the first position in
our hand but we have a 1 somewhere else in our hand, we should most likely
discard the 1 since discarding the 5 would definitely lead to a loss.

Making this change yields a slight improvement in win rate:

```
Ran 100,000 trials in 38.58 seconds.
	Average score: 23.13
	Wins: 28,473 (28.47%)
```

#### Simulating Hints

The next realization was that there was a major difference between our omniscient
AI and a real player in the way the game is played. If a real player does not
have any playable cards or known useless cards, they also have the option of
giving a hint to another player. Our implementation simply ignored the whole
hint process and went ahead and made a best guess discard.

While hints are useless to our AI since they already know their entire hand, the
process of giving a hint lets us progress through a turn without discarding a
potentially important card. This improvement yields the biggest improvement we
have seen in a while:

```
Ran 100,000 trials in 41.30 seconds.
	Average score: 24.22
	Wins: 52,477 (52.48%)
```

#### Bugs and Player Count

At this point it is quite apparent there is a bug somewhere in our
implementation. The logs from some runs show that players are holding on to
fives they could have played which results in an imperfect score. Additionally,
player count has a huge impact on win rate. If we drop the player count to two
or raise it to five, the win rate drops down to ~30%, but with three players it
jumps to ~57%.

*__Note:__ See the section below regarding win rate.*

#### Optimal Card to Play

Our next observation was that if a player has multiple playable cards, there is
a "best" choice. The logic here is that we want to maximize the number of
players who can follow up the play. For now, our implementation simply plays the
lowest numbered playable card. This yielded a slight improvement to both the win
rate and average score:

```
Ran 100,000 trials in 50.77 seconds.
	Average score: 24.35
	Wins: 58,600 (58.60%)
```

#### Win Rate Musings

After considering strategies further, it seems our seemingly low win rate is not
necessarily a bug but more a result of a lack of strategies for the endgame. As
the game comes to a close, the order of plays becomes more important to ensure
that all cards can be played before the game ends.

## License

This project is licensed under the [MIT License](LICENSE).
