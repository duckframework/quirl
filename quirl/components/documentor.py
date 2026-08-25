"""
quirl.components.documentor
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Assembles complete documentation for any Duck component.
"""

from duck.html.components.container import Container
from duck.html.components.card import Card
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph
from duck.html.components.code import Code

from quirl.components.animation.demo import Demo


class Documentor(Container):
    """
    Stitches together full documentation for any Duck component.

    Combines markdown docstring, props reference, usage code block,
    and animated live preview into a single documentation card.

    Required Props:
    - component: The component class to document. Required.
    
    Optional Props:
    - title: Optional heading text. Defaults to the class name.
    - id: Stable DOM id for the documentation card.
    """
    
    def on_create(self):
        """
        Build the documentation card from the component's docstring.
        """
        super().on_create()

        # Read configuration at construction time
        self.component_class = self.get_kwarg_or_raise("component")
        self.doc_title = self.kwargs.get("title", self.component_class.__name__)
        self.doc_id = self.kwargs.get("id", f"{self.component_class.__name__.lower()}-docs")

        # Apply container base styles
        self.style.update({
            "padding": "32px",
            "gap": "24px",
            "display": "flex",
            "flex-direction": "column",
        })

        # Assemble documentation sections
        self.add_children([
            self.build_header(),
            self.build_description(),
            self.build_props_section(),
            self.build_usage_section(),
            self.build_preview_section(),
        ])

    def build_header(self) -> Heading:
        """
        Return the component name heading.

        Returns:
            A Heading component with the documentation title.
        """
        return Heading(type="h2", text=self.doc_title)

    def build_description(self) -> Paragraph:
        """
        Return the first paragraph of the docstring as a description.

        Returns:
            A Paragraph with the description text, or an empty Paragraph
            if no docstring is present.
        """
        doc = self.component_class.__doc__ or ""
        first_line = doc.strip().split("\n")[0] if doc else ""
        
        # Return the final paragraph
        return Paragraph(text=first_line)

    def build_props_section(self) -> Container:
        """
        Parse Required Props and Optional Props from the docstring.

        Returns:
            A Container with headings and bullet paragraphs for each
            prop section found in the docstring.
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
            children.append(Heading(type="h4", text="Required Props"))
            
            for prop in required:
                children.append(Paragraph(text=f"• {prop}"))

        # Add optional props block
        if optional:
            children.append(Heading(type="h4", text="Optional Props"))
            
            for prop in optional:
                children.append(Paragraph(text=f"• {prop}"))

        # Return final container
        return Container(children=children)

    def build_usage_section(self) -> Container:
        """
        Extract the Usage code block from the docstring.

        Returns:
            A Container with a heading and Code component, or an empty
            Container if no usage block is found.
        """
        doc = self.component_class.__doc__ or ""

        # Extract code between ```python and ```
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

        if not usage_lines:
            return Container()

        # Usage code
        usage_code = "\n".join(usage_lines)

        return Container(
            children=[
                Heading(type="h4", text="Usage"),
                Code(text=usage_code),
            ],
        )

    def build_preview_section(self) -> Demo:
        """
        Build the live preview with animated demo.

        Reads docs_preview_kwargs and docs_animation_steps from the
        component class, instantiates the component, and wraps it in
        a Demo container.

        Returns:
            A Demo component with the live preview and animation.
        """
        preview_kwargs = getattr(self.component_class, "docs_preview_kwargs", {})
        animation_steps = getattr(self.component_class, "docs_animation_steps", [])
        
        # Build instance
        instance = self.component_class(**preview_kwargs)

        return Demo(
            component=instance,
            steps=animation_steps,
            title="Live Preview",
        )
