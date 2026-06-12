import datetime
import enum
import json
import logging
import os
import pickle
import subprocess
import tempfile
from collections.abc import Generator, Mapping, Sequence
from functools import lru_cache, partial
from hashlib import sha256
from itertools import chain
from pathlib import Path
from typing import Any, NamedTuple

import frontmatter
import mako
import mako.lookup
import yaml
from dotwiz import DotWiz

from .template_vars import recurse_inplace_template_substitution

log = logging.getLogger(__name__)


class JSONObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        if isinstance(obj, set):
            return tuple(obj)
        if isinstance(obj, enum.Enum):
            return "__enum__.{type}.{name}.{value}".format(
                type=type(obj).__name__, name=obj.name, value=obj.value
            )
        return super().default(obj)


# https://stackoverflow.com/a/74728773/3356840
def yaml_include_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    """
    Include YAML file referenced with `!include filename`
    e.g.
        root:
            a: 1
            b: !include addition.yaml
    """
    with open(
        Path(loader.name).parent.joinpath(loader.construct_yaml_str(node)).resolve(),
        "r",
    ) as f:
        return yaml.load(f, type(loader))


YamlLoader = yaml.SafeLoader  # Works with any loader
YamlLoader.add_constructor("!include", yaml_include_constructor)
yaml_load = partial(yaml.load, Loader=YamlLoader)


class Gravatar:
    @staticmethod
    def getGravatarHash(email: str) -> str:
        hash = sha256()
        hash.update(email.strip().lower().encode("utf8"))
        return hash.hexdigest()

    @classmethod
    def getGravatarUrl(cls, email: str) -> str:
        return f"https://0.gravatar.com/avatar/{cls.getGravatarHash(email)}"


def render_markdown_to_html(markdown: str) -> str:
    """
    Attempt to use the same Markdown renderer as ZeroMD
    Perhaps this can be switched out for a plain python implementation in future?

    Cant use pipe because I cant get the `argv` to `marked/main.js`
    """
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(markdown.encode("utf8"))
        process_output = subprocess.run(
            ("node", "./myMarked", "-i", temp.name),
            capture_output=True,
        )
    if process_output.returncode:
        raise Exception(process_output)
    return process_output.stdout.decode("utf8")


class MetadataDB(dict[Path, Mapping]):
    def __init__(self, path_build: Path):
        assert path_build.is_dir()
        self.path_metadata = path_build.joinpath("metadata.json")
        self.path_metadata_db = path_build.joinpath("metadata.pickle")
        if self.path_metadata_db.exists():
            with self.path_metadata_db.open("rb") as f:
                self |= pickle.load(f)
        self.has_changed = False

    def __setitem__(self, key: Path, value: Mapping) -> None:
        self.has_changed = True
        return super().__setitem__(key, value)

    def get(self, key: str | Path) -> Mapping:
        return super().get(key) or super().get(Path(key).with_suffix(".html")) or {}

    def save(self) -> None:
        if not self.has_changed:
            log.debug(f"no {self.__class__.__name__} changes")
            return
        log.info(
            f"has_modified - saving {self.path_metadata_db} + {self.path_metadata}"
        )
        with self.path_metadata_db.open("wb") as f:
            pickle.dump(db, f)
        with self.path_metadata.open("w") as f:
            data = {str(k): v for k, v in db.items()}
            json.dump(data, f, cls=JSONObjectEncoder)

    def get_path_src_startswith(self, startswith: str) -> filter[Mapping]:
        return filter(
            lambda i: str(i["path_src"]).startswith(startswith), self.values()
        )

    @property
    def articles(self) -> Sequence[Mapping]:
        return sorted(
            db.get_path_src_startswith("article"),
            key=lambda i: i.get(
                "date", datetime.datetime.fromtimestamp(0, tz=datetime.UTC)
            ),
            reverse=True,
        )


class PathType(enum.StrEnum):
    DATA = enum.auto()
    CONTENT = enum.auto()
    STATIC = enum.auto()
    TEMPLATES = enum.auto()


class File(NamedTuple):
    filesystem: Path
    relative: Path


