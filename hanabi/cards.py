import enum
import random


class Colors(enum.Enum):
    """
    Enum containing possible card colors.
    """
    BLUE = 'blue'
    GREEN = 'green'
    RED = 'red'
    WHITE = 'white'
    YELLOW = 'yellow'


class Card:
    """
    A card has a color and a number.
    """

    def __init__(self, color: Colors, number: int):
        """
        Initialize a new card.

        Args:
            color:
                The card's color.
            number:
                The card's number.
        """
        self.color = color
        self.number = number

    def __str__(self):
        """
        Returns:
            A string containing the card's color and number.
        """
        return f'{self.color.value} {self.number}'


class Deck:
    """
    A deck is a collection of cards.
    """

    CARD_COUNT_MAP = {
        1: 3,
        2: 2,
        3: 2,
        4: 2,
        5: 1,
    }
    """
    A map from card numbers to their counts.
    """

    def __init__(self):
        """
        Initialize a new, empty deck.
        """
        self.cards = []

    @classmethod
    def full_shuffled_deck(cls):
        """
        Returns:
            A new deck containing a random shuffle of all possible
            cards.
        """
        deck = cls()

        for color in Colors:
            for number, count in cls.CARD_COUNT_MAP.items():
                deck.cards += [Card(color, number) for _ in range(count)]

        deck.shuffle()

        return deck

    @property
    def is_empty(self):
        return not len(self.cards)

    def shuffle(self):
        """
        Shuffle the cards in the deck (in place).
        """
        random.shuffle(self.cards)
