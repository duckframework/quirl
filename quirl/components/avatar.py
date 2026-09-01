"""
A user avatar with image support, initials fallback, and status indicator.
"""

from duck.html.components.container import Container
from duck.html.components.image import Image
from duck.html.components.label import Label

from quirl.theme import Theme


# Pixel diameter for each named avatar size
SIZE_MAP = {
    "xs": "24px",
    "sm": "32px",
    "md": "40px",
    "lg": "48px",
    "xl": "64px",
}

# Theme token backing each status dot color
STATUS_TOKEN_MAP = {
    "online": "success_color",
    "away": "warning_color",
    "busy": "error_color",
    "offline": "border_color",
}


class Avatar(Container):
    """
    A circular user avatar with image support, initials fallback, and an
    optional presence status dot.

    Displays a profile image when available, otherwise renders initials
    centered in a themed circle. The image fades in smoothly once loaded.

    Usage:
    ```python
    Avatar(src="/static/user.jpg", alt="Jane Doe", initials="JD", status="online")
    ```

    Required Props:
    - initials: Fallback text when no image is provided

    Optional Props:
    - src: Image source URL
    - alt: Alt text for the image
    - size: One of xs, sm, md, lg, xl. Defaults to md.
    - status: One of online, away, busy, offline. Adds a presence dot.
    - bg_color: Circle background, defaults to var(--quirl-accent-color)
    - color: Initials color, defaults to var(--quirl-surface-color)
    """

    docs_preview_kwargs = {
        "initials": "JD",
        "size": "lg",
        "status": "online",
    }

    def on_create(self):
        """
        Build the avatar circle plus an optional status dot.
        """
        super().on_create()

        size = self.kwargs.get("size", "md")
        dim = SIZE_MAP.get(size, SIZE_MAP["md"])
        status = self.kwargs.get("status")

        # Wrapper stays overflow-visible so the status dot can sit on the edge
        self.style.update({
            "position": "relative",
            "display": "inline-flex",
            "width": dim,
            "height": dim,
            "flex-shrink": "0",
        })

        # Assemble the circle and optional presence dot
        children = [self.build_circle(dim)]

        if status:
            children.append(self.build_status_dot(status, dim))

        self.add_children(children)

    def build_circle(self, dim: str) -> Container:
        """
        Build the clipped circle holding the image or initials.

        Args:
            dim: Pixel diameter for this avatar's size.

        Returns:
            A circular Container with image or initials content.
        """
        src = self.kwargs.get("src")
        alt = self.kwargs.get("alt", "")

        if src:
            content = [Image(
                source=src,
                alt=alt,
                style={
                    "width": "100%",
                    "height": "100%",
                    "object-fit": "cover",
                    "animation": "quirl-fade-in 0.3s ease-out",
                },
            )]
        else:
            content = [Label(
                text=self.kwargs.get("initials", ""),
                style={
                    "color": "inherit",
                    "font-size": "inherit",
                    "font-weight": "inherit",
                },
            )]

        return Container(
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "width": "100%",
                "height": "100%",
                "border-radius": "50%",
                "overflow": "hidden",
                "background": self.kwargs.get("bg_color", Theme.current.accent_color),
                "color": self.kwargs.get("color", Theme.current.surface_color),
                "font-weight": "600",
                "font-size": f"calc({dim} * 0.4)",
                "box-shadow": Theme.current.shadow_sm,
            },
            children=content,
        )

    def build_status_dot(self, status: str, dim: str) -> Container:
        """
        Build the small presence indicator anchored to the avatar's edge.

        Args:
            status: One of online, away, busy, offline.
            dim: Pixel diameter of the parent avatar.

        Returns:
            A positioned Container rendering the status dot.
        """
        token = STATUS_TOKEN_MAP.get(status, STATUS_TOKEN_MAP["offline"])
        dot_size = f"calc({dim} * 0.28)"

        return Container(
            props={"aria-label": f"Status: {status}"},
            style={
                "position": "absolute",
                "bottom": "0",
                "right": "0",
                "width": dot_size,
                "height": dot_size,
                "min-width": "8px",
                "min-height": "8px",
                "border-radius": "50%",
                "background": getattr(Theme.current, token),
                "border": f"2px solid {Theme.current.surface_color}",
            },
        )
