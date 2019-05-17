#!/usr/bin/env python3

import collections
import logging

from hanabi import cards, players


logging.basicConfig(level=logging.DEBUG)
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
        self.players = [klass(self) for klass in player_classes]
        self.player_hands = collections.defaultdict(list)

        for _ in range(self.CARDS_PER_PLAYER):
            for player in self.players:
                self.player_hands[player].append(self.deck.cards.pop())

        # Game completion status
        self.turns_remaining = None

    def discard(self, player, card_index):
        """
        Discard a card from a player's hand.

        Args:
            player:
                The player who is discarding.
            card_index:
                The index within the player's hand of the card to
                discard.
        """
        card = self.player_hands[player].pop(card_index)
        self.discards.append(card)

        logger.info(
            'Player %s discarded a %s',
            player,
            card,
        )

        self.draw_card(player)
        self.hints_remaining += 1

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

        logger.debug('Dealing %s a new card.', player)

        self.player_hands[player].append(self.deck.cards.pop())

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
        return self.deck.is_empty and self.turns_remaining == 0

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


def main():
    """
    The entry-point into the game.
    """
    game = Game([players.ConsolePlayer, players.ConsolePlayer])
    game.play()


if __name__ == '__main__':
    main()
