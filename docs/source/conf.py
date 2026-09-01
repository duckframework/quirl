import os
import ast
import sys
import json
import pathlib
import subprocess
import datetime


# METADATA
DUCK_HOMEPAGE = "https://duckframework.com"
QUIRL_DOCS_URL = "https://docs.duckframework.com"
QUIRL_DOCS_MAIN_URL = f"{QUIRL_DOCS_URL}/main"
QUIRL_PACKAGE_RELATIVE_PATH = "../../quirl"
COMPONENTS_TOCTREE_CAPTION = "Quirl Components"

# Metadata for sitemap generation
DOCS_DIR = pathlib.Path(__file__).parent.parent
DOCS_SOURCE_DIRS = ( "source", "source/api")

# Path to the duck package's __init__.py
QUIRL_INIT_PATH = (
    pathlib.Path(__file__).resolve().parent / QUIRL_PACKAGE_RELATIVE_PATH / "__init__.py"
)

# This must be called before any use of the duck.settings module e.g. through duck.app
os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.settings"
os.environ["DJANGO_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.backend.django.duckapp.duckapp.settings"


# Entry point to sphinx
def setup(app):
    def on_html_page_context(app, template_name, template, context, _):
        context["DUCK_HOMEPAGE"] = DUCK_HOMEPAGE
        context["QUIRL_DOCS_URL"] = QUIRL_DOCS_URL
    app.connect("html-page-context", on_html_page_context)
    app.connect("builder-inited", on_builder_inited)
    app.connect("build-finished", on_build_finished)


def on_builder_inited(app):
    """
    Called once Sphinx has loaded all extensions, before any source
    files are read.

    Args:
        app: The Sphinx application object.
    """
    update_components_toctree(pathlib.Path(app.srcdir))


def update_components_toctree(srcdir: pathlib.Path) -> None:
    """
    Render a Documentor page for every public Quirl component and wire
    them into the "Quirl Components" toctree in index.rst, so the docs
    site regenerates automatically as components are added or removed.
    The autodocx-generated API reference (api/index) is untouched.

    Args:
        srcdir: The Sphinx source root (app.srcdir).
    """
    index_path = srcdir / "index.rst"

    if not index_path.exists():
        return

    entries = generate_component_pages(srcdir)

    if not entries:
        return

    content = index_path.read_text(encoding="utf-8")
    updated = inject_toctree_entries(content, COMPONENTS_TOCTREE_CAPTION, entries)
    index_path.write_text(updated, encoding="utf-8")


def generate_component_pages(srcdir: pathlib.Path) -> list:
    """
    Render a Documentor(component_cls=X) page for every public component
    in quirl.components and write it to source/components/<name>.rst.

    Args:
        srcdir: The Sphinx source root (app.srcdir).

    Returns:
        Sorted list of toctree entries relative to srcdir, without the
        .rst extension.
    """
    import quirl.components
    
    from quirl.components.documentor import Documentor
    from quirl.styles import quirl_global_styles

    components_dir = srcdir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    global_styles_html = quirl_global_styles().render()
    entries = []

    for name in quirl.components.__all__:
        component_cls = getattr(quirl.components, name)
        doc_html = Documentor(component_cls=component_cls).render()
        page_html = global_styles_html + doc_html

        page_path = components_dir / f"{name.lower()}.rst"
        write_component_page(page_path, name, page_html)
        entries.append(f"components/{name.lower()}")

    return sorted(entries)


def write_component_page(path: pathlib.Path, title: str, html: str) -> None:
    """
    Write a single component documentation page embedding rendered HTML.

    Args:
        path: Output .rst file path.
        title: Page title, also used as the toctree label.
        html: Rendered HTML markup to embed via a raw:: html block.
    """
    indented_html = "\n".join(
        f"   {line}" if line.strip() else "" for line in html.splitlines()
    )

    content = "\n".join([
        title,
        "=" * len(title),
        "",
        ".. raw:: html",
        "",
        indented_html,
        "",
    ])

    path.write_text(content, encoding="utf-8")


def inject_toctree_entries(content: str, caption: str, entries: list) -> str:
    """
    Insert entries into the toctree directive matching the given caption,
    replacing whatever entries region was already there. Every other
    toctree block in the file is left byte-for-byte untouched.

    Args:
        content: Full text of index.rst.
        caption: The :caption: value identifying which toctree to update.
        entries: Toctree entries to insert, one per line.

    Returns:
        The updated file content.
    """
    lines = content.splitlines()
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip() != ".. toctree::":
            output.append(line)
            i += 1
            continue

        output.append(line)
        i += 1

        option_lines = []
        
        while i < len(lines) and lines[i].strip().startswith(":"):
            option_lines.append(lines[i])
            output.append(lines[i])
            i += 1

        is_target = any(f":caption: {caption}" == opt.strip() for opt in option_lines)
        existing_body = []
        
        while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith(" ")):
            existing_body.append(lines[i])
            i += 1

        if is_target and entries:
            output.append("")
            output.extend(f"   {entry}" for entry in entries)
            output.append("")
        else:
            output.extend(existing_body)

    return "\n".join(output).rstrip() + "\n"


