from pathlib import Path
import subprocess

import frontmatter
import mako
import mako.lookup

PATH_TEMPLATES = Path("./templates")
PATH_STATIC = Path("./static")
template_lookup = mako.lookup.TemplateLookup(directories=(PATH_TEMPLATES, PATH_STATIC))


def render_template(path: Path, context) -> str:
    try:
        return template_lookup.get_template(
            str(path.relative_to(PATH_TEMPLATES))
        ).render(**context)
    except Exception:
        print(mako.exceptions.text_error_template().render())  # TODO stderr?
        return ""


def render_markdown_to_html(path: Path) -> str:
    """
    Attempt to use the same Markdown renderer as ZeroMD
    Perhaps this can be switched out for a plain python implementation in future?
    """
    process_output = subprocess.run(
        ["node", "./myMarked", "-i", path], capture_output=True
    )
    if process_output.returncode:
        raise Exception("poo")
    return process_output.stdout.decode("utf8")


if __name__ == "__main__":
    content_file = Path("./content/test.md")

    post = frontmatter.load(content_file)
    print(post.metadata)
    # print(post.content)

    content_markdown = render_markdown_to_html(content_file)

    rendered = render_template(
        Path("templates/page.mako"),
        context={
            "markdown": post.content,
            "markdown_html": content_markdown,
            "title": "test",
        },
    )

    print(rendered)
