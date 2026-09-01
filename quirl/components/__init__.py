"""
Modern UI components for Duck Framework's Lively system.

Components are lazily imported on first access (PEP 562), so
`import quirl.components` stays cheap no matter how many components
the pack grows to — only the submodule you actually touch gets loaded.

Adding a new component only requires one line in _COMPONENT_MAP below;
no top-level import statement needed.
"""

import importlib


# Maps public name -> "submodule:attribute" to import lazily
_COMPONENT_MAP = {
    "Badge": "badge:Badge",
    "Avatar": "avatar:Avatar",
    "Alert": "alert:Alert",
    "Skeleton": "skeleton:Skeleton",
    "Tag": "tag:Tag",
    "Spinner": "spinner:Spinner",
    "Divider": "divider:Divider",
    "CodeBlock": "code_block:CodeBlock",
    "Demo": "animation.demo:Demo",
    "Documentor": "documentor:Documentor",
}

__all__ = list(_COMPONENT_MAP)


def __getattr__(name: str):
    """
    Lazily import and cache a component on first access.

    Args:
        name: The attribute being accessed, e.g. "Badge".

    Returns:
        The requested component class.

    Raises:
        AttributeError: If name isn't a known component.
    """
    target = _COMPONENT_MAP.get(name)

    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_path, attr_name = target.split(":")
    module = importlib.import_module(f".{module_path}", __name__)
    value = getattr(module, attr_name)

    # Cache directly on the module so repeated access skips __getattr__
    globals()[name] = value
    return value


def __dir__():
    """
    Report the public component names for tab-completion and dir().
    """
    return sorted(__all__)
