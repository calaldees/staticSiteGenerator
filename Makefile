

build_site:
	${MAKE} --directory static
	uv run --no-dev static_site_generator/app.py
# -m pdb -c continue

serve: build_site
	python3 -m http.server -d build

serve_watch:
	mkdir -p build
	find . \
		-not -path '*/node_modules/*' -and \
		-not -path '*/.*' -and \
		-not -path '*/__*' -and \
		-not -path '*/metadata.*' -and \
		-not -path '*/build*' | \
		entr -rs '\
			${MAKE} serve \
		\'

build/index.html.gz:
	find build -type f \
			-iname '*.html' \
		-or -iname '*.css' \
		-or -iname '*.svg' \
		-or -iname '*.js' \
		-or -iname '*.json' \
		-or -iname '*.xml' \
		-or -iname '*.txt' \
		-or -iname '*.md' \
		| xargs gzip -9 -k


#example:
#	showdown makehtml --input test.md

test:
	uv run pytest
clean:
	rm -rf build metadata.*
clean_all: clean
	rm -rf .venv node_modules package-lock.json

upgrade:
	uv lock --upgrade
