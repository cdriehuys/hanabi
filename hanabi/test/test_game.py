import pytest

import cards
from game import Game


@pytest.mark.parametrize('card_value', range(1, 6))
@pytest.mark.parametrize('played_value', range(1, 6))
def test_is_card_useful_already_played(card_value, played_value):
    """
    If a card's number is less than or equal to the played stack of its
    color, it should no longer be useful.
    """
    game = Game([])
    game.stacks[cards.Colors.BLUE] = played_value
    card = cards.Card(cards.Colors.BLUE, card_value)

    expected = card_value > played_value

    assert game.is_card_useful(card) == expected


@pytest.mark.parametrize('killed_value', range(1, 5))
def test_is_card_useful_killed_by_discard(killed_value):
    """
    A card should be not useful if any of the numbers lower than it have
    been entirely discarded, thus killing the color.
    """
    game = Game([])
    for _ in range(cards.Deck.CARD_COUNT_MAP[killed_value]):
        game.discards.append(cards.Card(cards.Colors.BLUE, killed_value))

    assert not game.is_card_useful(cards.Card(cards.Colors.BLUE, 5))