class Site:
    def __init__(self, paths: Mapping[PathType, Sequence[Path]]):
        self.paths = paths
        self.template_lookup = mako.lookup.TemplateLookup(
            directories=tuple(
                chain(self.paths[PathType.TEMPLATES], self.paths[PathType.STATIC])
            )
        )

    def get_files(self, path_type: PathType) -> Generator[File]:
        for path in self.paths[path_type]:
            for file in path.glob("**"):
                if file.stem.startswith("_") or not file.is_file():
                    continue
                yield File(file, file.relative_to(path))

    def get_file(self, path_type: PathType, filename: str) -> File:
        for path in self.paths[path_type]:
            path_file = path.joinpath(filename)
            if path_file.is_file():
                return File(path_file, path_file.relative_to(path))
        raise ValueError(f"{filename} not found")

    @lru_cache
    def data(self, filename: str = "index.yaml") -> DotWiz:
        # def _ff(data, file):
        #     with file.open() as f:
        #         data |= yaml_load(f)
        # reduce(_ff, self.get_files(PathType.data), {})
        with self.get_file(PathType.DATA, filename).filesystem.open() as f:
            data = DotWiz(yaml_load(f))
        recurse_inplace_template_substitution(data)
        return data

    def render_template(self, **kwargs) -> str:
        template_pathname = str(
            self.get_file(
                PathType.TEMPLATES,
                kwargs.get("template") or self.data().get("template") or "default.mako",
            ).relative
        )
        try:
            return self.template_lookup.get_template(template_pathname).render(
                **self.data(), **kwargs
            )
        except Exception:
            log.error(mako.exceptions.text_error_template().render())
            return ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    PATH_BUILD = Path("./build")
    PATH_BUILD.mkdir(exist_ok=True)

    PATH_SITE = Path("./site")

    db = MetadataDB(PATH_BUILD)

    site = Site(
        paths={
            PathType.DATA: (PATH_SITE.joinpath("data"),),
            PathType.TEMPLATES: (PATH_SITE.joinpath("templates"),),
            PathType.STATIC: (PATH_SITE.joinpath("static"),),
            PathType.CONTENT: (PATH_SITE.joinpath("content"),),
        }
    )

    # Consider fastscan of source + destination files?
    for path_src, path_src_relative in site.get_files(PathType.CONTENT):
        if path_src.suffix != ".md":
            continue

        path_mtime = path_src.stat().st_mtime
        path_dst = PATH_BUILD.joinpath(path_src_relative.with_suffix(".html"))
        path_dst_relative = path_dst.relative_to(PATH_BUILD)
        path_output_mtime = path_dst.stat().st_mtime if path_dst.exists() else 0
        if path_mtime == path_output_mtime:
            # TODO: and built_template_mtime == template_mtime
            log.debug(f"skipping {path_src}")
            continue

        frontmatter_markdown = frontmatter.load(path_src)
        html = render_markdown_to_html(frontmatter_markdown.content)

        metadata = (
            {
                "template": "article.html.mako",
                "date": datetime.datetime.fromtimestamp(
                    path_output_mtime, tz=datetime.UTC
                ),
            }
            | frontmatter_markdown.metadata
            | {
                "path_src": path_src_relative,
                "path_dst": path_dst_relative,
            }
        )
        if "email" in metadata:
            metadata["gravatar_url"] = Gravatar.getGravatarUrl(metadata["email"])

        # Render single html page
        rendered = site.render_template(html=html, **metadata)
        if not rendered:
            log.error(f"Failed to render template {path_src}")
            continue

        # Write output html
        path_dst.parent.mkdir(exist_ok=True)
        path_dst.write_text(rendered)
        os.utime(path_dst, (path_mtime, path_mtime))  # Output mtime should match source

        db[metadata["path_dst"]] = metadata
        log.info(path_dst)

    # Single page processing complete ------------------------------------------

    db.save()
    if db.has_changed:
        log.info("content db updated: rendering all global_templates")
        for template_pathname in site.data().global_templates:
            log.info(template_pathname)
            rendered = site.render_template(template=template_pathname, db=db)
            PATH_BUILD.joinpath(template_pathname).with_suffix("").write_text(rendered)

    # Copy static assets (if needed)
    PATH_STATIC = 'static'  # I don't like this hard coded output path
    for path_src, path_src_relative in site.get_files(PathType.STATIC):
        path_dst = PATH_BUILD.joinpath(PATH_STATIC, path_src_relative)
        if not path_dst.exists() or (
            path_dst.exists() and path_src.stat().st_mtime > path_dst.stat().st_mtime
        ):
            path_dst.parent.mkdir(parents=True, exist_ok=True)
            path_src.copy(path_dst)
            log.debug(f"static copy: {path_dst}")
