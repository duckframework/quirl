"""
A loading spinner with theme-aware color.
"""

from duck.html.components.container import Container

from quirl.theme import Theme


# Pixel diameter for each spinner size
SIZE_MAP = {
    "sm": "16px",
    "md": "24px",
    "lg": "32px",
}


class Spinner(Container):
    """
    A loading spinner with theme-aware color.

    Renders as a rotating ring by default, or a trio of bouncing dots in
    the iOS activity-indicator style.

    Note: requires `quirl.styles.quirl_global_styles()` added to the page
    head for the animation to run.

    Usage:
    ```python
    Spinner(size="md", color="var(--quirl-accent-color)")
    Spinner(variant="dots")
    ```

    Optional Props:
    - variant: One of ring, dots. Defaults to ring.
    - size: One of sm, md, lg. Defaults to md.
    - color: Spinner color, defaults to var(--quirl-accent-color)
    """

    docs_preview_kwargs = {
        "size": "md",
    }

    def on_create(self):
        """
        Build the spinner as a rotating ring or bouncing dots.
        """
        super().on_create()

        variant = self.kwargs.get("variant", "ring")

        if variant == "dots":
            self.build_dots()
        else:
            self.build_ring()

    def build_ring(self) -> None:
        """
        Style this component as a rotating ring indicator.
        """
        size = self.kwargs.get("size", "md")
        dim = SIZE_MAP.get(size, SIZE_MAP["md"])
        color = self.kwargs.get("color", Theme.current.accent_color)

        # Apply spinner container styles
        self.style.update({
            "width": dim,
            "height": dim,
            "border": f"3px solid {Theme.current.border_color}",
            "border-top-color": color,
            "border-radius": "50%",
            "animation": "quirl-spin 0.8s linear infinite",
        })

        self.props["class"] = "quirl-spinner"

    def build_dots(self) -> None:
        """
        Style this component as three bouncing dots.
        """
        size = self.kwargs.get("size", "md")
        dot_size = {"sm": "5px", "md": "7px", "lg": "9px"}.get(size, "7px")
        color = self.kwargs.get("color", Theme.current.accent_color)

        self.style.update({
            "display": "inline-flex",
            "align-items": "center",
            "gap": "4px",
        })
        self.props["class"] = "quirl-spinner-dots"

        # Stagger each dot's bounce so they animate in sequence
        for delay in ("0s", "0.15s", "0.3s"):
            self.add_child(Container(
                style={
                    "width": dot_size,
                    "height": dot_size,
                    "border-radius": "50%",
                    "background": color,
                    "animation": f"quirl-bounce-dot 1s ease-in-out {delay} infinite",
                },
            ))
