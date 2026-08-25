"""
Standalone animation demo component for any Duck component.

Wraps any component and renders it with CSS-animated state transitions.
Output is pure HTML/CSS/JS — no WebSocket, no Python runtime, no
inheritance required on the wrapped component.
"""

import json

from typing import Any, Dict, List

from duck.html.components.container import Container
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph
from duck.html.components.script import Script
from duck.html.components.style import Style


class Demo(Container):
    """
    Wraps any component and renders it with animated state transitions.

    Required Props:
    - component: The component to demonstrate.
    
    Optional Props:
    - steps: List of animation steps. Each step is a dict with:
            - ``delay`` (int): Milliseconds before next step.
            - ``cursor`` (dict, optional): ``{"top": "50%", "left": "50%"}``.
            - ``target`` (str, optional): CSS selector relative to demo.
            - ``click`` (bool, optional): Trigger click on target.
    - title: Heading above the demo.
    - description: Optional text below the heading.
    - id: Stable DOM id. Auto-generated if omitted.
    """
    
    def on_create(self):
        """
        Build the demo container with animated state transitions.
        """
        super().on_create()

        # Read configuration from kwargs at construction time
        self.demo_component = self.get_kwarg_or_raise("component")
        self.steps = self.kwargs.get("steps", [])
        self.demo_title = self.kwargs.get("title", "")
        self.demo_description = self.kwargs.get("description", "")
        self.demo_id = self.kwargs.get("id", f"demo-{self.uid}")
        
        # Validate step format
        self.validate_steps()

        # Apply demo container base styles
        self.style.update({
            "position": "relative",
            "border": "1px solid var(--theme-border)",
            "border-radius": "12px",
            "padding": "24px",
            "overflow": "hidden",
            "background": "var(--theme-surface)",
        })

        # Add header content
        if self.demo_title:
            self.add_child(Heading(type="h4", text=self.demo_title))

        if self.demo_description:
            self.add_child(Paragraph(text=self.demo_description))

        # Add the component being demonstrated
        self.add_child(self.demo_component)

        # Add animation layers
        self.add_child(self.build_cursor())
        self.add_child(self.build_styles())
        self.add_child(self.build_script())

    def validate_steps(self) -> None:
        """
        Ensure all animation steps have the required delay field.

        Raises:
            ValueError: If a step is missing ``delay`` or is not a dict.
        """
        for idx, step in enumerate(self.steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step {idx} must be a dict, got {type(step).__name__}")
            
            if "delay" not in step:
                raise ValueError(f"Step {idx} is missing required 'delay' key")

    def build_cursor(self) -> Container:
        """
        Build the fake mouse cursor element.

        Returns:
            A positioned Container acting as the cursor.
        """
        return Container(
            id=f"{self.demo_id}-cursor",
            klass="demo-cursor",
            style={
                "position": "absolute",
                "width": "20px",
                "height": "20px",
                "border-radius": "50%",
                "background": "rgba(59, 130, 246, 0.3)",
                "border": "2px solid #3b82f6",
                "pointer-events": "none",
                "z-index": "1000",
                "transition": "all 0.5s ease-in-out",
                "opacity": "0",
                "top": "50%",
                "left": "50%",
            },
        )

    def build_styles(self) -> Style:
        """
        Generate scoped CSS for the highlight pulse effect.

        Returns:
            A Style component with demo-specific keyframes.
        """
        css = f"""
        #{self.demo_id} .demo-highlight {{
          animation: demo-pulse 0.8s ease-in-out;
        }}

        @keyframes demo-pulse {{
          0%, 100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }}
          50% {{ box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }}
        }}
        """
        return Style(inner_html=css)

    def build_script(self) -> Script:
        """
        Generate the JS state machine that drives the animation steps.

        Returns:
            A Script component that cycles through steps on the client.
        """
        steps_json = json.dumps(self.steps)
        js = f"""
        (function() {{
            const steps = {steps_json};
            if (!steps.length) return;

            const container = document.getElementById('{self.demo_id}');
            const cursor = document.getElementById('{self.demo_id}-cursor');
            let index = 0;

            function applyStep(step) {{
                if (step.cursor && cursor) {{
                    cursor.style.top = step.cursor.top || '50%';
                    cursor.style.left = step.cursor.left || '50%';
                    cursor.style.opacity = '1';
                }} else if (cursor) {{
                    cursor.style.opacity = '0';
                }}

                if (step.target) {{
                    const target = container.querySelector(step.target);
                    if (target) {{
                        target.classList.add('demo-highlight');
                        setTimeout(
                            () => target.classList.remove('demo-highlight'),
                            800
                        );
                    }}
                }}

                if (step.click && step.target) {{
                    const target = container.querySelector(step.target);
                    if (target) {{
                        setTimeout(() => target.click(), 400);
                    }}
                }}
            }}

            function nextStep() {{
                const step = steps[index];
                applyStep(step);
                index = (index + 1) % steps.length;
                setTimeout(nextStep, step.delay || 2000);
            }}

            setTimeout(nextStep, 800);
        }})();
        """
        return Script(inner_html=js)
