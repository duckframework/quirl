"""
Assembles complete documentation for any Duck component.
"""

from duck.html.components.container import Container, FlexContainer
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph

from quirl.components.animation.demo import Demo
from quirl.components.badge import Badge
from quirl.components.code_block import CodeBlock
from quirl.components.divider import Divider
from quirl.theme import Theme


class Documentor(Container):
    """
    Stitches together full documentation for any Duck component.

    Combines the docstring description, a props reference, a usage code
    block, and an animated live preview into a single styled
    documentation card.

    Required Props:
    - component_cls: The component class to document. Required.

    Optional Props:
    - title: Optional heading text. Defaults to the class name.
    - id: Stable DOM id for the documentation card.
    """
    
    docs_preview_kwargs = None
    
    docs_no_preview_reason = (
        "Documentor requires a component_cls to document and isn't "
        "meant to preview itself."
    )
    
    def on_create(self):
        """
        Build the documentation card from the component's docstring.
        """
        super().on_create()

        # Read configuration at construction time
        self.component_class = self.get_kwarg_or_raise("component_cls")
        self.doc_title = self.kwargs.get("title", self.component_class.__name__)
        self.doc_id = self.kwargs.get("id", f"{self.component_class.__name__.lower()}-docs")

        self.id = self.doc_id

        # Apply container base styles as an elevated, responsive card
        self.style.update({
            "padding": "clamp(20px, 5vw, 32px)",
            "gap": "20px",
            "display": "flex",
            "flex-direction": "column",
            "background": Theme.current.surface_color,
            "border": f"1px solid {Theme.current.border_color}",
            "border-radius": Theme.current.border_radius,
            "max-width": "720px",
            "width": "100%",
            "box-sizing": "border-box",
            "font-family": Theme.current.font_family,
            "animation": "quirl-fade-in 0.3s ease-out",
        })

        # Assemble documentation sections, separated by dividers
        self.add_children([
            self.build_header(),
            self.build_description(),
            Divider(),
            self.build_props_section(),
            Divider(),
            self.build_usage_section(),
            Divider(),
            self.build_preview_section(),
        ])

    def build_header(self) -> Container:
        """
        Build the component name heading with a category badge.

        Returns:
            A Container with the title and a small "Component" badge.
        """
        return Container(
            style={
                "display": "flex",
                "align-items": "center",
                "gap": "10px",
                "flex-wrap": "wrap",
            },
            children=[
                Heading(
                    type="h2",
                    text=self.doc_title,
                    style={"margin": "0", "color": Theme.current.text_color},
                ),
                Badge(text="Component", variant="accent", size="sm"),
            ],
        )

    def build_description(self) -> Paragraph:
        """
        Return the first paragraph of the docstring as a description.

        Returns:
            A Paragraph with the description text, or an empty Paragraph
            if no docstring is present.
        """
        doc = self.component_class.__doc__ or ""
        first_line = doc.strip().split("\n")[0] if doc else ""

        return Paragraph(
            text=first_line,
            style={"margin": "0", "color": Theme.current.muted_text_color, "line-height": "1.5"},
        )

    def build_props_section(self) -> Container:
        """
        Parse Required Props and Optional Props from the docstring.

        Returns:
            A Container with headings and prop rows for each section
            found in the docstring.
        """
        doc = self.component_class.__doc__ or ""
        lines = doc.split("\n")

        required = []
        optional = []
        section = None

        # Parse prop lines from the docstring
        for line in lines:
            stripped = line.strip()

            if stripped == "Required Props:":
                section = "required"
                continue

            elif stripped == "Optional Props:":
                section = "optional"
                continue

            elif stripped.startswith("```") or stripped.startswith("Usage:"):
                section = None
                continue

            if section and stripped.startswith("-"):
                prop_text = stripped.lstrip("- ").strip()

                if section == "required":
                    required.append(prop_text)

                elif section == "optional":
                    optional.append(prop_text)

        children = []

        # Add required props block
        if required:
            children.append(self.build_prop_group("Required Props", required, "warning"))

        # Add optional props block
        if optional:
            children.append(self.build_prop_group("Optional Props", optional, "neutral"))

        return Container(
            style={"display": "flex", "flex-direction": "column", "gap": "16px"},
            children=children,
        )

    def build_prop_group(self, label: str, props: list, badge_variant: str) -> Container:
        """
        Build a single labeled group of prop rows.

        Args:
            label: Section heading text, e.g. "Required Props".
            props: List of raw "name: description" prop lines.
            badge_variant: Badge variant used for the section label.

        Returns:
            A Container with the section heading and prop rows.
        """
        return Container(
            style={"display": "flex", "flex-direction": "column", "gap": "8px"},
            children=[
                Container(
                    style={"display": "flex", "align-items": "center", "gap": "8px"},
                    children=[
                        Heading(
                            type="h4",
                            text=label,
                            style={"margin": "0", "font-size": "0.9rem", "color": Theme.current.text_color},
                        ),
                        Badge(text=str(len(props)), variant=badge_variant, size="sm"),
                    ],
                ),
                Container(
                    style={"display": "flex", "flex-direction": "column", "gap": "6px"},
                    children=[self.build_prop_row(prop) for prop in props],
                ),
            ],
        )

    def build_prop_row(self, prop_text: str) -> Container:
        """
        Build a single prop row with the name emphasized as code.

        Args:
            prop_text: Raw "name: description" text from the docstring.

        Returns:
            A Container styled as a row inside a props list.
        """
        name, _, description = prop_text.partition(":")

        return Container(
            style={
                "display": "flex",
                "flex-wrap": "wrap",
                "gap": "8px",
                "padding": "8px 12px",
                "border-radius": Theme.current.border_radius_sm,
                "background": Theme.current.surface_elevated_color,
            },
            children=[
                Paragraph(
                    text=name.strip(),
                    style={
                        "margin": "0",
                        "font-family": "monospace",
                        "font-weight": "600",
                        "color": Theme.current.accent_color,
                    },
                ),
                Paragraph(
                    text=description.strip(),
                    style={"margin": "0", "color": Theme.current.muted_text_color},
                ),
            ],
        )

    def build_usage_section(self) -> Container:
        """
        Build the Usage code block from the same kwargs driving the Demo.

        Sourcing usage from ``docs_preview_kwargs`` (rather than a
        hand-written docstring snippet) guarantees the code shown here
        always matches what the live preview actually renders. Falls
        back to parsing a ```python block from the docstring only for
        components that opt out of a preview entirely.

        Returns:
            A Container with a heading and code block, or an empty
            Container if there's nothing to show.
        """
        preview_kwargs = getattr(self.component_class, "docs_preview_kwargs", {})

        if preview_kwargs is not None:
            usage_code = self.format_usage_code(preview_kwargs)
        else:
            usage_code = self.extract_docstring_usage()

        if not usage_code:
            return Container(
                style={"display": "flex", "flex-direction": "column", "gap": "8px"},
                children=[
                    Heading(
                        type="h4",
                        text="Usage",
                        style={"margin": "0", "font-size": "0.9rem", "color": Theme.current.text_color},
                    ),
                    Container(
                        text="Usage code not available",
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "padding": "32px 16px",
                            "border-radius": Theme.current.border_radius,
                            "border": f"1px dashed {Theme.current.border_color}",
                            "color": Theme.current.muted_text_color,
                            "font-size": "0.875rem",
                            "text-align": "center",
                        },
                    ),
                ],
            )

        return FlexContainer(
            style={"flex-direction": "column", "gap": "8px"},
            children=[
                Heading(
                    type="h4",
                    text="Usage",
                    style={"margin": "0", "font-size": "0.9rem", "color": Theme.current.text_color},
                ),
                Container(
                    style={
                        "border-radius": Theme.current.border_radius_sm,
                        "overflow": "hidden",
                        "max-width": "100%",
                    },
                    children=[CodeBlock(code=usage_code)],
                ),
            ],
        )

    def format_usage_code(self, kwargs: dict) -> str:
        """
        Render a constructor call string from the exact kwargs used to
        build the live preview.

        Args:
            kwargs: The component's docs_preview_kwargs.

        Returns:
            A Python-formatted constructor call, e.g. ``Badge(text='Beta')``.
        """
        class_name = self.component_class.__name__

        if not kwargs:
            return f"{class_name}()"

        args = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        single_line = f"{class_name}({args})"

        if len(single_line) <= 60:
            return single_line

        lines = [f"{class_name}("]

        for key, value in kwargs.items():
            lines.append(f"    {key}={value!r},")

        lines.append(")")
        return "\n".join(lines)

    def extract_docstring_usage(self) -> str:
        """
        Extract a ```python code block from the docstring.

        Only used as a fallback for components with no preview kwargs
        to generate usage from.

        Returns:
            The extracted code, or an empty string if none is found.
        """
        doc = self.component_class.__doc__ or ""
        usage_lines = []
        in_code = False

        for line in doc.split("\n"):
            if "```python" in line:
                in_code = True
                continue

            elif "```" in line and in_code:
                in_code = False
                continue

            if in_code:
                usage_lines.append(line)

        return "\n".join(usage_lines)

    def build_preview_section(self):
        """
        Build the live preview with animated demo, or a placeholder.

        A component opts out of a preview by setting the class attribute
        ``docs_preview_kwargs = None`` (as opposed to ``{}``, which means
        "no kwargs needed but a preview is still wanted"). Optionally set
        ``docs_no_preview_reason`` for a specific explanation.

        Returns:
            A Demo component with the live preview and animation, or a
            Container explaining why no preview is available.
        """
        preview_kwargs = getattr(self.component_class, "docs_preview_kwargs", {})

        if preview_kwargs is None:
            return self.build_no_preview_placeholder()

        animation_steps = getattr(self.component_class, "docs_animation_steps", [])
        instance = self.component_class(**preview_kwargs)

        return Demo(
            component=instance,
            steps=animation_steps,
            title="Live Preview",
        )

    def build_no_preview_placeholder(self) -> Container:
        """
        Build the placeholder shown when a component opts out of a preview.

        Returns:
            A dashed-border Container explaining the lack of a preview.
        """
        reason = getattr(
            self.component_class,
            "docs_no_preview_reason",
            "No live preview available for this component.",
        )

        return FlexContainer(
            style={"flex-direction": "column", "gap": "8px"},
            children=[
                Heading(
                    type="h4",
                    text="Live Preview",
                    style={"margin": "0", "font-size": "0.9rem", "color": Theme.current.text_color},
                ),
                Container(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "padding": "32px 16px",
                        "border-radius": Theme.current.border_radius,
                        "border": f"1px dashed {Theme.current.border_color}",
                        "color": Theme.current.muted_text_color,
                        "font-size": "0.875rem",
                        "text-align": "center",
                    },
                    children=[Paragraph(text=reason, style={"margin": "0"})],
                ),
            ]
        )
