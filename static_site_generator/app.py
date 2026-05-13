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

    # Consider fastscan of ousource + destination files?
    for path in PATH_CONTENT.glob('**'):
        if path.suffix != '.md' or path.stem.startswith('_'):
            continue

        path_mtime = path.stat().st_mtime
        path_output = PATH_BUILD.joinpath(path.relative_to(PATH_CONTENT).with_suffix('.html'))
        path_output_mtime = path_output.stat().st_mtime if path_output.exists() else 0
        if path_mtime == path_output_mtime:
            log.info(f'skipping {path}')
            continue

        frontmatter_markdown = frontmatter.load(path)
        html = render_markdown_to_html(frontmatter_markdown.content)

        rendered = render_template(
            Path("templates/page.html.mako"),
            context=dict(
                metadata=DotWiz(frontmatter_markdown.metadata),
                markdown_html=html,
                path=path,
            ),
        )
        if not rendered:
            log.error(f'Failed to render template {path}')
            continue

        path_output.parent.mkdir(exist_ok=True)
        path_output.write_text(rendered)
        os.utime(path_output, (path_mtime, path_mtime))  # Output mtime should match source
        log.info(path_output)
