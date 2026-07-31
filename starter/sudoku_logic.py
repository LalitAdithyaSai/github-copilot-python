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


def count_solutions(board, max_solutions=2):
    """Count solutions for the board up to max_solutions."""
    if max_solutions <= 0:
        return 0

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY_CELL:
                solution_count = 0
                for candidate in range(1, SIZE + 1):
                    if not is_valid_placement(board, row, col, candidate):
                        continue
                    board[row][col] = candidate
                    solution_count += count_solutions(board, max_solutions - solution_count)
                    board[row][col] = EMPTY_CELL
                    if solution_count >= max_solutions:
                        return solution_count
                return solution_count
    return 1


def has_unique_solution(board):
    """Return True if the board has exactly one valid Sudoku solution."""
    return count_solutions(board, 2) == 1


def remove_cells_from_solution(board, clue_count):
    """Remove cells from a solved board while preserving unique solution."""
    cells_to_remove = SIZE * SIZE - clue_count
    filled_positions = [(row, col) for row in range(SIZE) for col in range(SIZE) if board[row][col] != EMPTY_CELL]
    random.shuffle(filled_positions)
    attempts = 0
    max_attempts = len(filled_positions) * 20

    while cells_to_remove > 0 and attempts < max_attempts:
        if not filled_positions:
            break

        row, col = random.choice(filled_positions)
        saved_value = board[row][col]
        board[row][col] = EMPTY_CELL

        if has_unique_solution(board):
            cells_to_remove -= 1
            filled_positions = [(r, c) for (r, c) in filled_positions if board[r][c] != EMPTY_CELL]
        else:
            board[row][col] = saved_value
        attempts += 1

    if cells_to_remove > 0:
        raise RuntimeError('Unable to generate puzzle with a unique solution for the desired clue count.')


def generate_puzzle(clue_count=35, max_attempts=5):
    """Generate a new Sudoku puzzle with a unique solution."""
    for attempt in range(max_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy_board(board)

        try:
            remove_cells_from_solution(board, clue_count)
            puzzle = deep_copy_board(board)
            return puzzle, solution
        except RuntimeError:
            continue

    raise RuntimeError('Unable to generate a unique-solution Sudoku puzzle after multiple attempts.')
