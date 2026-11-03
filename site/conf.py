"""Sphinx configuration for Modsmith's home page."""

import html
from pathlib import Path

from sphinx.application import Sphinx

project = "Modsmith"
author = "MeNeither"
copyright = "2026 MeNeither"
release = ""

SITE = "https://modsmithmc.org/"
CLI = SITE + "modsmith-cli/"
LIBRARY = SITE + "modsmith-python/"

extensions = ["myst_parser", "modsmith_sphinx_theme"]
exclude_patterns = ["_build", "assets", "home", "README.md"]
# The home page is written by hand, in home/, and copied over the site's root.
root_doc = "sitemap"
html_extra_path = ["home"]

html_theme = "modsmith"
html_title = project
html_baseurl = SITE
html_theme_options = {
    "base_url": SITE,
    "home_url": SITE,
    "repository": "ModsmithMC/modsmith-cli",
    "site_name": "Home",
    "sites": [
        ["Home", SITE, "What Modsmith is, and how to get it"],
        ["Command line", CLI, "Install modpacks, and every command"],
        ["Python library", LIBRARY, "Build your own tools"],
    ],
    "search": False,
    # The command line's guide was at /modsmith/ before its repository was
    # renamed. This site owns every path no other repository does, so its 404
    # page forwards those.
    "moved": [["/modsmith/", "/modsmith-cli/"]],
}
html_favicon = "assets/logo.svg"
html_static_path = ["assets"]
html_show_sourcelink = False
myst_enable_extensions = ["colon_fence", "deflist"]

# The library's documentation used to live at the root of this domain.
MOVED = Path(__file__).with_name("moved.txt")

REDIRECT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved</title>
<link rel="canonical" href="{target}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace({target_js} + location.search + location.hash);</script>
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


def write_redirects(app: Sphinx, exception: Exception | None) -> None:
    """Send each old address of the library's pages to its new one."""
    if exception is not None:
        return
    for line in MOVED.read_text(encoding="utf-8").splitlines():
        path = line.strip().strip("/")
        if not path:
            continue
        target = f"{LIBRARY}{path}/"
        page = Path(app.outdir, path, "index.html")
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            REDIRECT.format(target=html.escape(target), target_js=repr(target)),
            encoding="utf-8",
        )


def setup(app: Sphinx) -> None:
    """Register the build hooks."""
    app.connect("build-finished", write_redirects)
