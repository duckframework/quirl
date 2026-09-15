"""
An image with placeholder fallback on network error or unset src.
"""

from duck.html.components.container import Container
from duck.html.components.image import CircularImage, Image

from quirl.theme import Theme


class SmartImagePlaceholder(Container):
    """
    Generic fallback placeholder used by SmartImage/CircularSmartImage when
    no placeholder, unset_placeholder, or error_placeholder is supplied.
    Renders a simple neutral image glyph so an unset or failed image never
    ends up passing None as a child.
    """

    # Minimal "broken/generic image" glyph as an inline data URI
    GLYPH_SOURCE = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
        "fill='none' stroke='currentColor' stroke-width='1.5'>"
        "<rect x='3' y='3' width='18' height='18' rx='2'/>"
        "<circle cx='8.5' cy='8.5' r='1.5'/>"
        "<path d='M21 15l-5-5L5 21'/>"
        "</svg>"
    )

    def on_create(self):
        """
        Build a small centered generic-image glyph.
        """
        super().on_create()
        
        # Update style.
        self.style.update({
            "width": "40%",
            "height": "40%",
            "opacity": "0.4",
        })

        self.add_children([
            Image(
                source=self.GLYPH_SOURCE,
                alt="",
                style={
                    "width": "100%",
                    "height": "100%",
                    "object-fit": "contain",
                },
            ),
        ])


class SmartImage(Container):
    """
    A themeable image that falls back to a placeholder when unset or on
    network error. The placeholder can be a URL string or another component
    (e.g. an icon, a Label, a Spinner).

    Required Props:
    - (none — src is optional; placeholder covers the unset case)

    Optional Props:
    - source: Image source URL. If omitted, the placeholder shows immediately.
    - placeholder: Fallback (URL string or component) for both unset src
      and network error, unless overridden below. If neither this nor
      unset_placeholder/error_placeholder is given, a plain
      SmartImagePlaceholder is used instead of showing nothing.
    - unset_placeholder: Shown when src is empty/None. Overrides placeholder.
    - error_placeholder: Shown when the image fails to load. Overrides placeholder.
    - alt: Alt text for the image.
    - fit: object-fit value, defaults to cover.
    - height: Container height (CSS value).
    - width: Container width (CSS value).
    - circular: Whether to render the image (and placeholder) as a circle.
    - image_id: Optional id applied to the underlying <img>, so calling code can
          update `.src` later (e.g. `document.getElementById(image_id).src = url`)
          and have the placeholder swap react live.
    - lazy: If True, sets the native `loading="lazy"` attribute so the
          browser defers fetching until the image nears the viewport. Defaults
          to False (eager). Only affects the primary image, not placeholders.

    Usage:
    ```python
    SmartImage(source="/img/avatar.png", placeholder="/img/default.png")
    SmartImage(source="/img/hero.png", placeholder=Icon(name="broken-image"))
    SmartImage(unset_placeholder=Spinner(), error_placeholder="/img/broken.png")
    ```

    Notes:
        The image, unset placeholder, and error placeholder are all rendered as
            siblings up front. Visibility is then driven entirely by the <img>'s own
            `load`/`error` events, so changing `.src` on the image element at any
            point after mount (empty -> url, url -> a different url, etc.) is
            reflected automatically without re-rendering this component.
    """

    docs_preview_kwargs = {"placeholder": "/static/img/placeholder.png"}

    # Shared data attribute used to scope placeholder lookups to this
    # instance's own siblings via `this.parentElement.querySelector(...)`.
    UNSET_ROLE = "unset"
    ERROR_ROLE = "error"

    def on_create(self):
        """
        Build the image plus both placeholders, wiring load/error handlers
        so visibility reacts live to source changes.
        """
        super().on_create()

        # Get some props
        self.source = self.kwargs.get("source")
        self.fit = self.kwargs.get("fit", self.style.get("object-fit", "cover")) 
        self.circular = self.kwargs.get("circular", False)
        self.image_id = self.kwargs.get("image_id")
        self.width = self.kwargs.get("width", self.style.get("width", None))
        self.height = self.kwargs.get("height", self.style.get("height", None))
        self.lazy = self.kwargs.get("lazy", False)
        
        # Get placeholders
        self.unset_placeholder = (
            self.kwargs.get("unset_placeholder")
            or self.kwargs.get("placeholder")
            or SmartImagePlaceholder()
        )
        self.error_placeholder = (
            self.kwargs.get("error_placeholder")
            or self.kwargs.get("placeholder")
            or SmartImagePlaceholder()
        )
        
        # Set class
        self.klass = "smart-image"
        
        # Update style
        self.style.update({
            "position": "relative",
            "display": "inline-block",
            "overflow": "hidden",
            "background": Theme.current.surface_color,
        })

        if self.width is not None:
            self.style["width"] = self.width

        if self.height is not None:
            self.style["height"] = self.height

        # Set image cls
        self.image_cls = Image if not self.circular else CircularImage

        # Add children: image plus both placeholders, always present.
        self.add_children([
            self.build_image(),

            self.build_placeholder(
                self.unset_placeholder,
                role=self.UNSET_ROLE,
                visible=not self.source,
            ),

            self.build_placeholder(
                self.error_placeholder,
                role=self.ERROR_ROLE,
                visible=False,
            ),
        ])

    def build_image(self) -> Image:
        """
        Build the underlying image, wired so `load`/`error` events toggle
        which sibling placeholder is visible. Works whether the source is
        set at construction time or assigned later by other code.

        Returns:
            An Image component with load/error handoff attached.
        """
        image_props = {
            "onload": (
                "this.style.display='block';"
                f"this.parentElement.querySelector('[data-role={self.UNSET_ROLE}]').style.display='none';"
                f"this.parentElement.querySelector('[data-role={self.ERROR_ROLE}]').style.display='none';"
            ),
            "onerror": (
                "this.style.display='none';"
                f"this.parentElement.querySelector('[data-role={self.ERROR_ROLE}]').style.display='flex';"
                f"this.parentElement.querySelector('[data-role={self.UNSET_ROLE}]').style.display='none';"
            ),
        }

        if self.image_id:
            image_props["id"] = self.image_id

        if self.lazy:
            image_props["loading"] = "lazy"

        image_kwargs = {
            "alt": self.kwargs.get("alt", ""),
            "style": {
                "width": "100%",
                "height": "100%",
                "object-fit": self.fit,
                "display": "block" if self.source else "none",
            },
            "props": image_props,
        }

        # Omit `source` entirely rather than passing "" — an empty src
        # attribute is treated by some browsers as a reference to the
        # current page and can fire spurious load/error events.
        if self.source:
            image_kwargs["source"] = self.source

        return self.image_cls(**image_kwargs)

    def build_placeholder(self, placeholder, role: str, visible: bool) -> Container:
        """
        Build a placeholder slot, wrapping a URL string in an Image or
        rendering a given component directly.

        Args:
            placeholder:
                A URL string or a component instance.

            role:
                Either UNSET_ROLE or ERROR_ROLE, used to target this
                placeholder from the image's load/error handlers.

            visible:
                Whether this placeholder should be shown initially.

        Returns:
            A Container holding the resolved placeholder content.
        """
        if placeholder and isinstance(placeholder, str):
            content = [
                self.image_cls(
                    source=placeholder,
                    alt=self.kwargs.get("alt", ""),
                    style={"width": "100%", "height": "100%", "object-fit": self.fit},
                ),
            ]

        else:
            content = [placeholder]

        return Container(
            props={"data-role": role},
            style={
                "display": "flex" if visible else "none",
                "align-items": "center",
                "justify-content": "center",
                "width": "100%",
                "height": "100%",
            },
            children=content,
        )


