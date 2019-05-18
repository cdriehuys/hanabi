import itertools


class ConsoleRenderer:
    """
    Class to handle rendering a game's state in the console.
    """
    COLUMN_WIDTH = 16

    game_renderers = {}

    def __init__(self, game):
        """
        Create a new console renderer.
        """
        self.game = game

    @staticmethod
    def buffer_section(rendered):
        """
        Add a buffer to a rendered section.

        Args:
            rendered:
                The rendered string to add a buffer to.

        Returns:
            The original string, buffered with newlines.
        """
        return f'\n\n{rendered}\n\n'

    @classmethod
    def for_game(cls, game):
        """
        Get the renderer for a given game. If the renderer doesn't exist
        it will be created.

        Args:
            game:
                The game to get the renderer for.

        Returns:
            A console renderer for the given game.
        """
        if game not in cls.game_renderers:
            cls.game_renderers[game] = cls(game)

        return cls.game_renderers[game]

    def render_discards(self):
        """
        Render the cards that have been discarded.

        Returns:
            A string representation of the discarded cards.
        """
        discards = self.game.discards.copy()
        discards.sort(key=lambda card: card.color.value)

        if not discards:
            return self.buffer_section(
                "Discards: \n\nNo cards have been discarded."
            )

        columns = {}
        for color, cards in itertools.groupby(discards, lambda card: card.color.value):
            columns[color.title()] = list(cards)
            columns[color.title()].sort(key=lambda card: card.number)

        ret_str = 'Discards:\n\n'

        for row in itertools.zip_longest(*columns.values(), fillvalue=''):
            ret_str += ''.join(str(val).ljust(self.COLUMN_WIDTH).title() for val in row)
            ret_str += '\n'

        return self.buffer_section(ret_str)

    def render_game_info(self):
        """
        Render a basic overview of the game.

        Returns:
            A string containing a basic overview of the game.
        """
        ret_str = "Game Overview:\n"
        ret_str += f"\t          Score: {self.game.score}\n"
        ret_str += f"\tRemaining Cards: {len(self.game.deck.cards)}\n"

        if self.game.turns_remaining is None:
            ret_str += "\tTurns Remaining: N/A\n"
        else:
            ret_str += f"\tTurns Remaining: {self.game.turns_remaining}\n"

        return self.buffer_section(ret_str)

    def render_other_hands(self, player):
        """
        Render the hands of all other players.

        Args:
            player:
                The current player. The current player's hand will not
                be included in the output.

        Returns:
            A string representation of the other players' hands.
        """
        hands = self.game.describe_other_hands(player)

        ret_str = 'Player Hands:\n\n'
        ret_str += ''.join(str(player).ljust(self.COLUMN_WIDTH) for player in hands)
        ret_str += '\n'

        for row in itertools.zip_longest(*hands.values(), fillvalue=''):
            ret_str += ''.join(str(val).ljust(self.COLUMN_WIDTH).title() for val in row)
            ret_str += '\n'

        return self.buffer_section(ret_str)

    def render_stacks(self):
        """
        Render the stacks of cards that have been played.

        Returns:
            A string representation of the stacks of played cards.
        """
        ret_str = 'Played Cards:\n\n'
        ret_str += ''.join(color.value.title().ljust(self.COLUMN_WIDTH) for color in self.game.stacks)
        ret_str += '\n'
        ret_str += ''.join(str(value).ljust(self.COLUMN_WIDTH) for value in self.game.stacks.values())

        return self.buffer_section(ret_str)
