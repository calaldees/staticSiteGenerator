DOCKER_IMAGE:=staticsite

build_site:
	${MAKE} --directory static
	uv run --no-dev -m static_site_generator.app
# -m pdb -c continue

serve: build_site
	python3 -m http.server -d build

serve_watch:
	find . \
		-not -path '*/node_modules/*' -and \
		-not -path '*/.*' -and \
		-not -path '*/__*' -and \
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

build_docker:
	docker build --tag ${DOCKER_IMAGE} --target site .

	docker create --name=${DOCKER_IMAGE}_container ${DOCKER_IMAGE}
	docker cp ${DOCKER_IMAGE}_container:/site/build/ build/
	docker rm ${DOCKER_IMAGE}_container

serve_docker:
	docker build --tag ${DOCKER_IMAGE} .
	docker run --rm --publish 80:80 ${DOCKER_IMAGE}

#example:
#	showdown makehtml --input test.md

test:
	uv run pytest
clean:
	rm -rf build
clean_all: clean
	rm -rf .venv node_modules package-lock.json

upgrade:
	uv lock --upgrade
