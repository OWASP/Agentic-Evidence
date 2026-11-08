# SPDX-License-Identifier: Apache-2.0
# Only targets that actually work today are listed here. Add schema-check and
# golden-update when M1/M2 make them real (and list them in CONTRIBUTING.md).

.PHONY: setup lint test check

setup:
	uv sync --frozen

lint:
	uv run --frozen ruff check
	uv run --frozen ruff format --check
	uv run --frozen mypy

test:
	uv run --frozen pytest -q

check: lint test