def on_build_finished(app, exception):
    """
    Called when Sphinx finishes building the documentation.

    Args:
        app: The Sphinx application object.
        exception: Exception raised during build, if any.
    """
    generate_sitemap(app.outdir)


def read_metadata_from_init(init_path):
    """
    Reads and extracts metadata variables (e.g., __version__, __author__, __email__)
    from the duck/__init__.py file as string values.

    Args:
        init_path (pathlib.Path): The file path of the package's __init__.py file.

    Returns:
        dict: A dictionary containing metadata like __version__, __author__, and __email__.
    """
    metadata = {}
    
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            # Look for __<name>__ = '<value>'
            if line.startswith("__") and "=" in line:
                try:
                    # Parse the line into an abstract syntax tree (AST) for safety
                    node = ast.parse(line).body[0]
                    if isinstance(node, ast.Assign):
                        key = node.targets[0].id
                        value = node.value.s  # Extract the string value
                        metadata[key] = value
                except Exception:
                    pass  # Skip malformed lines
    return metadata


def sitemap_sort_key(url: str) -> tuple[int, str]:
    """
    Sort sitemap URLs so that top-level pages appear before nested pages.

    Args:
        url: Absolute documentation URL.

    Returns:
        A tuple used for sorting.
    """
    relative = url.removeprefix(f"{QUIRL_DOCS_MAIN_URL}/")

    # Root page always comes first.
    if relative == QUIRL_DOCS_MAIN_URL or url == QUIRL_DOCS_MAIN_URL:
        return (0, "")

    # Pages without subdirectories come before nested pages.
    depth = relative.count("/")

    return (0 if depth == 0 else 1, relative)
    

def generate_sitemap(outdir: str) -> None:
    """
    Generate a sitemap from the built HTML documentation.

    This function scans the generated HTML output instead of the source files,
    ensuring that only pages actually published by Sphinx are included. It
    automatically supports nested directories and future documentation
    structure changes without requiring updates.

    Args:
        outdir: Path to the generated HTML output directory (typically `app.outdir`).
    """
    from duck.contrib.sitemap import SitemapBuilder
    from duck.logging import console
    from duck.utils.path import joinpaths

    # Initialize the output directory and URL collection.
    outdir = pathlib.Path(outdir)
    urls = set()

    # Scan all generated HTML files.
    for html_file in outdir.rglob("*.html"):
        relative = html_file.relative_to(outdir)

        # Ignore Sphinx-generated support directories.
        if any(part.startswith("_") for part in relative.parts):
            continue

        # Resolve the documentation URL.
        if relative == pathlib.Path("index.html"):
            # Root documentation page.
            url = QUIRL_DOCS_MAIN_URL

        elif relative.name == "index.html":
            # Directory index page.
            url = "/".join([
                QUIRL_DOCS_MAIN_URL,
                relative.parent.as_posix(),
            ])

        else:
            # Regular documentation page.
            url = "/".join([
                QUIRL_DOCS_MAIN_URL,
                relative.with_suffix("").as_posix(),
            ])

        
        # Add URL to list.
        urls.add(url)

    # Build the sitemap.
    build_html_dir = outdir.parent
    sitemap_filepath = joinpaths(build_html_dir, "sitemap.xml")

    # Initialize the sitemap builder.
    builder = SitemapBuilder(
        server_url=QUIRL_DOCS_MAIN_URL,
        save_to_file=True,
        filepath=sitemap_filepath,
        extra_urls=sorted(urls, key=sitemap_sort_key),
    )

    # Generate and save the sitemap.
    builder.build()
    
    # Show a debug message.
    console.log(
        f"Sitemap has been saved at {sitemap_filepath}",
        level=console.DEBUG,
    )


# Project information

