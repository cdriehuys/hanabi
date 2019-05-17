class BasePlayer:
    """
    A base class to define behavior that is expected from all players.
    """

    def __init__(self, game):
        """
        Initialize a new player.

        Args:
            game:
                The game that the player is participating in.
        """
        self.game = game

    def discard(self, card_index):
        """
        Discard the card at the given index.

        Args:
            card_index:
                The index of the card in the player's hand to discard.
        """
        self.game.discard(self, card_index)

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

            if move in ['discard']:
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

        move_type = self.get_move_type()

        if move_type == 'discard':
            self.discard(self.get_card_index())
