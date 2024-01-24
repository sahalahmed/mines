"""
6.1010 Spring '23 Lab 7: Mines
"""

#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    locations = render_2d_locations(game, xray)
    board = ["".join(row) for row in locations]
    return "\n".join(board)


# N-D IMPLEMENTATION


def array_builder(dimensions, remaining_dims, filler):
    """
    Generate n-dimensional array of filler.

    Args:
        dimensions (tuple): Dimensions of the board
        remaining_dims (int): Length of dimensions
        filler: Object to fill array with

    Returns:
        Filled array
    """
    if remaining_dims == 0:
        return filler
    else:
        result = []
        for _ in range(dimensions[-remaining_dims]):
            result.append(array_builder(dimensions, remaining_dims - 1, filler))
        return result


def marker(coordinates, board, mark):
    """
    Modifies array by replacing coordinate
    position with the mark.

    Args:
        coordinates (tuple): Where to modify entry
        board (list): Array to modify
        mark: Object to modify entry to
    """
    if len(coordinates) == 1:
        board[coordinates[0]] = mark
    else:
        marker(coordinates[1:], board[coordinates[0]], mark)


def excavator(coordinates, board):
    """
    Returns array entry at specified coordinate.

    Args:
        coordinates (tuple): Where to retrieve entry
        board (list): Array to retrieve from

    Returns:
        Entry of array at coordinates location.
    """
    if len(coordinates) == 1:
        return board[coordinates[0]]
    else:
        return excavator(coordinates[1:], board[coordinates[0]])


def victory_check(game):
    """
    Checks game victory condition and modifies
    state if necessary.

    Args:
        game (dict): Game state
    """
    hidden_squares = 0
    for coordinates in all_coordinates(game["dimensions"]):
        if excavator(coordinates, game["board"]) != ".":
            if excavator(coordinates, game["hidden"]):
                hidden_squares += 1
    if not hidden_squares:
        game["state"] = "victory"


def get_neighbors(coordinates, dimensions):
    """
    Returns set of legal neigboring coordinates
    to given coordinates.

    Args:
        coordinates (tuple): Location to find neighbors of
        dimensions (tuple): Dimensions of the game board

    Returns:
        Set of all legal neighbors.
    """

    def neighbor_subsequences(seq, dimensions):
        """
        Helper function recursively generating
        raw set of neighbors.

        Args:
            seq (tuple): Location to find neighbors of
            dimensions (tuple): Dimensions of the game board

        Returns:
            Set of all legal neighbors.
        """
        if len(seq) == 1:
            return {
                (point,)
                for point in range(seq[0] - 1, seq[0] + 2)
                if 0 <= point < dimensions[0]
            }
        else:
            first = seq[0:1]
            first_dimensions = dimensions[0:1]
            rest = seq[1:]
            rest_dimensions = dimensions[1:]
            result = set()
            for subseq1 in neighbor_subsequences(first, first_dimensions):
                for subseq2 in neighbor_subsequences(rest, rest_dimensions):
                    result.add(subseq1 + subseq2)
            return result

    return neighbor_subsequences(coordinates, dimensions)


def all_coordinates(seq):
    """
    Generates complete set of coordinates within
    game board.

    Args:
        seq (tuple): Dimensions of the game board

    Returns:
        Set of all game coordinates.
    """
    if not seq:
        return {()}
    else:
        first = seq[0]
        rest = seq[1:]
        result = set()
        for subseq in all_coordinates(rest):
            for i in range(1, first + 1):
                result.add((first - i,) + subseq)
        return result


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """
    dimension_count = len(dimensions)
    board_array = array_builder(dimensions, dimension_count, 0)
    hidden_array = array_builder(dimensions, dimension_count, True)

    for bomb in bombs:
        marker(bomb, board_array, ".")
        for neighbor in get_neighbors(bomb, dimensions):
            val = excavator(neighbor, board_array)
            if val != ".":
                marker(neighbor, board_array, val + 1)
    my_dict = {
        "dimensions": dimensions,
        "board": board_array,
        "hidden": hidden_array,
        "state": "ongoing",
    }
    return my_dict


def dig_nd(game, coordinates, victory_flag=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """
    if game["state"] != "ongoing" or not excavator(coordinates, game["hidden"]):
        return 0

    val = excavator(coordinates, game["board"])
    marker(coordinates, game["hidden"], False)
    revealed = 1

    if val == ".":
        game["state"] = "defeat"
        return revealed
    if val == 0:
        for neighbor in get_neighbors(coordinates, game["dimensions"]):
            revealed += dig_nd(game, neighbor, False)
    if victory_flag:
        victory_check(game)
    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    dimensions = game["dimensions"]
    render = array_builder(dimensions, len(dimensions), 0)

    for coordinates in all_coordinates(game["dimensions"]):
        if not xray and excavator(coordinates, game["hidden"]):
            marker(coordinates, render, "_")
        else:
            val = excavator(coordinates, game["board"])
            if val == ".":
                marker(coordinates, render, ".")
            elif val == 0:
                marker(coordinates, render, " ")
            else:
                marker(coordinates, render, f"{val}")
    return render


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #     render_nd, globals(), optionflags=_doctest_flags, verbose=False
    # )
