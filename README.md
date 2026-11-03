<p align="center">
  <img src="site/assets/banner.svg" alt="Modsmith" width="100%">
</p>

# Modsmith's website

The source of [modsmithmc.org](https://modsmithmc.org/), and
the theme that all of Modsmith's sites share.

| Address | What it is | Built from |
| --- | --- | --- |
| [`/`](https://modsmithmc.org/) | The home page, for players | `site/` in this repository |
| [`/modsmith/`](https://modsmithmc.org/modsmith/) | The command line's guide | [ModsmithMC/modsmith](https://github.com/ModsmithMC/modsmith) |
| [`/modsmith-python/`](https://modsmithmc.org/modsmith-python/) | The Python library's guide | [ModsmithMC/modsmith-python](https://github.com/ModsmithMC/modsmith-python) |

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

[`brand/`](brand/) holds the logo as PNG: `avatar.png` on the site's dark
background, used for the GitHub organization, and `logo.png` on transparency.
Both are drawn from `site/assets/logo.svg`, one block per pixel.

The `social-*.png` cards, 1280 by 640, are the repositories' preview images on
GitHub. Each is its README banner reframed with more sky, from the matching
`.svg` beside it; render one with a headless browser at that size.
