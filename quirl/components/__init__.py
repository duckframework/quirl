"""
Modern UI components for Duck Framework's Lively system.

Components are lazily imported on first access (PEP 562), so
`import quirl.components` stays cheap no matter how many components
the pack grows to — only the submodule you actually touch gets loaded.

Adding a new component only requires one entry in COMPONENT_GROUPS
below; no top-level import statement needed. A submodule that exports
several components together (e.g. carousel.py's MarqueeCarousel and
SliderCarousel) lists them as a group — importing any one of them
caches all of them, since they came from the same import anyway.
"""

import importlib


# Maps submodule -> the public component names it exports
COMPONENT_GROUPS = {
    "badge": ["Badge"],
    "avatar": ["Avatar"],
    "alert": ["Alert"],
    "skeleton": ["Skeleton"],
    "tag": ["Tag"],
    "spinner": ["Spinner"],
    "divider": ["Divider"],
    "code_block": ["CodeBlock"],
    "animation.demo": ["Demo"],
    "documentor": ["Documentor"],
    "carousel": ["MarqueeCarousel", "SliderCarousel"],
}

# Reverse lookup built once: public name -> its submodule
NAME_TO_MODULE = {
    name: module_path
    for module_path, names in _COMPONENT_GROUPS.items()
    for name in names
}


__all__ = list(NAME_TO_MODULE)


def __getattr__(name: str):
    """
    Lazily import a component's submodule and cache its whole group.

    Args:
        name: The attribute being accessed, e.g. "MarqueeCarousel".

    Returns:
        The requested component class.

    Raises:
        AttributeError: If name isn't a known component.
    """
    module_path = NAME_TO_MODULE.get(name)

    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = importlib.import_module(f".{module_path}", __name__)

    # Cache every name this submodule exports, not just the one requested
    for exported_name in COMPONENT_GROUPS[module_path]:
        globals()[exported_name] = getattr(module, exported_name)

    # Add name to globals
    return globals()[name]


def __dir__():
    """
    Report the public component names for tab-completion and dir().
    """
    return sorted(__all__)
