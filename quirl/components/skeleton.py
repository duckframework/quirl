"""
A loading placeholder that shimmers while content loads.
"""

from duck.html.components.container import Container

from quirl.theme import Theme


# Border radius used for each skeleton shape variant
VARIANT_RADIUS_MAP = {
    "rect": None,
    "text": "6px",
    "circle": "50%",
}


class Skeleton(Container):
    """
    A loading placeholder that shimmers while content loads.

    Renders as a rounded block with an animated light sweep. Use multiple
    Skeletons to mock cards, avatars, or text blocks.

    Note: requires `quirl.styles.quirl_global_styles()` added to the page
    head for the shimmer animation to run.

    Usage:
    ```python
    Skeleton(width="100%", height="16px", variant="text")
    ```

    Optional Props:
    - variant: One of rect, text, circle. Defaults to rect.
    - width: CSS width value. Defaults to 100%.
    - height: CSS height value. Defaults to 16px.
    - border_radius: Corner radius, overrides variant default.
    """

    docs_preview_kwargs = {
        "width": "200px",
        "height": "16px",
        "variant": "text",
    }

    def on_create(self):
        """
        Build the skeleton with shimmer animation styles.
        """
        super().on_create()

        variant = self.kwargs.get("variant", "rect")
        default_radius = VARIANT_RADIUS_MAP.get(variant) or Theme.current.border_radius
        surface = Theme.current.border_color

        # Apply skeleton placeholder styles with a moving highlight sweep
        self.style.update({
            "width": self.kwargs.get("width", "100%"),
            "height": self.kwargs.get("height", "16px"),
            "border-radius": self.kwargs.get("border_radius", default_radius),
            "background": (
                f"linear-gradient(90deg, {surface} 25%, "
                f"rgba(255, 255, 255, 0.18) 50%, {surface} 75%)"
            ),
            "background-size": "200% 100%",
            "animation": "quirl-shimmer 1.5s ease-in-out infinite",
        })

        self.props["class"] = "quirl-skeleton"
