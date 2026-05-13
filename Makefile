
run:
	uv run --no-dev static_site_generator/app.py

#example:
#	showdown makehtml --input test.md

test:
	uv run pytest
clean:
	rm -rf build *.pickle
clean_all: clean
	rm -rf .venv node_modules package-lock.json

upgrade:
	uv lock --upgrade
