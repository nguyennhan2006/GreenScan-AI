.PHONY: install test lint format demo evaluate serve build clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest --cov=quantum_gw --cov-report=term-missing

lint:
	ruff check src tests
	mypy src

format:
	ruff format src tests
	ruff check --fix src tests

demo:
	quantum-agent demo

evaluate:
	quantum-agent evaluate

serve:
	quantum-agent serve --host 0.0.0.0 --port 8000

build:
	python -m build

clean:
	rm -rf .quantum build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache
