PYTHON ?= python
VENV ?= .venv

BIN := $(VENV)/Scripts
PYTHON_BIN := $(BIN)/python.exe

SRC := src
TESTS := tests
APP := $(SRC)/chess_app/presentation/streamlit/app.py

.PHONY: install test lint format typecheck run clean fclean

install:
	$(PYTHON) -m venv $(VENV)
	$(PYTHON_BIN) -m pip install --upgrade pip
	$(PYTHON_BIN) -m pip install -e ".[dev]"

test:
	$(PYTHON_BIN) -m pytest $(TESTS)

lint:
	$(PYTHON_BIN) -m ruff check $(SRC) $(TESTS)
	$(PYTHON_BIN) -m ruff format --check $(SRC) $(TESTS)

format:
	$(PYTHON_BIN) -m ruff check --fix $(SRC) $(TESTS)
	$(PYTHON_BIN) -m ruff format $(SRC) $(TESTS)

typecheck:
	$(PYTHON_BIN) -m mypy --strict $(SRC)

pipeline: format lint typecheck test

run:
	$(PYTHON_BIN) -m streamlit run $(APP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
	find . -maxdepth 1 -type d -name "*.egg-info" -exec rm -rf {} +
