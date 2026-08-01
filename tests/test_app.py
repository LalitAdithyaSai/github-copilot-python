import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'starter'))

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


SOLVED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def test_incomplete_board_is_not_accepted(client):
    flask_app.game_state['solution'] = SOLVED_BOARD
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 200
    data = response.get_json()
    assert data['complete'] is False
    assert data['correct'] is False
    assert data['incorrect'] == []


def test_incorrect_complete_board_is_not_accepted(client):
    flask_app.game_state['solution'] = SOLVED_BOARD
    incorrect_board = [row[:] for row in SOLVED_BOARD]
    incorrect_board[0][0] = 1

    response = client.post('/check', json={'board': incorrect_board})

    assert response.status_code == 200
    data = response.get_json()
    assert data['complete'] is True
    assert data['correct'] is False
    assert data['incorrect'] == [[0, 0]]


def test_completed_correct_board_is_accepted(client):
    flask_app.game_state['solution'] = SOLVED_BOARD

    response = client.post('/check', json={'board': SOLVED_BOARD})

    assert response.status_code == 200
    data = response.get_json()
    assert data['complete'] is True
    assert data['correct'] is True
    assert data['incorrect'] == []


def test_duplicate_entries_are_reported_as_conflicts(client):
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    board[0][1] = 1

    response = client.post('/validate', json={'board': board})

    assert response.status_code == 200
    data = response.get_json()
    assert data['conflicts'] == [[0, 0], [0, 1]]
