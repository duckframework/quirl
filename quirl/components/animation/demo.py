"""
Standalone animation demo component for any Duck component.

Wraps any component and renders it with CSS-animated state transitions.
Output is pure HTML/CSS/JS — no WebSocket, no Python runtime, no
inheritance required on the wrapped component.
"""

import json

from duck.html.components.container import Container
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph
from duck.html.components.script import Script
from duck.html.components.style import Style

from quirl.theme import Theme


# Action verbs the client-side step runner knows how to perform
SUPPORTED_ACTIONS = {"click", "input", "toggle_class", "focus", "scroll_into_view"}


class Demo(Container):
    """
    Wraps any component and renders it with animated state transitions.

    Components that have nothing to demonstrate beyond "here's what it
    looks like" should pass no steps at all — Demo then renders a plain,
    still preview with no fake cursor or click theater. The cursor/click
    machinery only builds when at least one step defines a real action.

    Required Props:
    - component: The component to demonstrate.

    Optional Props:
    - steps: List of animation steps. Leave empty/omitted for a static
        preview. Each step is a dict with:
            - `delay` (int, required): Milliseconds before the next step.
            - `cursor` (dict, optional): Either `{"top": "50%", "left": "50%"}`, positioned relative
                to the preview row (not the whole card), or `{"target": "css-selector"}` to center
                the cursor on a matched element within the stage. When
                `target` is given, no other keys are allowed. Omit
                `cursor` entirely to hide the cursor for that step.
            - `target` (str, optional): CSS selector relative to the
                demo, used for both the highlight pulse and any action.
            - `action` (dict, optional): What to do to `target`.
                `{"type": "click"}`
                `{"type": "input", "value": "hello"}`
                `{"type": "toggle_class", "class_name": "is-active"}`
                `{"type": "focus"}`
                `{"type": "scroll_into_view"}`
                Each supports an optional `delay` (ms before firing,
                defaults to 400).
    - title: Heading above the demo.
    - description: Optional text below the heading.
    - id: Stable DOM id. Auto-generated if omitted.
    """
    
    docs_preview_kwargs = None
    
    docs_no_preview_reason = (
        "Demo requires a component to wrap and isn't meant to preview itself."
    )

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

        # An animation layer only earns its place when a step actually
        # does something — cursor-only wandering with no action is just
        # confusing click theater on components with nothing to click
        self.has_animation = any(step.get("action") for step in self.steps)

        # Apply demo container base styles as a rounded, elevated card
        self.style.update({
            "border": f"1px solid {Theme.current.border_color}",
            "border-radius": Theme.current.border_radius,
            "padding": "clamp(16px, 4vw, 24px)",
            "overflow": "hidden",
            "background": Theme.current.surface_elevated_color,
            "box-shadow": Theme.current.shadow_sm,
            "max-width": "100%",
            "box-sizing": "border-box",
            "display": "flex",
            "flex-direction": "column",
            "gap": "4px",
        })

        # Add header content
        if self.demo_title:
            self.add_child(Heading(
                type="h4",
                text=self.demo_title,
                style={"margin": "0", "color": Theme.current.text_color},
            ))

        if self.demo_description:
            self.add_child(Paragraph(
                text=self.demo_description,
                style={"margin": "0", "color": Theme.current.muted_text_color},
            ))

        # Add the component being demonstrated, centered in its own row.
        # This row is the coordinate space cursor steps are relative to.
        preview_children = [self.demo_component]

        if self.has_animation:
            preview_children.append(self.build_cursor())

        self.add_child(Container(
            id=f"{self.demo_id}-stage",
            style={
                "position": "relative",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "flex-wrap": "wrap",
                "gap": "12px",
                "min-height": "72px",
                "width": "100%",
                "box-sizing": "border-box",
                "padding": "8px 0",
            },
            children=preview_children,
        ))

        # Add animation support layers only when there's something to animate
        if self.has_animation:
            self.add_child(self.build_styles())
            self.add_child(self.build_script())

    def validate_steps(self) -> None:
        """
        Ensure every step has a delay, and every action has a known type.

        Raises:
            ValueError: If a step is malformed, or an action's type isn't
                one of SUPPORTED_ACTIONS.
        """
        for idx, step in enumerate(self.steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step {idx} must be a dict, got {type(step).__name__}")

            if "delay" not in step:
                raise ValueError(f"Step {idx} is missing required 'delay' key")

            cursor = step.get("cursor")

            if cursor is not None:
                if not isinstance(cursor, dict):
                    raise ValueError(f"Step {idx}'s cursor must be a dict")

                if "target" in cursor and set(cursor.keys()) != {"target"}:
                    raise ValueError(
                        f"Step {idx}'s cursor with 'target' must not include "
                        f"other keys"
                    )

            action = step.get("action")

            if action is not None:
                if not isinstance(action, dict) or "type" not in action:
                    raise ValueError(f"Step {idx}'s action must be a dict with a 'type' key")

                if action["type"] not in SUPPORTED_ACTIONS:
                    raise ValueError(
                        f"Step {idx}'s action type '{action['type']}' is not supported. "
                        f"Use one of: {', '.join(sorted(SUPPORTED_ACTIONS))}"
                    )

                if action["type"] != "click" and "target" not in step:
                    raise ValueError(f"Step {idx} has an action but no 'target' to apply it to")

    def build_cursor(self) -> Container:
        """
        Build the fake mouse cursor element, scoped to the preview stage.

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
                "transform": "translate(-50%, -50%)",
            },
        )

    def build_styles(self) -> Style:
        """
        Generate scoped CSS for the highlight pulse effect.

        Returns:
            A Style component with demo-specific keyframes.
        """
        css = f"""
        #{self.demo_id}-stage .demo-highlight {{
          animation: demo-pulse 0.8s ease-in-out;
        }}

        @keyframes demo-pulse {{
          0%, 100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }}
          50% {{ box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }}
        }}

        @media (max-width: 480px) {{
          #{self.demo_id} {{
            padding: 16px;
          }}
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

            const stage = document.getElementById('{self.demo_id}-stage');
            const cursor = document.getElementById('{self.demo_id}-cursor');
            let index = 0;

            function runAction(target, action) {{
                const fireDelay = action.delay ?? 400;

                setTimeout(() => {{
                    switch (action.type) {{
                        case 'click':
                            if (target) target.click();
                            break;
                        case 'input':
                            if (target) {{
                                target.focus();
                                target.value = action.value ?? '';
                                target.dispatchEvent(new Event('input', {{bubbles: true}}));
                            }}
                            break;
                        case 'toggle_class':
                            if (target && action.class_name) {{
                                target.classList.toggle(action.class_name);
                            }}
                            break;
                        case 'focus':
                            if (target) target.focus();
                            break;
                        case 'scroll_into_view':
                            if (target) {{
                                target.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            }}
                            break;
                        default:
                            break;
                    }}
                }}, fireDelay);
            }}

            function positionCursor(step) {{
                if (!cursor) return;

                if (step.cursor && step.cursor.target) {{
                    const el = stage.querySelector(step.cursor.target);

                    if (el) {{
                        const stageRect = stage.getBoundingClientRect();
                        const elRect = el.getBoundingClientRect();

                        cursor.style.top = `${{elRect.top - stageRect.top + elRect.height / 2}}px`;
                        cursor.style.left = `${{elRect.left - stageRect.left + elRect.width / 2}}px`;
                        cursor.style.opacity = '1';
                    }} else {{
                        cursor.style.opacity = '0';
                    }}
                }} else if (step.cursor) {{
                    cursor.style.top = step.cursor.top || '50%';
                    cursor.style.left = step.cursor.left || '50%';
                    cursor.style.opacity = '1';
                }} else {{
                    cursor.style.opacity = '0';
                }}
            }}

            function applyStep(step) {{
                positionCursor(step);

                const target = step.target ? stage.querySelector(step.target) : null;

                if (step.target && target) {{
                    target.classList.add('demo-highlight');
                    setTimeout(() => target.classList.remove('demo-highlight'), 800);
                }}

                if (step.action) {{
                    runAction(target, step.action);
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
