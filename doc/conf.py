# -*- coding: utf-8 -*-
import os
import sys
from importlib.metadata import metadata

pkg_name='astk'
meta = metadata('openalea.' + pkg_name)
release = meta.get("version")
# for example take major/minor
version = ".".join(release.split('.')[:3])
author = meta['Author-email'].split(' <')[0]
desc = meta['Summary']
urls = {k:v for k,v in [item.split(',') for item in meta.get_all('Project-URL')]}

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath(".."))  # to include the root of the package

# -- General configuration ------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # support for automatic inclusion of docstring
    "sphinx.ext.autosummary",  # generates autodoc summaries
    "sphinx.ext.doctest",  # inclusion and testing of doctest code snippets
    "sphinx.ext.intersphinx",  # support for linking to other projects
    "sphinx.ext.mathjax",  # support for math equations
    "sphinx.ext.ifconfig",  # support for conditional content
    "sphinx.ext.viewcode",  # support for links to source code
    "sphinx.ext.coverage",  # includes doc coverage stats in the documentation
    "sphinx.ext.todo",  # support for todo items
    "sphinx.ext.napoleon",  # support for numpy and google style docstrings
    "sphinx_favicon",  # support for favicon
    "nbsphinx",  # for integrating jupyter notebooks
    "myst_parser",  # for parsing .md files
]


nbsphinx_allow_errors = True
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
autosummary_generate = True
exclude_patterns = ["build", "_build", "_templates"]
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
# The master toctree document.
master_doc = "index"
# General information about the project.
copyright = u'2015-2025, INRAE-CIRAD-INRIA'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"
# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "header_links_before_dropdown": 6,
    "sidebarwidth": 200,
    "collapse_navigation": "false",
    "icon_links": [
        {
            "name": "GitHub",
            "url": urls['Repository'],
            "icon": "fa-brands fa-github",
        },
    ],
    "show_version_warning_banner": True,
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "secondary_sidebar_items": {
        "**/*": ["page-toc", "edit-this-page", "sourcelink"],
        "examples/no-sidebar": [],
    },
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "_static/openalea_web.svg"
html_favicon = "_static/openalea_web.svg"
# If false, no module index is generated.
html_domain_indices = True
# If false, no index is generated.
html_use_index = True
# If true, the index is split into individual pages for each letter.
html_split_index = False
# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True
# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = True
# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True
# Output file base name for HTML help builder.
htmlhelp_basename = pkg_name + "_documentation"

# -- Options for LaTeX output ---------------------------------------------
latex_elements = {}
latex_documents = [
    (
        master_doc,
        pkg_name+".tex",
        pkg_name+" Documentation",
        "INRAe / INRIA / CIRAD",
        "manual",
    ),
]

# -- Options for manual page output ---------------------------------------
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, pkg_name, pkg_name +" Documentation", [author], 1)]

# -- Options for Texinfo output -------------------------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        pkg_name,
        pkg_name + " Documentation",
        author,
        pkg_name,
        desc,
        "Miscellaneous",
    ),
]
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("https://docs.python.org/", None)}
