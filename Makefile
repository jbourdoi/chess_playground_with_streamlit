PYTHON ?= python
VENV ?= .venv

BIN := $(VENV)/Scripts
PYTHON_BIN := $(BIN)/python.exe

SRC := src
TESTS := tests
APP := $(SRC)/chess_app/presentation/streamlit/app.py

.PHONY: install test lint format typecheck snapshot headers pipeline run clean fclean

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

snapshot:
	cat src/chess_app/domain/*.py \
		src/chess_app/application/*.py \
		src/chess_app/ports/*.py \
		src/chess_app/infrastructure/persistence/*py \
		src/chess_app/infrastructure/session/*.py 						> snapshot/sources.py

	cat tests/*/*.py 													> snapshot/tests.py

	cat src/chess_app/presentation/streamlit/*.py \
		src/chess_app/presentation/streamlit/components/*.py						> snapshot/streamlit_impl.py

	cat src/chess_app/presentation/streamlit/static/css/*.css			> snapshot/streamlit_styles.css

	wc -l snapshot/sources.py snapshot/tests.py snapshot/streamlit_impl.py snapshot/streamlit_styles.css


headers:
	bash scripts/check_python_headers.sh
	bash scripts/check_css_headers.sh

pipeline: headers format lint typecheck test snapshot run

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
