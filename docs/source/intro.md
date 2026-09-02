# Introduction

Quirl is a reusable UI component library for [Duck Framework](https://duckframework.com)'s Lively reactive system.

It provides ready-to-use, themeable components that can be built entirely in Python. There is no separate frontend toolchain, JavaScript bundler, or build step for your UI logic.

Quirl is designed around three main ideas:

- **Themeable components** — Shared design tokens are provided through CSS custom properties, allowing components to inherit a consistent theme.
- **Reusable components** — Build interfaces from existing Quirl components or create your own components on top of Duck's built-in components.
- **Self-documenting demos** — Components can include their own usage documentation and interactive demo configuration, which Quirl can turn into static documentation.

Quirl also includes a static demo system that can generate animated component showcases without requiring a running Python server or WebSocket connection. This makes it possible to deploy component documentation to static hosting such as GitHub Pages or Netlify.

> **Prerequisite:** Quirl requires [Duck Framework](https://duckframework.com) and Python 3.10 or later.

---

## Installation

Install stable Quirl version using pip:

```bash
pip install quirl
```

Install the latest version using pip:

```bash
pip install git+https://github.com/duckframework/quirl.git
```

Quirl requires:

- Python **3.10+**
- `duckframework>=2.3.1`

Once installed, you can import Quirl components and utilities directly from your Python application.

---

## Getting Started

This guide shows the basic setup for using Quirl in a Duck application.

### 1. Add Quirl's Global Styles

```{important} Required: Global Styles

Before using any Quirl component, add "quirl_global_styles()" to your page's "<head>". 
Quirl components rely on these global styles for their default appearance and behavior.
```

```python
from quirl.styles import quirl_global_styles

page.add_to_head(quirl_global_styles())
```

```{important}
Important: This only needs to be added once per page. It is required whenever you use Quirl components.
```

### 2. Define a Theme

Quirl uses themes to provide shared design tokens across components.

```python
from quirl.theme import Theme

dark = Theme(
    name="dark",
    accent_color="#F5C842",
    surface_color="#111318",
)

Theme.current = dark
```

Components automatically use the active theme unless their properties are explicitly overridden.

### 3. Use a Component

You can use Quirl components alongside Duck's built-in components.

For example:

```python
from quirl.components import Badge

badge = Badge(text="Getting started", variant="success")
```

Render the component as part of your page:

```python
page.add_to_body(badge)
```

Because Quirl components are Duck components, they work with Lively's reactive system and can be composed with other Duck components.

### 4. Create Your Own Component

Quirl is not limited to its built-in components. You can extend Duck's existing components and apply your own styling and behavior.

```python
from duck.html.components.label import Label

class StatusLabel(Label):
    """
    A themed label for displaying status text.

    Usage:
    ```python
    StatusLabel(text="Active", color="green")
    ```

    Required Props:
    - text: Display text
    
    Optional Props:
    - color: The text color for the label
    """
    
    # Preview kwargs for the demo
    docs_preview_kwargs = {"text": "Preview", "color": "#3b82f6"}
    
    # Demo animation steps
    docs_animation_steps = [
        {"delay": 1000, "cursor": {"target": "label"}},
        {"delay": 500, "target": "span", "click": True},
    ]

    def on_create(self):
        super().on_create()
        
        # Update style
        self.style.update({
            "border-radius": "9999px",
            "padding": "4px 12px",
            "font-weight": "500",
        })
```

Your custom component can then be used like any other Duck component:

```python
status = StatusLabel(
    text="Active",
    color="green",
)

page.body.add(status)
```

## 5. Add Static Component Demos

Quirl also provides `Demo` for creating static component showcases.

```python
from duck.html.components.button import Button
from quirl.components import Demo

button_demo = Demo(
    component=Button(
        text="Submit",
        bg_color="blue",
        color="white",
    ),
    steps=[
        {"delay": 1000, "cursor": {"target": "button"}},
        {"delay": 500, "target": "button", "click": True},
        {"delay": 2000},
    ],
    title="Button",
)
```

A demo can be rendered to static HTML:

```python
html = button_demo.render()
```

The resulting output can be deployed to a static host such as GitHub Pages or Netlify. No Python runtime or WebSocket connection is required for the generated demo.

## What's Next?

You can now start building with Quirl components.

- Browse the **Components** section to see available components and their properties.
- Read the **Theming** guide to customize Quirl's design system.
- Learn about **Demos** to create animated component showcases.
- See **Custom Components** to build your own reusable Quirl components.
