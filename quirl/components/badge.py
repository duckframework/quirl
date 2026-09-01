"""
A compact status indicator badge.
"""

from duck.html.components.span import Span

from quirl.theme import Theme


# Theme token used for each semantic badge variant
VARIANT_TOKEN_MAP = {
    "neutral": "text_color",
    "accent": "accent_color",
    "success": "success_color",
    "warning": "warning_color",
    "error": "error_color",
    "info": "info_color",
}

# Padding and font size for each badge size
SIZE_STYLE_MAP = {
    "sm": {"padding": "2px 8px", "font-size": "0.75rem"},
    "md": {"padding": "4px 12px", "font-size": "0.875rem"},
    "lg": {"padding": "6px 16px", "font-size": "1rem"},
}


class Badge(Span):
    """
    A compact status indicator badge.

    Renders as a tinted rounded pill, ideal for statuses, counts, or
    categories. Pulls colors from the active theme by default.

    Usage:
    ```python
    Badge(text="New", variant="success")
    ```

    Required Props:
    - text: The badge label text

    Optional Props:
    - variant: One of neutral, accent, success, warning, error, info. Defaults to neutral.
    - dot: Render as a small solid dot with no text. Defaults to False.
    - size: One of sm, md, lg. Defaults to md.
    - bg_color: Override background color.
    - color: Override text color.
    """

    docs_preview_kwargs = {
        "text": "Beta",
        "variant": "accent",
    }
    
    def on_create(self):
        """
        Build the badge with theme-aware tinting, sizing, and radius.
        """
        super().on_create()

        variant = self.kwargs.get("variant", "neutral")
        size = self.kwargs.get("size", "md")
        dot = self.kwargs.get("dot", False)
        tone = getattr(Theme.current, VARIANT_TOKEN_MAP.get(variant, "text_color"))

        # Tint the background with the variant's tone instead of a flat fill
        bg_color = self.kwargs.get("bg_color", f"color-mix(in srgb, {tone} 16%, transparent)")
        text_color = self.kwargs.get("color", tone)

        # Apply theme-aware badge styles
        self.style.update({
            "display": "inline-flex",
            "align-items": "center",
            "border-radius": "9999px",
            "font-weight": "600",
            "line-height": "1",
            "background": bg_color,
            "color": text_color,
            "animation": "quirl-scale-in 0.2s ease-out",
            **SIZE_STYLE_MAP.get(size, SIZE_STYLE_MAP["md"]),
        })

        if dot:
            # Collapse to a small solid indicator dot
            self.style.update({
                "width": "8px",
                "height": "8px",
                "min-width": "8px",
                "padding": "0",
                "background": text_color,
            })
            
            self.inner_html = ""
        
        else:
            self.inner_html = self.kwargs.get("text", "")