# Extract metadata from quirl/__init__.py
metadata = read_metadata_from_init(QUIRL_INIT_PATH)
project = "Quirl"
copyright = f"{datetime.datetime.now().year}, Quirl"
author = metadata.get("__author__", "Brian Musakwa")
release = metadata.get("__version__", "")
email = metadata.get("__email__", "digreatbrian@gmail.com")
favicon_url = "/favicon.ico"


# -- General configuration ---------------------------------------------------
extensions = [
    "autodocx",                     # Use sphinx-autodocx for documentation
    "myst_parser",                  # For parsing MyST markdown
    "sphinx.ext.viewcode",          # Add links to source code
    "sphinx.ext.todo",              # Include TODOs in documentation
    "sphinx.ext.mathjax",           # For rendering LaTeX math
    "sphinx.ext.intersphinx",       # For linking to other projects
    "sphinx.ext.autosummary",       # Automatically generate summary tables
    "sphinx_design",                # Useful components for building beautiful docs
    "sphinx_tabs.tabs",             # Tab functionality for documentation
    "sphinx_search.extension",      # Add search functionality
    "sphinx_autodoc_typehints",     # Show type hints in descriptions
    "sphinx_multiversion", # For docs multiversioning
]


# Sphinx multiversion configuration
smv_tag_whitelist = r'^.*$'  # Match all tags
smv_branch_whitelist = r'^(main|stable)$'
smv_remote_whitelist = r'^origin$'


# Napoleon configuration
napoleon_config = {
    "use_google_docstrings": True,  # Enable Google style docstrings
    "use_numpy_docstrings": False,  # Disable Numpy-style docstrings (set to True if needed)
    "napoleon_include_private_with_doc": True,  # Include private members with docstrings
    "napoleon_include_special_with_doc": True,  # Include special methods (e.g., __init__) with docstrings
    "napoleon_use_ivar": True,  # Use 'ivar' for instance variables
    "napoleon_use_param": True,  # Use 'param' for function parameters in Google style
    "napoleon_use_rtype": True,  # Use 'rtype' for return type in Google style
    "napoleon_preprocess_types": True,  # Automatically process type annotations
    "napoleon_attr_annotations": True,  # Enable attribute annotations for class properties
    "napoleon_use_admonition_for_examples": False,  # Use admonitions for 'Examples' sections
    "napoleon_use_admonition_for_notes": True,
    "napoleon_custom_sections": [
        (".*", "notes_style"),  # Treat everything like "Notes:"
    ]
}

# Autodocx Configuration
autodocx_packages = [
    QUIRL_PACKAGE_RELATIVE_PATH,  # Path to our source package
]

autodocx_output_dir = "api"  # Where autodocx should store generated docs
autodocx_render_plugin = "myst"  # Render docstrings using MyST Markdown
autodocx_include_private = True  # Include private members (_ prefixed)
autodocx_include_special = True  # Include special methods (__init__, etc.)
autodocx_sort_names = True  # Sort members alphabetically
autodocx_show_if_no_docstring = True
autodocx_docstring_sections = True

# Exclude specific folders from autodocx
autodocx_exclude = [
    "*/projects/*/backend/django/*",  # Exclude Django backend from all projects
    "*/tests/*",                      # Exclude test folders
    "*/migrations/*",                  # Exclude Django migrations
    "*/experimental/*",                # Exclude experimental code
]


# -- MyST Configuration --
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Set MyST list indent to 4 to avoid leading whitespace in lists
myst_list_indent = 4

# Make sure TOC tree entries are included
myst_heading_anchors = 3  # Allows anchor links for headings and includes them in the TOC


# -- Autosummary Configuration --
autosummary_generate = True


# -- Templates & Exclusions --
templates_path = ["_templates"]
exclude_patterns = ["*/projects/*/backend/*", "_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output --
html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_title = "Quirl"
html_baseurl = "https://quirl.duckframework.com/main/"
html_theme_options = {
    "logo_light": "_static/images/duck-logo.png",
    "logo_dark": "_static/images/duck-logo.png",
    "show_breadcrumbs": True,
    "show_prev_next": True,
    "show_scrolltop": True,
    "main_nav_links": {
        "Explore Main Site": DUCK_HOMEPAGE,
    }
}

# Add buttons at the bottom (footer) of the page
html_context = {
    "next_previous_buttons": True  # Enable next/prev buttons in the footer
}

html_search = True

# Enabling syntax highlighting in code blocks
highlight_language = 'python'  # or the language you're using (e.g., 'bash', 'cpp', etc.)
pygments_style = 'friendly'  # or 'monokai', 'friendly', 'colorful', etc. for different themes
