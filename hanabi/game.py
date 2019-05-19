#!/usr/bin/env python3

import collections
import logging
import time

from tqdm import tqdm

from hanabi import cards, players


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Game:
    """
    This class encapsulates a game of Hanabi including the cards that
    have been played and discarded
    """

    CARDS_PER_PLAYER = 4
    """
    The number of cards that each player should have in their hand at
    all times (until there are no cards left in the deck).
    """

    HINT_GIVING_NUMBERS = [5]
    """
    A list of the numbers that give a hint when played. The typical
    behavior is to give a hint when a stack is completed.
    """

    MAX_BOMBS = 4
    """
    The maximum number of bombs that can be set off before the game is
    lost.
    """

    MAX_HINTS = 8
    """
    The maximum number of hints that can be accumulated. This is also
    the number of hints available at the beginning of the game.
    """

    def __init__(self, player_classes):
        """
        Create a new game.

        Args:
            player_classes:
                An iterable containing the classes used to represent
                each player in the game. Each class will be instantiated
                with a reference to the game instance.
        """
        self.deck = cards.Deck.full_shuffled_deck()
        self._hints_remaining = self.MAX_HINTS

        # Track plays and discards
        self.stacks = collections.defaultdict(int)
        self.discards = []

        # Player creation
        self.players = [klass(self, i) for i, klass in enumerate(player_classes)]
        self.player_hands = collections.defaultdict(list)

        for _ in range(self.CARDS_PER_PLAYER):
            for player in self.players:
                self.player_hands[player].append(self.deck.cards.pop())

        # Game completion status
        self.bombs = 0
        self.turns_remaining = None

    def describe_other_hands(self, player):
        """
        Get representations of each of the other players' hands.

        Args:
            player:
                The player asking for the other hands. Their hand will
                not be included.

        Returns:
            A dictionary of the other players' hands.
        """
        hands = self.player_hands.copy()
        del hands[player]

        return hands

    def discard_player_card(self, player, card, give_hint=True):
        """
        Discard a card that was in a player's hand and give them a new
        card.

        Args:
            player:
                The player who is discarding the card.
            card:
                The card being discarded.
            give_hint:
                A boolean indicating if a hint should be given for the
                discard.
        """
        self.discards.append(card)

        logger.info('%s discarded a %s', player, card)

        self.draw_card(player)

        if give_hint:
            self.hints_remaining += 1

    def discard_player_card_by_index(self, player, card_index):
        """
        Discard a card from a player's hand and give them a new card.

        Args:
            player:
                The player who is discarding.
            card_index:
                The index within the player's hand of the card to
                discard.
        """
        self.discard_player_card(
            player, self.player_hands[player].pop(card_index)
        )

    def draw_card(self, player):
        """
        Give a card to the specified player. If the deck is empty, this
        is a no-op.

        Args:
            player:
                The player to deal a card to.
        """
        if self.deck.is_empty:
            logger.info(
                'Not dealing a card to %s because the deck is empty.',
                player,
            )

            return

        logger.info('Dealing %s a new card.', player)

        self.player_hands[player].append(self.deck.cards.pop())
        logger.debug(
            'Dealing %s a %s.', player, self.player_hands[player][-1]
        )

        if self.deck.is_empty and self.turns_remaining is None:
            self.turns_remaining = len(self.players)

            logger.info(
                'The last card was drawn from the deck. There are %d turns '
                'remaining.',
                self.turns_remaining,
            )

    @property
    def hints_remaining(self):
        """
        Returns:
            The number of available hints.
        """
        return self._hints_remaining

    @hints_remaining.setter
    def hints_remaining(self, hints):
        """
        Set the number of remaining hints.

        The number of hints may not drop below zero or rise above the
        maximum number of hints.

        Args:
            hints:
                The new number of hints available.
        """
        if hints < 0:
            raise ValueError(
                'The number of available hints may not be less than zero.'
            )

        if hints > self.MAX_HINTS:
            logger.info(
                'Capping remaining hints to %d after attempting to set it to '
                '%d',
                self.MAX_HINTS,
                hints,
            )

            hints = self.MAX_HINTS

        logger.debug(
            'The number of available hints changed from %d to %d',
            self._hints_remaining,
            hints,
        )

        self._hints_remaining = hints

    @property
    def is_finished(self):
        """
        Returns:
            A boolean indicating if the game is finished because the
            cards have run out.
        """
        return (
            self.bombs >= self.MAX_BOMBS
            or all(self.stacks[color] == 5 for color in cards.Colors)
            or self.deck.is_empty and self.turns_remaining == 0
        )

    def is_card_useful(self, card):
        """
        Determine if a card is still useful.

        Args:
            card:
                The card to determine the usefulness of.

        Returns:
            A boolean indicating if the card is still useful.
        """
        if card.number <= self.stacks[card.color]:
            return False

        discarded_counts = collections.defaultdict(int)
        for discard in self.discards:
            if discard.color == card.color:
                discarded_counts[discard.number] += 1

        for i in range(card.number - 1, 0, -1):
            if discarded_counts[i] == cards.Deck.CARD_COUNT_MAP[i]:
                return False

        return True

    def is_playable(self, card):
        """
        Determine if a card is playable.

        Args:
            card:
                The card to test for playability.

        Returns:
            A boolean indicating if the provided card is playable.
        """
        return card.number == self.stacks[card.color] + 1

    def is_valid_card_index(self, player, card_index):
        """
        Determine if the provided card index is valid for the given
        player.

        Args:
            player:
                The player to determine if the card index is valid for.
            card_index:
                The index to check the validity of.

        Returns:
            A boolean indicating if the provided card index is valid for
            the given player.
        """
        return 0 <= card_index < len(self.player_hands[player])

    def play(self):
        """
        Start the game and prompt each player for their move until the
        game is finished.
        """
        player_index = 0

        while not self.is_finished:
            self.players[player_index].get_move()

            player_index = (player_index + 1) % len(self.players)

            # If the amount of remaining turns is not None, we can
            # assume the deck is empty and we are now in the final
            # round.
            if self.turns_remaining is not None:
                self.turns_remaining -= 1

                logger.debug('%d turn(s) remaining.', self.turns_remaining)

        logger.info('The game is complete.')

    def play_card(self, player, card_index):
        """
        Play a card from the specified player's hand.

        Args:
            player:
                The player whose hand is played from.
            card_index:
                The index of the card to play within the given player's
                hand.

        Returns:
            A boolean indicating if the card was successfully played. A
            play is unsuccessful if it is not the next card in any of
            the stacks.
        """
        was_played = False
        card = self.player_hands[player].pop(card_index)

        if self.is_playable(card):
            self.stacks[card.color] += 1

            logger.info(
                '%s played the %s increasing the score to %d',
                player,
                card,
                self.score,
            )

            if card.number in self.HINT_GIVING_NUMBERS:
                logger.info(
                    'Giving an additional hint because a %d was played.',
                    card.number,
                )
                self.hints_remaining += 1

            was_played = True
        else:
            logger.info(
                '%s tried to play the %s which is not playable.', player, card
            )
            logger.debug(
                'The %s is not playable on the stacks %s', card, self.stacks
            )
            self.bombs += 1

            self.discard_player_card(player, card, give_hint=False)

        self.draw_card(player)

        return was_played

    @property
    def score(self):
        return sum(stack for stack in self.stacks.values()) - self.bombs


def main():
    """
    The entry-point into the game.
    """
    scores = []
    trials = 10_000
    # trials = 10

    start = time.time()

    for _ in tqdm(range(trials)):
        game = Game([players.GodPlayer for _ in range(4)])
        game.play()

        scores.append(game.score)

    end = time.time()
    avg_score = float(sum(scores)) / len(scores)
    score_counts = collections.Counter(scores)
    wins = score_counts[25]
    win_percentage = wins / float(trials) * 100

    print(f'Ran {trials:,} trials in {end - start:.2f} seconds.')
    print(f'\tAverage score: {avg_score:.2f}')
    print(f'\tWins: {wins:,} ({win_percentage:.2f}%)')


if __name__ == '__main__':
    main()
