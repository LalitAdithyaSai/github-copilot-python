Instruction — Sudoku-Copilot
=============================

Purpose
-------
A compact, project-specific style and architecture guide for contributors to the Sudoku Flask project. Goal: keep code readable, consistent, testable, and easy to extend.

General principles
------------------
- Prefer clarity over cleverness. Write code that a new contributor can understand quickly.
- Keep functions small and single-purpose. One level of abstraction per function.
- Favor composition over inheritance unless the domain demands otherwise.
- Name things by their role (e.g., sudoku_solver.solve_grid, ui.routes.show_board).
- Keep logic out of templates: templates are for presentation only.

Python (core & solver)
-----------------------
- Formatting: follow PEP 8. Use 4-space indentation, max line length 88–100.
- Typing: add type hints to public functions and major helpers (parameters and return types).
- Docstrings: every module, public class, and public function should have a short docstring (-> purpose, arguments, return).
- Modules: group related code. Suggested layout:
  - starter/ (Flask entrypoint)
  - app/solver.py (pure Sudoku solving logic, no Flask)
  - app/utils.py (helpers shared by solver and routes)
  - app/api.py or app/routes.py (Flask route handlers)
  - templates/ and static/
- Tests: keep solver logic fully unit-tested. Tests live in tests/ and mock no network or Flask when testing pure logic.
- Error handling: raise typed exceptions from solver; handlers in Flask layer translate them to user-friendly messages.
- Logging: use the logging module. Log at appropriate levels (DEBUG for developers, INFO for high-level events, WARNING/ERROR for issues).

Flask (application layer)
-------------------------
- App Factory: prefer an application factory (create_app) to allow different configs (testing, development, production).
- Blueprints: use blueprints if app grows beyond a few routes; otherwise keep routes in a single clear module.
- Configuration: keep secrets out of source. Use environment variables and a config.py for default values.
- Request handlers:
  - Keep handlers thin: validate input, call solver/service functions, return templates or JSON.
  - Validate and sanitize user input; never trust client-side checks alone.
- Responses:
  - For AJAX endpoints return consistent JSON: { success: bool, data?: ..., error?: { code, message }}
- Templates:
  - Keep Jinja logic minimal. No heavy loops or algorithmic logic in templates.
  - Use partial templates for repeated markup (board cell, controls).
- Security & CORS: enable only what is necessary. CSRF protections for form posts if forms used.

JavaScript (frontend behavior)
-----------------------------
- Organization: place behavior in static/js/ with small modules (board.js, api.js, ui.js).
- Global scope: avoid globals. Use an IIFE or ES module imports (preferred) to scope code.
- DOM updates: separate DOM manipulation (rendering) from data/state logic.
- Event handling: use event delegation for the board grid to keep listeners minimal.
- Network: use fetch with async/await. Centralize API calls in api.js; handle errors and timeouts gracefully.
- UX: show clear loading and error states for long-running solver operations.
- Testing: keep critical UI logic isolated so it can be unit tested or validated manually.

CSS (presentation)
------------------
- Organization: static/css/ with a main.css and small partials if needed (board.css, controls.css).
- Naming: use BEM-like selectors for the board (e.g., .board, .board__cell, .board__cell--given).
- Variables: use CSS variables for colors, spacing and board sizes to keep them easy to tune.
- Responsiveness: ensure the board is usable on different widths (mobile-first where practical).
- Avoid inline styles. Prefer classes and CSS rules.

Project-specific guidelines
---------------------------
- Solver separation: all Sudoku solving algorithms must live in the solver module and be importable/usable without Flask.
- Route naming: use descriptive endpoint names and RESTful verbs for APIs (POST /api/solve, GET /board/new).
- Files:
  - Entrypoint: [starter/app.py](C:/Users/manda/KLAS/Stream Training/Udacity Projects/SUDOKU SOLVER UProject/Sudoku-Copilot/starter/app.py)
  - Templates: [templates/] (use partials for board components)
  - Static: [static/js/, static/css/, static/img/]
- Commit messages: short summary line + optional body. Keep commits focused and small.

Linting, formatting & running
----------------------------
- Run a formatter (black) and a linter (flake8/pylint) before commits. Keep tooling configs in repo if present.
- Run unit tests for solver: python -m pytest tests/test_solver.py
- Run dev server with Flask's recommended pattern (FLASK_APP or create_app pattern).

Onboarding notes
----------------
- To implement a new solver feature: add pure-Python logic in app/solver.py -> add unit tests in tests/ -> expose via Flask route that calls the solver -> update frontend API client and UI.

Keep it readable, modular, and testable. Small, well-named modules + good test coverage = easy evolution of solver strategies and UI improvements.
