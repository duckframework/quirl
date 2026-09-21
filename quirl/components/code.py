"""
A theme-colored, horizontally-scrollable code block.
"""

import html

from duck.html.components.code import (
    CodeBlock as BaseCodeBlock,
    EditableCodeBlock as BaseEditableCodeBlock,
)

from quirl.theme import Theme


def get_default_style() -> dict:
    """
    Returns the codeblock default style.'
    """
    return {
        "margin": "0",
        "padding": "12px 16px",
        "color": Theme.current.text_color,
        "border": f"1px solid {Theme.current.border_color}",
        "border-radius": Theme.current.border_radius_sm,
        "font-family": "monospace",
        "font-size": "0.85rem",
        "line-height": "1.5",
        "max-width": "100%",
        "box-sizing": "border-box",
        "-webkit-overflow-scrolling": "touch",
    }
    

class CodeBlock(BaseCodeBlock):
    """
    A theme-colored, monospace code block with horizontal scroll.
    
    Required Props:
        - code (str):
              The code text to display inside the code block.
    
    Optional Props:
        - language (str):
              Label shown in the header, e.g. "python".
              Also applied to the inner `<code>` tag as a `language-{language}` class.
        
        - filename (str):
            Filename shown in the header, e.g. "main.py".
        
        - collapsible (bool):
                Renders a fixed-height preview with a bottom fade and a labeled 
                toggle beneath the code when True.
                
        - collapsed_height (str):
                Preview height while collapsed, e.g. "320px". Defaults to a
                height that reads as a genuine preview rather than a sliver.
        
        - expand_label (str):
                Footer label shown while collapsed. Defaults to "Show more".
    
        - ollapse_label (str):
                Footer label shown while expanded. Defaults to "Show less".
                
        - code_props (dict):
                Extra props applied to the `<code>` tag.
                
        - code_style (dict):
                Extra styles applied to the `<code>` tag.
                
        - disable_copy_button (bool):
                Hides the copy button when True.
                
        - idle_icon (str):
                Raw svg shown on the copy button by default.
        
        - success_icon (str):
                Raw svg shown after a successful copy.
        
        - chevron_icon (str):
                Raw svg shown in the collapse footer.
            
    Usage:
    ```python
    CodeBlock(code="Button(text='Click me')", language="python")
    ```
    """
    
    docs_preview_kwargs = {"code": "Button(text='Click me')"}
    
    def on_create(self):
        """
        Build the code block with theme-aware, escaped content.
        """
        super().on_create()
        
        # Apply readable, theme-colored code block styles
        self.style.update(get_default_style())


class EditableCodeBlock(BaseEditableCodeBlock):
    """
    An editable theme-colored, monospace code block with horizontal scroll.
    
    Required Props:
        - code (str):
              The code text to display inside the code block.
    
    Optional Props:
        - language (str):
              Label shown in the header, e.g. "python".
              Also applied to the inner `<code>` tag as a `language-{language}` class.
        
        - filename (str):
            Filename shown in the header, e.g. "main.py".
        
        - collapsible (bool):
                Renders a fixed-height preview with a bottom fade and a labeled 
                toggle beneath the code when True.
                
        - collapsed_height (str):
                Preview height while collapsed, e.g. "320px". Defaults to a
                height that reads as a genuine preview rather than a sliver.
        
        - expand_label (str):
                Footer label shown while collapsed. Defaults to "Show more".
    
        - ollapse_label (str):
                Footer label shown while expanded. Defaults to "Show less".
                
        - code_props (dict):
                Extra props applied to the `<code>` tag.
                
        - code_style (dict):
                Extra styles applied to the `<code>` tag.
                
        - disable_copy_button (bool):
                Hides the copy button when True.
                
        - idle_icon (str):
                Raw svg shown on the copy button by default.
        
        - success_icon (str):
                Raw svg shown after a successful copy.
        
        - chevron_icon (str):
                Raw svg shown in the collapse footer.
            
    Usage:
    ```python
    CodeBlock(code="Button(text='Click me')", lanuage="python")
    ```
    """
    
    docs_preview_kwargs = {"code": "Button(text='Click me')"}
    
    def on_create(self):
        """
        Build the code block with theme-aware, escaped content.
        """
        super().on_create()
        
        # Apply readable, theme-colored code block styles
        self.style.update(get_default_style())
