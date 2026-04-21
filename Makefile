
example:
	showdown makehtml --input test.md

test:
	uv run pytest
clean:
	rm -rf .venv