.PHONY: lint lint_code lint_types test format_ruff revision upgrade sort_imports

source_dirs = src tests migrations scripts

lint: lint_code lint_types

format: format_ruff sort_imports

lint_code:
	@poetry run ruff check $(source_dirs)

lint_types:
	@poetry run pyright $(source_dirs)

format_ruff:
	@ruff format $(source_dirs)

sort_imports:
	@ruff check --select I001 --fix $(source_dirs)

test:
	@python -m pytest -vv

revision:
	@python cli.py migrator autogenerate

upgrade:
	@python cli.py migrator upgrade head
