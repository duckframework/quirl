"""
A theme-colored, horizontally-scrollable code block.
"""

import html

from duck.html.components.container import Container

from quirl.theme import Theme


class CodeBlock(Container):
    """
    A theme-colored, monospace code block with horizontal scroll.

    Renders as a <pre> element with escaped content, so it never depends
    on an external syntax-highlighter stylesheet being loaded.

    Usage:
    ```python
    CodeBlock(code="Button(text='Click me')")
    ```

    Required Props:
    - code: The raw code text to display.
    """
    
    docs_preview_kwargs = None
    
    docs_no_preview_reason = (
        "CodeBlock requires code to display and isn't meant to preview itself."
    )

    def get_element(self):
        """
        Return the HTML tag for this component.

        Returns:
            The pre tag name, which preserves whitespace and line breaks.
        """
        return "pre"

    def on_create(self):
        """
        Build the code block with theme-aware, escaped content.
        """
        super().on_create()

        code_text = self.get_kwarg_or_raise("code")

        # Apply readable, theme-colored code block styles
        self.style.update({
            "margin": "0",
            "padding": "12px 16px",
            "background": Theme.current.surface_elevated_color,
            "color": Theme.current.text_color,
            "border": f"1px solid {Theme.current.border_color}",
            "border-radius": Theme.current.border_radius_sm,
            "font-family": "monospace",
            "font-size": "0.85rem",
            "line-height": "1.5",
            "overflow-x": "auto",
            "max-width": "100%",
            "box-sizing": "border-box",
            "-webkit-overflow-scrolling": "touch",
        })

        # Escape manually since <pre> content must stay as literal text,
        # including any <, >, & characters the code itself contains
        self.inner_html = html.escape(code_text)
