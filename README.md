<p align="center">
  <img src="site/assets/banner.svg" alt="Modsmith" width="100%">
</p>

<p align="center">
  <strong>The source of modsmithmc.org, and the theme all of Modsmith's sites share.</strong>
</p>

<p align="center">
  <a href="https://modsmithmc.org/">Website</a> · <a href="https://modsmithmc.org/modsmith-cli/">Command line</a> · <a href="https://modsmithmc.org/modsmith-python/">Python library</a>
</p>

---

## Sites

| Address | What it is | Built from |
| --- | --- | --- |
| [`/`](https://modsmithmc.org/) | The project's home: what Modsmith does, and where to start | `site/` in this repository |
| [`/modsmith-cli/`](https://modsmithmc.org/modsmith-cli/) | The command line's guide, with a page for every command | [ModsmithMC/modsmith-cli](https://github.com/ModsmithMC/modsmith-cli) |
| [`/modsmith-python/`](https://modsmithmc.org/modsmith-python/) | The Python library's guide and API reference | [ModsmithMC/modsmith-python](https://github.com/ModsmithMC/modsmith-python) |

Each repository publishes its own pages with GitHub Pages. This repository is
the organization's site, so it owns the domain, and the other two appear under
it at their repository's name.

## Build it

```bash
uv sync
uv run sphinx-build -b dirhtml site site/_build/html
```

## Theme

[`theme/`](theme/) holds the Sphinx theme. The other sites install it from
here, so a change to it reaches them the next time they lock their
dependencies.

## Moved pages

The library's guide used to live at the root of the domain. Every page it had
is listed in [`site/moved.txt`](site/moved.txt), and the build writes a page at
each old address that sends visitors to the new one.

## Brand

[`brand/`](brand/) holds the logo as PNG: `avatar.png`, large on transparency,
for the GitHub organization, and `logo.png`, with a margin around it.
Both are drawn from `site/assets/logo.svg`, one block per pixel.

Each site has its own scene of the same hill and anvil: night for the home
page, a terminal's green for the command line, and sunrise at the forge for the
library. [`brand/scenes.py`](brand/scenes.py) draws the other two from the home
page's `site/assets/hero.svg`, along with each site's README banner
(`site/assets/banner*.svg`) and the repositories' preview cards
(`brand/social-*.svg`):

```bash
uv run --no-project --with fonttools --with brotli python brand/scenes.py
```

The `social-*.png` cards, 1280 by 640, are what GitHub shows when a repository
is shared; render each from its `.svg` with a headless browser at that size,
and upload it in the repository's settings.
