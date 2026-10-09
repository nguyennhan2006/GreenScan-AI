.PHONY: install ui app test lint format demo evaluate serve build clean

install:
	python -m pip install -e ".[dev,crawl]"

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

# Build the web UI once; `make app` then serves API + UI on http://localhost:8000.
ui:
	cd frontend && npm ci && npm run build

app:
	quantum-agent app

build:
	python -m build

clean:
	rm -rf .quantum build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache
