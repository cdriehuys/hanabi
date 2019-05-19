import collections
import logging

from cards import Deck
from hanabi.renderers.console import ConsoleRenderer


logger = logging.getLogger(__name__)


class BasePlayer:
    """
    A base class to define behavior that is expected from all players.
    """

    def __init__(self, game, player_index):
        """
        Initialize a new player.

        Args:
            game:
                The game that the player is participating in.
            player_index:
                The index that the player occupies in the game's
                rotation.
        """
        self.game = game
        self.player_index = player_index

    def __str__(self):
        """
        Returns:
            A string describing the player's rotation in the game.
        """
        return f'Player {self.player_index}'

    def discard(self, card_index):
        """
        Discard the card at the given index.

        Args:
            card_index:
                The index of the card in the player's hand to discard.
        """
        self.game.discard_player_card_by_index(self, card_index)

    def play(self, card_index):
        """
        Play the card at the given index.

        Args:
            card_index:
                The index of the card in the player's hand to play.
        """
        self.game.play_card(self, card_index)

    def get_move(self):
        """
        Get the player's move. This must be implemented by a subclass.
        """
        raise NotImplementedError(
            'This method must be implemented by a subclass.'
        )


class ConsolePlayer(BasePlayer):
    """
    A player who interacts with the game through the console.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the console player's renderer.
        """
        super().__init__(*args, **kwargs)

        self.renderer = ConsoleRenderer.for_game(self.game)

    @staticmethod
    def get_move_type():
        """
        Get the type of move the player wishes to make from the player.

        Returns:
            The type of move the player wishes to make.
        """
        valid = False
        while not valid:
            move = input('What type of move do you wish to make: ').lower()

            if move in ['discard', 'play']:
                return move

            print('Please enter a valid move type.')

    def get_card_index(self):
        """
        Get the index of a card in the player's hand from the user.

        Returns:
            The index of a card in the player's hand.
        """
        valid = False
        while not valid:
            try:
                index = int(input('Enter the index of your card: '))
            except ValueError:
                print('Please enter a valid number.')

                continue

            if self.game.is_valid_card_index(self, index):
                return index

            print('That card index is not valid. Please try again.')

    def get_move(self):
        print(f"It is now {self}'s turn")

        print(self.renderer.render_game_info())
        print(self.renderer.render_discards())
        print(self.renderer.render_stacks())
        print(self.renderer.render_other_hands(self))

        move_type = self.get_move_type()

        if move_type == 'discard':
            self.discard(self.get_card_index())
        elif move_type == 'play':
            self.play(self.get_card_index())
        else:
            raise ValueError(f'Received unexpected move type: {move_type}')


class GodPlayer(BasePlayer):
    """
    A god player has knowledge of their own hand.
    """

    def get_move(self):
        """
        Play any card that is playable. If none of the cards are
        playable, the player will try to find a card that is no longer
        needed and discard it.
        """
        IndexedCard = collections.namedtuple(
            'IndexedCard', ('card', 'hand_index')
        )

        cards = self.game.player_hands[self]

        playable_cards = []
        unplayable_cards = []

        # Sort cards by playability
        for i, card in enumerate(cards):
            if self.game.is_playable(card):
                playable_cards.append(IndexedCard(card, i))
            else:
                unplayable_cards.append(IndexedCard(card, i))

        # If any card is playable, we should play it.
        if playable_cards:
            indexed_card = min(playable_cards, key=lambda ic: ic.card.number)
            self.play(indexed_card.hand_index)

            return

        # After checking for playable cards, we should get rid of any
        # card we know is useless.
        for indexed_card in unplayable_cards:
            if not self.game.is_card_useful(indexed_card.card):
                self.discard(indexed_card.hand_index)

                return

        # If we have no useless cards, we would rather "use" a hint
        # rather than discard a potentially important card. Since hints
        # are useless to an omniscient AI, we just simulate using the
        # hint here.
        if self.game.hints_remaining > 0:
            self.game.hints_remaining -= 1

            return

        logger.info('%s has no useless cards so discarding first card.', self)

        # The last heuristic we can apply is to sort cards by descending
        # rarity. This decreases the odds that we toss out the only 5
        # for example.
        unplayable_cards.sort(
            key=lambda ic: Deck.CARD_COUNT_MAP[ic.card.number], reverse=True
        )

        self.discard(unplayable_cards[0].hand_index)
