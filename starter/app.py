"""Flask application for a simple Sudoku generator and checker."""

from flask import Flask, jsonify, render_template, request
import random
import sudoku_logic

app = Flask(__name__)

DEFAULT_CLUE_COUNT = 35
BAD_REQUEST = 400

DIFFICULTY_CLUE_COUNTS = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

# Simple in-memory store for the current puzzle and its solution.
game_state = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium',
}


def get_active_solution():
    """Return the current solution from the stored game state."""
    return game_state.get('solution')


def get_clue_count_for_difficulty(difficulty):
    """Return the number of starting clues for the requested difficulty."""
    return DIFFICULTY_CLUE_COUNTS.get(difficulty.lower(), DEFAULT_CLUE_COUNT)


@app.route('/hint')
def reveal_hint():
    """Reveal one correct value in a single empty cell of the current puzzle.

    Returns JSON with `row`, `col`, and `value` for the revealed cell.
    """
    puzzle = game_state.get('puzzle')
    solution = game_state.get('solution')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), BAD_REQUEST

    empty_cells = [
        (r, c)
        for r in range(sudoku_logic.SIZE)
        for c in range(sudoku_logic.SIZE)
        if puzzle[r][c] == 0
    ]

    if not empty_cells:
        return jsonify({'error': 'No empty cells available'}), BAD_REQUEST

    row, col = random.choice(empty_cells)
    value = solution[row][col]

    # Reveal the value in the stored puzzle so subsequent checks consider it filled.
    puzzle[row][col] = value

    return jsonify({'row': row, 'col': col, 'value': value})

@app.route('/')
def index():
    """Render the Sudoku user interface."""
    return render_template('index.html')


@app.route('/new')
def new_game():
    """Generate a new Sudoku puzzle and store the current game."""
    difficulty = request.args.get('difficulty', 'medium')
    clue_count = get_clue_count_for_difficulty(difficulty)

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clue_count)
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 500

    game_state['puzzle'] = puzzle
    game_state['solution'] = solution
    game_state['difficulty'] = difficulty.lower()

    return jsonify({'puzzle': puzzle})


@app.route('/check', methods=['POST'])
def check_solution():
    """Validate the submitted board against the stored solution."""
    request_data = request.get_json(silent=True) or {}
    board = request_data.get('board')

    solution = get_active_solution()
    if solution is None:
        return jsonify({'error': 'No game in progress'}), BAD_REQUEST
    if board is None:
        return jsonify({'error': 'Missing board data'}), BAD_REQUEST

    incorrect_cells = []
    # Only consider cells the user has entered (non-zero) when checking.
    for row_index in range(sudoku_logic.SIZE):
        for column_index in range(sudoku_logic.SIZE):
            entered = board[row_index][column_index]
            # Skip empty cells -- do not mark missing values as incorrect.
            if not entered:
                continue
            if entered != solution[row_index][column_index]:
                incorrect_cells.append([row_index, column_index])

    return jsonify({'incorrect': incorrect_cells})

if __name__ == '__main__':
    app.run(debug=True)