// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let hintCount = 0;
let startTime = null;
let timerInterval = null;

function formatTime(seconds) {
  return `${seconds}s`;
}

function updateGameStats() {
  const difficultySelect = document.getElementById('difficulty-select');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';
  document.getElementById('current-difficulty').innerText = `Difficulty: ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`;
  document.getElementById('current-hints').innerText = `Hints used: ${hintCount}`;
  const elapsed = getElapsedSeconds();
  document.getElementById('current-time').innerText = `Time: ${formatTime(elapsed)}`;
}

function startTimer() {
  hintCount = 0;
  startTime = Date.now();
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  updateGameStats();
  timerInterval = setInterval(updateGameStats, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function getElapsedSeconds() {
  return startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
}

async function newGame() {
  stopTimer();
  hintCount = 0;
  startTimer();

  const difficultySelect = document.getElementById('difficulty-select');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}


async function requestHint() {
  const res = await fetch('/hint');
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const row = data.row;
  const col = data.col;
  const value = data.value;

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = row * SIZE + col;
  const inp = inputs[idx];
  inp.value = value;
  inp.disabled = true;
  inp.className = 'sudoku-cell prefilled';

  hintCount += 1;
  updateGameStats();

  msg.style.color = '#388e3c';
  msg.innerText = 'Hint revealed.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    stopTimer();
    updateGameStats();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    promptForScore();
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

function loadScoreboard() {
  const saved = localStorage.getItem('sudokuScoreboard');
  return saved ? JSON.parse(saved) : [];
}

function saveScoreboard(scores) {
  localStorage.setItem('sudokuScoreboard', JSON.stringify(scores));
}

function renderScoreboard() {
  const scores = loadScoreboard();
  const tbody = document.querySelector('#scoreboard-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  scores.slice(0, 10).forEach((score, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.name}</td>
      <td>${score.time}</td>
      <td>${score.difficulty}</td>
      <td>${score.hints}</td>
    `;
    tbody.appendChild(row);
  });
}

function promptForScore() {
  const name = window.prompt('Congratulations! Enter your name for the scoreboard:');
  if (!name || !name.trim()) {
    return;
  }

  const time = getElapsedSeconds();
  const difficultySelect = document.getElementById('difficulty-select');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';

  const scores = loadScoreboard();
  scores.push({
    name: name.trim(),
    time,
    difficulty: difficulty.charAt(0).toUpperCase() + difficulty.slice(1),
    hints: hintCount,
  });
  scores.sort((a, b) => a.time - b.time);
  saveScoreboard(scores);
  renderScoreboard();
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  const hintBtn = document.getElementById('hint-button');
  if (hintBtn) hintBtn.addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  renderScoreboard();
  // initialize
  newGame();
});