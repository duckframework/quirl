"""
Shared CSS keyframes for Quirl components.

Several Quirl components (Spinner, Skeleton, Badge, Alert, Tag) reference
keyframe animations by name. Add this stylesheet once per page so those
animations actually run.

Usage:
```python
from quirl.styles import quirl_global_styles

page.add_to_head(quirl_global_styles())
```
"""

from duck.html.components.style import Style


# Keyframes shared by every animated Quirl component
GLOBAL_KEYFRAMES = """
@keyframes quirl-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes quirl-shimmer {
  0% { background-position: 150% 0; }
  100% { background-position: -150% 0; }
}

@keyframes quirl-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes quirl-scale-in {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes quirl-slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes quirl-bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
"""


def quirl_global_styles() -> Style:
    """
    Build the shared keyframes stylesheet for Quirl components.

    Returns:
        A Style component ready for page.add_to_head().
    """
    return Style(inner_html=GLOBAL_KEYFRAMES)
