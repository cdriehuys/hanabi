from hanabi import cards


def main():
    """
    The entry-point into the game.
    """
    deck = cards.Deck.full_shuffled_deck()

    for card in deck.cards:
        print(card)


if __name__ == '__main__':
    main()
