"""Sudoku puzzle generation and validation utilities."""

import copy
import random

SIZE = 9
EMPTY_CELL = 0
BOX_SIZE = 3


def deep_copy_board(board):
    """Return a deep copy of the board to preserve original state."""
    return copy.deepcopy(board)


def create_empty_board():
    """Create and return an empty Sudoku board."""
    return [[EMPTY_CELL for _ in range(SIZE)] for _ in range(SIZE)]


def is_valid_placement(board, row, col, value):
    """Return True if placing value at (row, col) does not violate Sudoku rules."""
    for index in range(SIZE):
        if board[row][index] == value or board[index][col] == value:
            return False

    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for box_row in range(BOX_SIZE):
        for box_col in range(BOX_SIZE):
            if board[start_row + box_row][start_col + box_col] == value:
                return False

    return True


def fill_board(board):
    """Fill the board with a valid Sudoku solution using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY_CELL:
                continue

            candidate_values = list(range(1, SIZE + 1))
            random.shuffle(candidate_values)
            for candidate in candidate_values:
                if not is_valid_placement(board, row, col, candidate):
                    continue

                board[row][col] = candidate
                if fill_board(board):
                    return True

                board[row][col] = EMPTY_CELL

            return False

    return True


def remove_cells_from_solution(board, clue_count):
    """Remove cells from a solved board to create a playable puzzle."""
    cells_to_remove = SIZE * SIZE - clue_count
    while cells_to_remove > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] == EMPTY_CELL:
            continue

        board[row][col] = EMPTY_CELL
        cells_to_remove -= 1


def generate_puzzle(clue_count=35):
    """Generate a new Sudoku puzzle and return (puzzle, solution)."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy_board(board)

    remove_cells_from_solution(board, clue_count)
    puzzle = deep_copy_board(board)

    return puzzle, solution
