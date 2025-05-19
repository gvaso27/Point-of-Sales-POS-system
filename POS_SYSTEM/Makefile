help:
	echo "No Help"

install:
	python -m pip install --upgrade pip
	python -m pip install --upgrade poetry
	poetry install --no-root

lock:
	poetry lock --no-update

update:
	poetry update

format:
	poetry run ruff format app
	poetry run ruff check  app --fix

lint:
	poetry run ruff check app
	poetry run mypy app
