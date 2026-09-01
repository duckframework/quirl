"""
Theme system for Quirl components.

Provides design tokens (colors, spacing, typography, etc.) as CSS custom
properties so any Quirl component can reference var(--quirl-<token>)
instead of hardcoded literals. Tokens are open-ended — add any name/value
pair, not just the built-in defaults.
"""

from typing import ClassVar, Optional

from duck.html.components.style import Style


class ThemeMeta(type):
    """
    Metaclass for Theme that provides class-level current theme access.
    """

    @property
    def current(cls) -> "Theme":
        """
        Return the globally active theme.

        Returns:
            The active Theme instance, or DEFAULT_THEME if none was set.
        """
        return _current_theme

    @current.setter
    def current(cls, theme: "Theme") -> None:
        """
        Set the globally active theme.

        Args:
            theme: The Theme instance to activate globally.
        """
        global _current_theme
        _current_theme = theme


class Theme(metaclass=ThemeMeta):
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

    CSS_PREFIX: ClassVar[str] = "quirl"

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
        self.name = name

        # Layer base theme, then class defaults, then explicit overrides
        self.tokens: dict[str, str] = {}
        
        if base is not None:
            self.tokens.update(base.tokens)
        
        # Update tokens
        self.tokens.update(self.DEFAULTS)
        self.tokens.update(tokens)

    def __getattr__(self, key: str) -> str:
        """
        Allow attribute-style reads, e.g. theme.accent_color.

        Args:
            key: Token name to look up.

        Returns:
            The token's string value.

        Raises:
            AttributeError: If the token does not exist.
        """
        if key in self.tokens:
            return self.tokens[key]
        raise AttributeError(f"Theme '{self.name}' has no token '{key}'")

    def get(self, key: str, default: str = "") -> str:
        """
        Return a token value safely without raising.

        Args:
            key: Token name to look up.
            default: Fallback if the token is missing.

        Returns:
            The token value or default.
        """
        return self.tokens.get(key, default)

    def update(self, **tokens: str) -> "Theme":
        """
        Add new tokens or override existing ones after construction.

        Args:
            **tokens: Token name/value pairs to merge in.

        Returns:
            self, for chaining.
        """
        self.tokens.update(tokens)
        return self

    def extend(self, name: str, **overrides: str) -> "Theme":
        """
        Create a new Theme inheriting this theme's tokens.

        Args:
            name: Name for the derived theme.
            **overrides: Tokens to change or add.

        Returns:
            A new Theme instance; this theme is left unchanged.
        """
        return Theme(name=name, base=self, **overrides)

    def to_css_vars(self) -> dict[str, str]:
        """
        Convert every token into a CSS custom property.

        Returns:
            Dict mapping --quirl-<token> to its value.
        """
        css_vars = {}
        
        for token, value in self.tokens.items():
            css_name = token.replace("_", "-")
            css_vars[f"--{self.CSS_PREFIX}-{css_name}"] = value
        
        # Return final css vars.
        return css_vars

    def to_style(self, selector: str = ":root") -> Style:
        """
        Build a Style component declaring this theme's CSS variables.

        Args:
            selector: CSS selector to scope variables under. Defaults to
                :root for global theming. Pass .theme-dark to scope to a
                subtree.

        Returns:
            A Style component, ready for page.add_to_head().
        """
        declarations = "\n".join(
            f"  {prop}: {value};"
            for prop, value in self.to_css_vars().items()
        )
        return Style(inner_html=f"{selector} {{\n{declarations}\n}}")


# Sensible default so components theme themselves out of the box
DEFAULT_THEME = Theme()

# Module-level theme registry for global access
_current_theme: Theme = DEFAULT_THEME
