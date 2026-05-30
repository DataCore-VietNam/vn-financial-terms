.PHONY: dev install test lint format typecheck check build clean all

# ── Setup ──────────────────────────────────────────────────────────────────
dev:
	pip install -e ".[dev]"
	pre-commit install

install:
	pip install -e .

# ── Quality ────────────────────────────────────────────────────────────────
lint:
	ruff check src tests

format:
	ruff format src tests

format-check:
	ruff format --check src tests

typecheck:
	mypy src

check: lint format-check typecheck
	@echo "All checks passed."

# ── Tests ──────────────────────────────────────────────────────────────────
test:
	pytest -v

test-fast:
	pytest -v -x --no-cov

# ── Build ──────────────────────────────────────────────────────────────────
build:
	python -m build

# ── Clean ──────────────────────────────────────────────────────────────────
clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +

all: check test build
