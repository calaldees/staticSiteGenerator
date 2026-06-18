FROM python:alpine AS base
    COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
    ENV UV_SYSTEM_PYTHON=1
    ENV UV_NO_SYNC=True

    WORKDIR /site/

    # node is used for converting markdown to html
    # the hope was to have client markdown rendering identical to server markdown rendering.
    # possible https://zerodevx.github.io/zero-md/
    RUN apk add npm make
    COPY package.json .
    RUN npm install
    COPY myMarked .

    COPY pyproject.toml .
    RUN UV_NO_SYNC=False uv sync --no-dev

    COPY static_site_generator ./static_site_generator/
    COPY base ./base/
    # Download 3rd party static assets
    RUN make --directory base/static/css

FROM base AS build
    COPY example ./example/
    COPY Makefile .
    RUN make
