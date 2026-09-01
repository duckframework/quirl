"""
A horizontal or vertical section divider.
"""

from duck.html.components.container import Container
from duck.html.components.label import Label

from quirl.theme import Theme


class Divider(Container):
    """
    A horizontal or vertical section divider.

    Renders as a thin line, or as a line-label-line row when a label is
    given. Vertical dividers do not support labels.

    Usage:
    ```python
    Divider(orientation="horizontal", label="OR")
    ```

    Optional Props:
    - orientation: horizontal or vertical. Defaults to horizontal.
    - label: Optional centered text label (horizontal only).
    - color: Line color, defaults to var(--quirl-border-color)
    """

    docs_preview_kwargs = {
        "orientation": "horizontal",
        "label": "OR",
    }

    def on_create(self):
        """
        Build the divider with optional label and orientation.
        """
        super().on_create()

        orientation = self.kwargs.get("orientation", "horizontal")
        label = self.kwargs.get("label")
        color = self.kwargs.get("color", Theme.current.border_color)

        # A divider is a separator, not literal text content
        self.props["role"] = "separator"
        self.props["aria-orientation"] = orientation

        if orientation == "vertical":
            self.style.update({
                "width": "1px",
                "min-width": "1px",
                "height": "100%",
                "background": color,
                "margin": "0 12px",
                "flex-shrink": "0",
            })
            return

        # Horizontal dividers can optionally carry a centered label
        self.style.update({
            "display": "flex",
            "align-items": "center",
            "gap": "12px",
            "width": "100%",
            "margin": "20px 0",
        })

        if label:
            self.add_children([
                self.build_line(color),
                Label(
                    text=label,
                    style={
                        "color": Theme.current.muted_text_color,
                        "font-size": "0.8rem",
                        "font-weight": "600",
                        "white-space": "nowrap",
                        "text-transform": "uppercase",
                        "letter-spacing": "0.04em",
                    },
                ),
                self.build_line(color),
            ])
        else:
            self.add_child(self.build_line(color))

    def build_line(self, color: str) -> Container:
        """
        Build a single flexible divider line segment.

        Args:
            color: Line color to use.

        Returns:
            A thin, flex-grow Container acting as the line.
        """
        return Container(
            style={
                "height": "1px",
                "background": color,
                "flex": "1",
            },
        )
