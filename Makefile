PROJECT := jobflow_mvp
UV := uv run --project $(PROJECT)

.PHONY: sync run test lint fmt type precommit ci

sync:
	uv sync --project $(PROJECT)

run:
ifndef URL
	$(error Please provide URL="https://example.com/job" )
endif
	$(UV) python -m $(PROJECT).main "$(URL)"

lint:
	$(UV) ruff check $(PROJECT)

fmt:
	$(UV) ruff format $(PROJECT)

type:
	$(UV) mypy $(PROJECT)

test:
	$(UV) pytest $(PROJECT)/tests

precommit:
	$(UV) pre-commit run --all-files

ci: lint fmt type test precommit
