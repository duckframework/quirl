"""
A removable or selectable category/filter tag.
"""

from duck.html.components.container import Container
from duck.html.components.label import Label
from duck.html.components.button import Button

from quirl.theme import Theme


class Tag(Container):
    """
    A removable or selectable category/filter tag.

    Renders as a small capsule with text, an optional selected state, and
    an optional dismiss button. Commonly used for filters, categories, or
    selected items.

    Usage:
    ```python
    Tag(tag_text="Python", dismissible=True)
    Tag(tag_text="Active", selected=True)
    ```

    Required Props:
    - tag_text: The tag label text

    Optional Props:
    - dismissible: Show a remove button. Defaults to False.
    - selected: Highlight the tag with the accent color. Defaults to False.
    - bg_color: Background color override.
    - color: Text color override.
    """

    docs_preview_kwargs = {
        "tag_text": "Python",
        "dismissible": True,
    }

    docs_animation_steps = [
        {"delay": 1500, "cursor": {"target": "button"}, "target": "button", "action": {"type": "click"}},
        {"delay": 1500},
    ]

    def on_create(self):
        """
        Build the tag with optional selected state and dismiss button.
        """
        super().on_create()

        selected = self.kwargs.get("selected", False)

        # Selected tags use the accent color, otherwise a themed surface
        default_bg = Theme.current.accent_color if selected else Theme.current.surface_color
        default_color = Theme.current.surface_color if selected else Theme.current.text_color
        default_border = "transparent" if selected else Theme.current.border_color

        # Apply tag container styles
        self.style.update({
            "display": "inline-flex",
            "align-items": "center",
            "gap": "6px",
            "padding": "6px 14px",
            "border-radius": "9999px",
            "background": self.kwargs.get("bg_color", default_bg),
            "color": self.kwargs.get("color", default_color),
            "font-size": "0.875rem",
            "font-weight": "500",
            "border": f"1px solid {default_border}",
            "transition": Theme.current.transition_fast,
            "animation": "quirl-scale-in 0.2s ease-out",
        })

        self.add_child(
            Label(
                text=self.kwargs.get("tag_text", ""),
                style={"color": "inherit"},
            ),
        )
        
        # Initialize self.dismiss_btn
        self.dismiss_btn = None
        
        if self.kwargs.get("dismissible"):
            # Attach dismiss button
            self.dismiss_btn = self.build_dismiss_button()
            self.add_child(self.dismiss_btn)

    def build_dismiss_button(self) -> Button:
        """
        Build the dismiss button for removable tags.

        Returns:
            A styled Button component that triggers removal.
        """
        btn = Button(
            text="\u00d7",
            props={"aria-label": "Remove tag"},
            style={
                "padding": "0",
                "width": "20px",
                "height": "20px",
                "min-width": "20px",
                "border-radius": "50%",
                "font-size": "0.85rem",
                "line-height": "1",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "background": "rgba(0, 0, 0, 0.12)",
                "color": "inherit",
                "border": "none",
                "cursor": "pointer",
                "transition": Theme.current.transition_fast,
            },
        )
        btn.bind("click", self.on_dismiss, update_self=True)
        return btn

    async def on_dismiss(self, btn, event, value, ws):
        """
        Handle dismiss click by hiding the tag.

        Args:
            btn: The dismiss button component.
            event: The click event name.
            value: Event payload.
            ws: The active WebSocket connection.
        """
        self.style["display"] = "none"
