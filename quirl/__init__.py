"""
Quirl — a modern, iOS-inspired premium component pack for Duck Framework.

Add the shared keyframes stylesheet once per page so animated components
work:

```python
from quirl.styles import quirl_global_styles

page.add_to_head(quirl_global_styles())
```
"""
from quirl.version import version


__author__ = "Brian Musakwa"
__email__ = "digreatbrian@gmail.com"
__version__ = version
