"""
Theme system for Quirl components.

Provides design tokens (colors, spacing, typography, etc.) as CSS custom
properties so any Quirl component can reference var(--theme-<token>)
instead of hardcoded literals. Tokens are open-ended — add any name/value
pair, not just the built-in defaults.
"""
from duck.html.components.theme import Theme


class Theme(Theme):
    """
    An extensible set of design tokens.

    Tokens live in a plain dict so new ones can be added at construction
    time or later via update() — useful for overrides, plugin tokens,
    or runtime values. Each token becomes --quirl-<token> in CSS.

    Access the globally active theme at the class level:
    
    ```python
    active = Theme.current
    Theme.current = my_custom_theme
    ```
    """

    CSS_PREFIX: ClassVar[str] = "theme"

    DEFAULTS: ClassVar[dict[str, str]] = {
        "accent_color": "#F5C842",
        "surface_color": "#111318",
        "surface_elevated_color": "#1C1F26",
        "text_color": "#F5F5F5",
        "muted_text_color": "rgba(245, 245, 245, 0.6)",
        "border_color": "rgba(255, 255, 255, 0.12)",
        "success_color": "#30D158",
        "warning_color": "#FF9F0A",
        "error_color": "#FF453A",
        "info_color": "#0A84FF",
        "border_radius": "12px",
        "border_radius_sm": "8px",
        "font_family": (
            "-apple-system, BlinkMacSystemFont, 'SF Pro Text', "
            "'Segoe UI', Roboto, sans-serif"
        ),
        "font_size": "1rem",
        "spacing": "8px",
        "shadow_sm": "0 1px 2px rgba(0, 0, 0, 0.24)",
        "shadow_md": "0 8px 24px rgba(0, 0, 0, 0.28)",
        "transition_fast": "0.15s cubic-bezier(0.4, 0, 0.2, 1)",
        "transition_spring": "0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
    }

    def __init__(
        self,
        name: str = "default",
        base: Optional["Theme"] = None,
        **tokens: str,
    ):
        """
        Initialize a new theme with layered tokens.

        Args:
            name: Identifier for this theme.
            base:Optional Theme to inherit from before applying defaults and explicit overrides.
            **tokens: Any token name/value pairs. Unknown names are
                accepted, this is what makes the theme extensible.
        """
        super().__init__(name, base=base, **tokens)
