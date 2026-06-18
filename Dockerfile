FROM python:alpine AS base
    COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
    ENV UV_SYSTEM_PYTHON=1
    ENV UV_NO_SYNC=True

    WORKDIR /site/

    RUN apk add npm make
    COPY package.json .
    RUN npm install

    COPY pyproject.toml .
    RUN UV_NO_SYNC=False uv sync --no-dev

    COPY static_site_generator ./static_site_generator/
    COPY base ./base/
    COPY myMarked .

FROM base AS build
    COPY example ./example/
    COPY Makefile .
    RUN make

FROM nginx:alpine AS nginx
    EXPOSE 80
    WORKDIR /usr/share/nginx/html

    COPY --from=build /site/build/ .

    RUN sed -i'' -e 's/#gzip  on;/gzip  on;  gzip_static  on;  gzip_types text\/plain text\/css application\/javascript application\/json application\/x-javascript text\/xml application\/xml application\/xml+rss text\/javascript;  gzip_vary on; /g' /etc/nginx/nginx.conf
    RUN find . -type f \
            -iname '*.html' \
        -or -iname '*.css' \
        -or -iname '*.svg' \
        -or -iname '*.js' \
        -or -iname '*.json' \
        -or -iname '*.xml' \
        -or -iname '*.txt' \
        -or -iname '*.md' \
        -exec gzip -9 -k '{}' \;
