.PHONY: test, typing, lint, format, import-sort

test:
	pytest ./tests/

typing:
	mypy .

lint:
	ruff check

format:
	black .

import-sort:
	isort .
