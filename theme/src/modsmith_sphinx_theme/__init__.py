"""The Sphinx theme shared by Modsmith's sites.

Add ``"modsmith_sphinx_theme"`` to ``extensions`` and set ``html_theme`` to
``"modsmith"``. Each top-level section of a site gets its own sidebar when it is
listed in ``modsmith_sections``, a mapping from folder name to title.
"""

import re
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config

__version__ = "0.1.0"

THEME_DIR = Path(__file__).parent / "modsmith"


def add_section_navigation(
    app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree: Any
) -> None:
    """Give each page the sidebar of its own section."""
    sections: dict[str, str] = app.config.modsmith_sections
    section = pagename.split("/")[0]
    context["section"] = section
    context["sections"] = sections
    context["section_title"] = sections.get(section, "")
    context["section_nav"] = ""
    if section in sections and "toctree" in context:
        tree = context["toctree"](
            maxdepth=3, collapse=True, includehidden=True, titles_only=True
        )
        for part in re.split(r'(?=<p class="caption")', tree):
            if f">{sections[section]}<" in part:
                context["section_nav"] = part


def add_not_found_page(app: Sphinx, config: Config) -> None:
    """Build the theme's 404 page unless the site has its own."""
    config.html_additional_pages.setdefault("404", "404.html")


def publish_not_found_page(app: Sphinx, exception: Exception | None) -> None:
    """Copy the 404 page to the site root, where GitHub Pages looks for it."""
    page = Path(app.outdir, "404", "index.html")
    if exception is None and page.is_file():
        text = page.read_text(encoding="utf-8").replace('="../', '="')
        Path(app.outdir, "404.html").write_text(text, encoding="utf-8")


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the theme and its build hooks."""
    app.add_html_theme("modsmith", str(THEME_DIR))
    app.add_config_value("modsmith_sections", {}, "html", dict)
    app.connect("config-inited", add_not_found_page)
    app.connect("html-page-context", add_section_navigation, priority=400)
    app.connect("build-finished", publish_not_found_page)
    return {"version": __version__, "parallel_read_safe": True}