class CircularSmartImage(SmartImage):
    """
    A themeable circular image that falls back to a placeholder when unset or on
    network error. The placeholder can be a URL string or another component
    (e.g. an icon, a Label, a Spinner).

    Required Props:
    - (none — src is optional; placeholder covers the unset case)

    Optional Props:
    - source: Image source URL. If omitted, the placeholder shows immediately.
    - placeholder: Fallback (URL string or component) for both unset src
      and network error, unless overridden below. If neither this nor
      unset_placeholder/error_placeholder is given, a plain
      SmartImagePlaceholder is used instead of showing nothing.
    - unset_placeholder: Shown when src is empty/None. Overrides placeholder.
    - error_placeholder: Shown when the image fails to load. Overrides placeholder.
    - alt: Alt text for the image.
    - fit: object-fit value, defaults to cover.
    - height: Container height (CSS value).
    - width: Container width (CSS value).
    - image_id: Optional id applied to the underlying <img>, so calling code can
          update `.src` later (e.g. `document.getElementById(image_id).src = url`)
          and have the placeholder swap react live.
    - lazy: If True, sets the native `loading="lazy"` attribute so the
          browser defers fetching until the image nears the viewport. Defaults
          to False (eager). Only affects the primary image, not placeholders.

    Usage:
    ```python
    CircularSmartImage(source="/img/avatar.png", placeholder="/img/default.png")
    CircularSmartImage(source="/img/hero.png", placeholder=Icon(name="broken-image"))
    CircularSmartImage(unset_placeholder=Spinner(), error_placeholder="/img/broken.png")
    ```

    Notes:
        The image, unset placeholder, and error placeholder are all rendered as
            siblings up front. Visibility is then driven entirely by the <img>'s own
            `load`/`error` events, so changing `.src` on the image element at any
            point after mount (empty -> url, url -> a different url, etc.) is
            reflected automatically without re-rendering this component.
    """

    def on_create(self):
        """
        Build the circular image plus both placeholders, wiring load/error handlers
        so visibility reacts live to source changes.
        """
        self.kwargs["circular"] = True
        super().on_create()
