# Modsmith Sphinx theme

The theme of Modsmith's sites: the home page, the command line's documentation
and the Python library's documentation. They install it from this folder:

```toml
[dependency-groups]
docs = ["modsmith-sphinx-theme"]

[tool.uv.sources]
modsmith-sphinx-theme = { git = "https://github.com/ModsmithMC/modsmithmc.github.io", subdirectory = "theme" }
```

Then, in `conf.py`:

```python
extensions = ["modsmith_sphinx_theme"]
html_theme = "modsmith"
modsmith_sections = {"get-started": "Get started", "reference": "Reference"}
html_theme_options = {
    "base_url": "https://modsmithmc.org/some-site/",
    "home_url": "https://modsmithmc.org/",
    "repository": "ModsmithMC/some-repo",
}
```

| Option | Meaning |
| --- | --- |
| `base_url` | The site's own address, used by the 404 page |
| `home_url` | Where the logo leads. Defaults to the site's own home page |
| `repository` | The GitHub repository shown in the header and footer |
| `links` | Extra `[title, url]` pairs for the header, such as the other sites |
| `search` | Whether to show the search box. Defaults to true |
| `hero_home` | Whether the root page is a full-width hero page. Defaults to true |
| `site_title` | The name in page titles, such as `Modsmith command line`. Defaults to the project's name |
| `site_name` | The site's name, shown beside the logo and linking to the site's own home. The logo leads to `home_url` |
| `sites` | `[title, url, note]` for each of Modsmith's sites, linked from the footer |
| `moved` | `[old, new]` path prefixes, such as `["/modsmith/", "/modsmith-cli/"]`. The 404 page sends a missing page under `old` to the same page under `new` |

Each folder listed in `modsmith_sections` becomes a header entry with its own
sidebar, built from the toctree caption of the same title.
