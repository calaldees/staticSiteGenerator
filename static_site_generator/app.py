import datetime
import enum
import json
import logging
import os
import pickle
import subprocess
from collections.abc import Mapping, MutableMapping
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    path_metadata = PATH_BUILD.joinpath("metadata.json")
    path_metadata_db = PATH_BUILD.joinpath("metadata.pickle")
    metadata_db: MutableMapping[Path, Mapping] = {}
    if path_metadata_db.exists():
        with path_metadata_db.open("rb") as f:
            metadata_db = pickle.load(f)

    # Consider fastscan of ousource + destination files?
    has_modified = False
    for path_src in PATH_CONTENT.glob("**"):
        if path_src.suffix != ".md" or path_src.stem.startswith("_"):
            continue

        path_mtime = path_src.stat().st_mtime
        path_dst = PATH_BUILD.joinpath(
            path_src.relative_to(PATH_CONTENT).with_suffix(".html")
        )
        path_output_mtime = path_dst.stat().st_mtime if path_dst.exists() else 0
        if path_mtime == path_output_mtime:
            log.debug(f"skipping {path_src}")
            continue

        frontmatter_markdown = frontmatter.load(path_src)
        metadata = frontmatter_markdown.metadata
        html = render_markdown_to_html(frontmatter_markdown.content)

        # Augment fontmatter-metadata with additional stuff
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

        rendered = render_template(
            Path("templates").joinpath(metadata["template"]),
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

        has_modified = True
        metadata_db[metadata["path_dst"]] = metadata
        log.info(path_dst)

    if has_modified:
        log.info(f"has_modified - saving {path_metadata_db} + {path_metadata}")
        with path_metadata_db.open("wb") as f:
            pickle.dump(metadata_db, f)
        with path_metadata.open("w") as f:
            data = {str(k): v for k, v in metadata_db.items()}
            json.dump(data, f, cls=JSONObjectEncoder)

    for path_static in PATHS_STATIC:
        if not path_static.is_dir():
            continue
        for path_src in path_static.iterdir():
            path_dst = PATH_BUILD.joinpath(path_src)
            if not path_dst.exists() or (path_dst.exists() and path_src.stat().st_mtime > path_dst.stat().st_mtime):
                path_dst.parent.mkdir(parents=True, exist_ok=True)
                path_src.copy(path_dst)
                log.debug(f'static: {path_dst}')
