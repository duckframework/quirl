"""
A contextual alert banner for notifications and feedback.
"""

from duck.html.components.container import Container
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph
from duck.html.components.button import Button

from quirl.theme import Theme


# Theme token used for each alert variant's accent and tint
VARIANT_TOKEN_MAP = {
    "info": "info_color",
    "success": "success_color",
    "warning": "warning_color",
    "error": "error_color",
}


class Alert(Container):
    """
    A contextual alert banner for notifications and feedback.

    Supports info, success, warning, and error variants with theme-aware
    color mapping and an optional dismiss button.

    Usage:
    ```python
    Alert(
        title="Heads up",
        description="Your changes have been saved.",
        variant="success",
        dismissible=True,
    )
    ```

    Required Props:
    - description: The alert message body

    Optional Props:
    - title: Optional bold heading above the description
    - variant: One of info, success, warning, error. Defaults to info.
    - dismissible: Show a close button. Defaults to False.
    """

    docs_preview_kwargs = {
        "title": "Success",
        "description": "Your profile has been updated.",
        "variant": "success",
        "dismissible": True,
    }

    docs_animation_steps = [
        {"delay": 1500, "cursor": {"target": "button"}, "target": "button", "action": {"type": "click"}},
        {"delay": 1500},
    ]

    def on_create(self):
        """
        Build the alert with variant-aware theming.
        """
        super().on_create()

        variant = self.kwargs.get("variant", "info")
        tone = getattr(Theme.current, VARIANT_TOKEN_MAP.get(variant, "info_color"))

        # Apply alert container styles as a tinted, rounded iOS-style card
        self.style.update({
            "padding": "16px",
            "border-radius": Theme.current.border_radius,
            "display": "flex",
            "align-items": "flex-start",
            "gap": "12px",
            "background": f"color-mix(in srgb, {tone} 12%, transparent)",
            "color": tone,
            "animation": "quirl-slide-up 0.25s ease-out",
        })

        # Accent dot standing in for a variant icon
        self.add_child(Container(
            style={
                "width": "8px",
                "height": "8px",
                "min-width": "8px",
                "margin-top": "6px",
                "border-radius": "50%",
                "background": tone,
            },
        ))

        self.add_child(self.build_body())
        
        # Initialize dismiss button
        self.dismiss_btn = None
        
        if self.kwargs.get("dismissible"):
            self.dismiss_btn = self.build_dismiss_button()
            self.add_child(self.dismiss_btn)

    def build_body(self) -> Container:
        """
        Build the title and description column.

        Returns:
            A Container holding the alert's text content.
        """
        title = self.kwargs.get("title")
        children = []

        if title:
            children.append(Heading(
                type="h5",
                text=title,
                style={"margin": "0", "color": "inherit", "font-weight": "600"},
            ))

        children.append(Paragraph(
            text=self.kwargs.get("description", ""),
            style={"margin": "0", "color": "inherit", "opacity": "0.9"},
        ))

        return Container(
            style={"display": "flex", "flex-direction": "column", "gap": "4px", "flex": "1"},
            children=children,
        )

    def build_dismiss_button(self) -> Button:
        """
        Build the close button for dismissible alerts.

        Returns:
            A styled Button component that hides the alert on click.
        """
        btn = Button(
            text="\u00d7",
            props={"aria-label": "Dismiss"},
            style={
                "padding": "0",
                "width": "24px",
                "height": "24px",
                "min-width": "24px",
                "border-radius": "50%",
                "font-size": "1rem",
                "line-height": "1",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "background": "transparent",
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
        Handle dismiss click by hiding the alert.

        Args:
            btn: The dismiss button component.
            event: The click event name.
            value: Event payload.
            ws: The active WebSocket connection.
        """
        self.style["display"] = "none"
