import pickle
import os
from collections.abc import Mapping
from pathlib import Path
import subprocess
from typing import Any
import logging

import frontmatter
import mako
import mako.lookup
from dotwiz import DotWiz


log = logging.getLogger(__name__)

PATH_BUILD = Path('./build')
PATH_BUILD.mkdir(exist_ok=True)

PATH_CONTENT = Path('./content')
PATH_TEMPLATES = Path("./templates")
PATH_STATIC = Path("./static")
template_lookup = mako.lookup.TemplateLookup(directories=(PATH_TEMPLATES, PATH_STATIC))


def render_template(path: Path, context: Mapping[str, Any]) -> str:
    try:
        return template_lookup.get_template(str(path.relative_to(PATH_TEMPLATES))).render(**context)
    except Exception:
        log.error(mako.exceptions.text_error_template().render())
        return ""


def render_markdown_to_html(markdown: str) -> str:
    """
    Attempt to use the same Markdown renderer as ZeroMD
    Perhaps this can be switched out for a plain python implementation in future?

    Cant use pipe because I cant get the `argv` to `marked/main.js`
    """
    temp = Path('temp.md')
    temp.write_text(markdown)
    process_output = subprocess.run(("node", "./myMarked", "-i", temp), capture_output=True)
    if process_output.returncode:
        raise Exception(process_output)
    return process_output.stdout.decode("utf8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    path_metadata_store = Path('data.pickle')
    metadata_store: Mapping[Path, Mapping] = {}
    if path_metadata_store.exists():
        with path_metadata_store.open('rb') as f:
            metadata_store = pickle.load(f)

    # Consider fastscan of ousource + destination files?
    for path_src in PATH_CONTENT.glob('**'):
        if path_src.suffix != '.md' or path_src.stem.startswith('_'):
            continue

        path_mtime = path_src.stat().st_mtime
        path_dst = PATH_BUILD.joinpath(path_src.relative_to(PATH_CONTENT).with_suffix('.html'))
        path_output_mtime = path_dst.stat().st_mtime if path_dst.exists() else 0
        if path_mtime == path_output_mtime:
            log.info(f'skipping {path_src}')
            continue

        frontmatter_markdown = frontmatter.load(path_src)
        metadata = frontmatter_markdown.metadata
        html = render_markdown_to_html(frontmatter_markdown.content)

        metadata['path_src'] = path_src.relative_to(PATH_CONTENT)
        metadata['path_dst'] = path_dst.relative_to(PATH_BUILD)
        metadata_store[metadata['path_src']] = metadata

        rendered = render_template(
            Path("templates/markdown.html.mako"),
            context=dict(
                metadata=DotWiz(metadata),
                markdown_html=html,
            ),
        )
        if not rendered:
            log.error(f'Failed to render template {path_src}')
            continue

        path_dst.parent.mkdir(exist_ok=True)
        path_dst.write_text(rendered)
        os.utime(path_dst, (path_mtime, path_mtime))  # Output mtime should match source
        log.info(path_dst)

    with path_metadata_store.open('wb') as f:
        pickle.dump(metadata_store, f, pickle.HIGHEST_PROTOCOL)

    breakpoint()