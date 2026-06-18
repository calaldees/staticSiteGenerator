DOCKER_IMAGE:=staticsite
DOCKER_IMAGE_BUILD:=${DOCKER_IMAGE}build
DOCKER_IMAGE_SERVE:=${DOCKER_IMAGE}serve

build_site:
	${MAKE} --directory base/static/css
	uv run --no-dev -m static_site_generator.app example
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

shell_docker:
	docker build --tag ${DOCKER_IMAGE} --target base .
	docker run --rm -it ${DOCKER_IMAGE} /bin/sh

build_docker: clean
	docker build --tag ${DOCKER_IMAGE_BUILD} --target build .

	docker create --name=${DOCKER_IMAGE}_container ${DOCKER_IMAGE_BUILD}
	docker cp ${DOCKER_IMAGE_BUILD}_container:/site/build/ build/
	docker rm ${DOCKER_IMAGE_BUILD}_container

serve_docker: build_docker
	docker build --file nginx.gzip_static.Dockerfile --tag ${DOCKER_IMAGE_SERVE} build/
	docker run --rm --publish 80:80 ${DOCKER_IMAGE_SERVE}

#example:
#	showdown makehtml --input test.md

build/static/images/og_image.png:
	"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
		--headless --screenshot --window-size=1200,630 \
		http://localhost:8000
	mv screenshot.png $@
	optipng $@

test:
	uv run pytest
clean:
	rm -rf build
clean_all: clean
	docker image rm \
		${DOCKER_IMAGE} \
		${DOCKER_IMAGE_BUILD} \
		${DOCKER_IMAGE_SERVE}
	rm -rf \
		.venv \
		node_modules \
		package-lock.json

upgrade:
	uv lock --upgrade
