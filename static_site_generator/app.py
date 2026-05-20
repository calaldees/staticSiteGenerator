import datetime
import enum
import json
import logging
import os
import pickle
import subprocess
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any

import frontmatter
import mako
import mako.lookup
from dotwiz import DotWiz

log = logging.getLogger(__name__)

PATH_BUILD = Path("./build")
PATH_BUILD.mkdir(exist_ok=True)

PATH_CONTENT = Path("./content")
PATH_TEMPLATES = Path("./templates")
PATHS_STATIC = (
    Path("./static"),
    Path("./images"),
)
template_lookup = mako.lookup.TemplateLookup(
    directories=(PATH_TEMPLATES,) + PATHS_STATIC
)


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


class Gravatar:
    @staticmethod
    def getGravatarHash(email: str) -> str:
        hash = sha256()
        hash.update(email.strip().lower().encode("utf8"))
        return hash.hexdigest()

    @classmethod
    def getGravatarUrl(cls, email: str) -> str:
        return f"https://0.gravatar.com/avatar/{cls.getGravatarHash(email)}"


def render_template(path: Path, context: Mapping[str, Any]) -> str:
    try:
        return template_lookup.get_template(
            str(path.relative_to(PATH_TEMPLATES))
        ).render(**context)
    except Exception:
        log.error(mako.exceptions.text_error_template().render())
        return ""


def render_markdown_to_html(markdown: str) -> str:
    """
    Attempt to use the same Markdown renderer as ZeroMD
    Perhaps this can be switched out for a plain python implementation in future?

    Cant use pipe because I cant get the `argv` to `marked/main.js`
    """
    temp = PATH_BUILD.joinpath("_temp.md")
    temp.write_text(markdown)
    process_output = subprocess.run(
        ("node", "./myMarked", "-i", temp), capture_output=True
    )
    if process_output.returncode:
        raise Exception(process_output)
    return process_output.stdout.decode("utf8")


class MetadataDB(dict[Path, Mapping]):
    def __init__(self):
        self.path_metadata = PATH_BUILD.joinpath("metadata.json")
        self.path_metadata_db = PATH_BUILD.joinpath("metadata.pickle")
        if self.path_metadata_db.exists():
            with self.path_metadata_db.open("rb") as f:
                self |= pickle.load(f)
        self.has_changed = False

    def __setitem__(self, key: Path, value: Mapping) -> None:
        self.has_changed = True
        return super().__setitem__(key, value)

    def get(self, key: str) -> Mapping:
        return super().get(key) or super().get(Path(key).with_suffix('.html')) or {}

    def save(self) -> None:
        if not self.has_changed:
            return
        log.info(
            f"has_modified - saving {self.path_metadata_db} + {self.path_metadata}"
        )
        with self.path_metadata_db.open("wb") as f:
            pickle.dump(db, f)
        with self.path_metadata.open("w") as f:
            data = {str(k): v for k, v in db.items()}
            json.dump(data, f, cls=JSONObjectEncoder)


def render_global_templates(db: MetadataDB):
    # Render global pages from metadata_db
    GLOBAL_TEMPLATE_PATHS = (
        Path("index.html.mako"),
        Path("authors.html.mako"),
    )
    for path in GLOBAL_TEMPLATE_PATHS:
        rendered = render_template(
            PATH_TEMPLATES.joinpath(path),
            context=dict(db=db),
        )
        PATH_BUILD.joinpath(path).with_suffix("").write_text(rendered)


def copy_static():
    for path_static in PATHS_STATIC:
        if not path_static.is_dir():
            continue
        for path_src in path_static.glob("**"):
            path_dst = PATH_BUILD.joinpath(path_src)
            if not path_dst.exists() or (
                path_dst.exists()
                and path_src.stat().st_mtime > path_dst.stat().st_mtime
            ):
                path_dst.parent.mkdir(parents=True, exist_ok=True)
                path_src.copy(path_dst)
                log.debug(f"static: {path_dst}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    db = MetadataDB()

    # Consider fastscan of source + destination files?
    for path_src in PATH_CONTENT.glob("**"):
        if path_src.suffix != ".md" or path_src.stem.startswith("_"):
            continue

        path_mtime = path_src.stat().st_mtime
        path_dst = PATH_BUILD.joinpath(
            path_src.relative_to(PATH_CONTENT).with_suffix(".html")
        )
        path_output_mtime = path_dst.stat().st_mtime if path_dst.exists() else 0
        if (
            path_mtime == path_output_mtime
        ):  # TODO: and built_template_mtime == template_mtime
            log.debug(f"skipping {path_src}")
            continue

        frontmatter_markdown = frontmatter.load(path_src)
        metadata = frontmatter_markdown.metadata
        html = render_markdown_to_html(frontmatter_markdown.content)

        # Augment frontmatter-metadata with additional stuff
        metadata = (
            {
                "template": "markdown.html.mako",
            }
            | metadata
            | {
                "path_src": path_src.relative_to(PATH_CONTENT),
                "path_dst": path_dst.relative_to(PATH_BUILD),
            }
        )
        if "email" in metadata:
            metadata["gravatar_url"] = Gravatar.getGravatarUrl(metadata["email"])

        # Render single html page
        rendered = render_template(
            PATH_TEMPLATES.joinpath(metadata["template"]),
            context=dict(
                metadata=DotWiz(metadata),
                markdown_html=html,
            ),
        )
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
        render_global_templates(db)
    copy_static()
