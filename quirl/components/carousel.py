"""
Quirl Carousel components — themeable, self-documenting carousels.

Two variants, since their driving logic differs enough to make one
class awkward: MarqueeCarousel loops continuously via rAF and never
"snaps" to a slide; SliderCarousel pages discretely and always has an
exact current index. Both share layout/theme plumbing via CarouselBase.
"""
from itertools import count

from duck.html.components.container import Container
from duck.html.components.script import Script
from duck.html.components.style import Style

from quirl.theme import Theme


class CarouselBase(Container):
    """
    Shared layout, theming, and dot-pagination for Quirl carousels.

    Not used directly — see MarqueeCarousel and SliderCarousel.
    
    Required Props:
        items (list[Component]): Slide content, one component per slide.

    Optional Props:
        gap (str): CSS gap between items. Defaults to the theme's spacing token.
        show_dots (bool): Whether to render position dots. Default True.
    """

    _id_counter = count(1)

    def on_create(self) -> None:
        super().on_create()
        
        # Get some kwargs
        self.items = self.get_kwarg_or_raise("items")
        self.gap = self.kwargs.get("gap", Theme.current.spacing)
        self.show_dots = self.kwargs.get("show_dots", True)
        
        # Set ID and class
        self.id = self.kwargs.get("id") or f"q-carousel-{next(self._id_counter)}"
        self.klass = f"{self.klass or ''} q-carousel".strip()
        
        # Update the style
        self.style.update({
            "display": "flex",
            "flex-direction": "column",
            "gap": Theme.current.spacing,
        })

    def build_track(self, children: list, extra_style: dict | None = None) -> Container:
        """
        Builds the horizontally scrollable row holding the slide items.

        Args:
            children: Item components (plus any duplicates) to render.
            extra_style: Style overrides layered on top of the base track style.

        Returns:
            A Container with native horizontal scroll.
        """
        style = {
            "display": "flex",
            "align-items": "stretch",
            "gap": self.gap,
            "overflow-x": "auto",
            "scrollbar-width": "none",
        }
        
        # Update style
        style.update(extra_style or {})
        
        # Return the final container
        return Container(id=f"{self.id}-track", klass="q-carousel-track", style=style, children=children)

    def build_dots(self) -> Container:
        """
        Builds one dot button per unique item.

        Returns:
            A Container row of dot buttons, styled and ready for the
            subclass's script to wire up click/active-state behavior.
        """
        dots = [
            Container(
                id=f"{self.id}-dot-{i}",
                klass="q-carousel-dot",
                props={"role": "button", "tabindex": "0", "aria-label": f"Go to slide {i + 1}"},
                style={
                    "width": "8px",
                    "height": "8px",
                    "border-radius": "999px",
                    "background": Theme.current.border_color,
                    "cursor": "pointer",
                    "transition": f"background {Theme.current.transition_fast}, transform {Theme.current.transition_fast}",
                },
            )
            for i in range(len(self.items))
        ]
        return Container(
            id=f"{self.id}-dots",
            klass="q-carousel-dots",
            style={"display": "flex", "justify-content": "center", "gap": "8px"},
            children=dots,
        )

    def build_dot_style(self) -> Style:
        """
        Returns the scoped stylesheet for the active-dot state.

        Returns:
            A Style component; subclasses append it alongside their own.
        """
        return Style(inner_html=f"""
            #{self.id} .q-carousel-dot.q-carousel-dot-active {{
                background: {Theme.current.accent_color};
                transform: scale(1.25);
            }}
            #{self.id} .q-carousel-track::-webkit-scrollbar {{
                display: none;
            }}
        """)


class MarqueeCarousel(CarouselBase):
    """
    Continuously auto-scrolling, seamlessly looping carousel.

    The item list is duplicated once internally so the loop wraps
    without a visible jump. Dots track the nearest item to the
    viewport's left edge and can be clicked to jump to that item;
    auto-scroll pauses on interaction and resumes after a delay.

    Required Props:
        items (list[Component]): Slide content, one component per slide.

    Optional Props:
        speed (float): Pixels scrolled per animation frame. Default 1.2.
        gap (str): CSS gap between items. Defaults to the theme's spacing token.
        show_dots (bool): Whether to render position dots. Default True.
        pause_on_interaction (bool): Pause auto-scroll on pointer/wheel/touch. Default True.
        resume_delay (int): Milliseconds of idle time before auto-scroll resumes. Default 2200.
        id (str): Element id. Auto-generated if omitted.

    Usage:
    ```python
    MarqueeCarousel(items=[Card(...) for c in collections], speed=1.5)
    ```
    """

    docs_preview_kwargs = {
        "items": [Container(text=f"Item {i}", style={"padding": "24px", "width": "160px"}) for i in range(4)],
        "speed": 1.2,
    }
    docs_animation_steps = [
        {"delay": 1200},
        {"delay": 800, "cursor": {"target": ".q-carousel-dot:nth-child(3)"}},
        {"delay": 400, "target": ".q-carousel-dot:nth-child(3)", "click": True},
        {"delay": 1500},
    ]

    def on_create(self) -> None:
        super().on_create()
        
        # Get some kwargs
        self.speed = self.kwargs.get("speed", 1.2)
        self.pause_on_interaction = self.kwargs.get("pause_on_interaction", True)
        self.resume_delay = self.kwargs.get("resume_delay", 2200)

        for i, item in enumerate(self.items):
            item.klass = f"{item.klass or ''} q-carousel-item".strip()
            item.props["data-index"] = str(i)

        # Initialize duplicates
        duplicates = []
        
        for i, item in enumerate(self.items):
            clone = item.clone() if hasattr(item, "clone") else item
            clone.props.update({"aria-hidden": "true", "tabindex": "-1"})
            duplicates.append(clone)

        # Build children
        children = [self.build_track(self.items + duplicates)]
        
        if self.show_dots:
            children.append(self.build_dots())

        # Add children
        self.add_children(children)
        
        # Add other children
        self.add_children([self.build_dot_style(), self.build_script()])

    def build_script(self) -> Script:
        """
        Returns the script driving continuous scroll, active-dot
        tracking, dot-click navigation, and pause/resume on interaction.

        Returns:
            A Script component with the marquee's runtime behavior.
        """
        return Script(inner_html=f"""
        (function () {{
          var track = document.getElementById('{self.id}-track');
          var dotsRow = document.getElementById('{self.id}-dots');
          if (!track) return;

          var SPEED = {self.speed};
          var paused = false;
          var resumeTimer = null;

          function pauseThenResume() {{
            paused = true;
            if (resumeTimer) clearTimeout(resumeTimer);
            resumeTimer = setTimeout(function () {{ paused = false; }}, {self.resume_delay});
          }}

          if ({str(self.pause_on_interaction).lower()}) {{
            ['pointerdown', 'wheel', 'touchstart'].forEach(function (evt) {{
              track.addEventListener(evt, pauseThenResume, {{ passive: true }});
            }});
          }}

          var originals = track.querySelectorAll('.q-carousel-item:not([aria-hidden])');
          var loopOffset = originals.length && track.querySelectorAll('.q-carousel-item')[originals.length]
            ? track.querySelectorAll('.q-carousel-item')[originals.length].offsetLeft - originals[0].offsetLeft
            : track.scrollWidth / 2;

          function updateActiveDot() {{
            if (!dotsRow) return;
            var closest = 0, closestDist = Infinity;
            originals.forEach(function (el, i) {{
              var dist = Math.abs(el.offsetLeft - track.scrollLeft);
              if (dist < closestDist) {{ closestDist = dist; closest = i; }}
            }});
            dotsRow.querySelectorAll('.q-carousel-dot').forEach(function (dot, i) {{
              dot.classList.toggle('q-carousel-dot-active', i === closest);
            }});
          }}

          if (dotsRow) {{
            dotsRow.querySelectorAll('.q-carousel-dot').forEach(function (dot, i) {{
              dot.addEventListener('click', function () {{
                track.scrollTo({{ left: originals[i].offsetLeft, behavior: 'smooth' }});
                pauseThenResume();
              }});
            }});
          }}

          function tick() {{
            if (!paused && loopOffset > 0) {{
              var next = track.scrollLeft + SPEED;
              track.scrollLeft = next >= loopOffset ? next - loopOffset : next;
            }}
            updateActiveDot();
            requestAnimationFrame(tick);
          }}
          requestAnimationFrame(tick);
        }})();
        """)


class SliderCarousel(CarouselBase):
    """
    Paginated slide-by-slide carousel with dot navigation and arrows.

    Advances one item at a time via scroll-snap. Autoplay, if enabled,
    advances on an interval and pauses on interaction.

    Required Props:
        items (list[Component]): Slide content, one component per slide.

    Optional Props:
        gap (str): CSS gap between items. Defaults to the theme's spacing token.
        autoplay (bool): Whether to auto-advance slides. Default True.
        interval (int): Milliseconds between auto-advances. Default 4000.
        loop (bool): Wrap from the last slide back to the first. Default True.
        show_dots (bool): Whether to render dot navigation. Default True.
        show_arrows (bool): Whether to render prev/next arrow buttons. Default True.
        pause_on_interaction (bool): Pause autoplay on pointer/wheel/touch. Default True.
        resume_delay (int): Milliseconds of idle time before autoplay resumes. Default 3000.
        id (str): Element id. Auto-generated if omitted.

    Usage:
    ```python
    SliderCarousel(items=[Slide(...) for s in slides], interval=5000)
    ```
    """

    docs_preview_kwargs = {
        "items": [Container(text=f"Slide {i}", style={"padding": "24px", "width": "100%"}) for i in range(3)],
        "autoplay": True,
    }
    docs_animation_steps = [
        {"delay": 1000},
        {"delay": 600, "cursor": {"target": ".q-carousel-arrow-next"}},
        {"delay": 400, "target": ".q-carousel-arrow-next", "click": True},
        {"delay": 1500},
    ]

    def on_create(self) -> None:
        super().on_create()
        
        # Get some kwargs
        self.autoplay = self.kwargs.get("autoplay", True)
        self.interval = self.kwargs.get("interval", 4000)
        self.loop = self.kwargs.get("loop", True)
        self.show_arrows = self.kwargs.get("show_arrows", True)
        self.pause_on_interaction = self.kwargs.get("pause_on_interaction", True)
        self.resume_delay = self.kwargs.get("resume_delay", 3000)

        for item in self.items:
            item.klass = f"{item.klass or ''} q-carousel-item".strip()
            item.style.update({"flex": "0 0 100%", "scroll-snap-align": "start"})

        # Build track
        track = self.build_track(self.items, extra_style={"scroll-snap-type": "x mandatory"})
        
        # Initialize row children with the track
        row_children = [track]
        
        if self.show_arrows:
            row_children = [self.build_arrow("prev", "‹"), track, self.build_arrow("next", "›")]

        children = [
            Container(
                klass="q-carousel-row",
                style={
                    "display": "flex",
                    "align-items": "center",
                    "gap": "12px",
                },
                children=row_children
            ),
        ]

        if self.show_dots:
            children.append(self.build_dots())

        # Initial children
        self.add_children(children)
        
        # Add other children
        self.add_children([self.build_dot_style(), self.build_script()])

    def build_arrow(self, direction: str, glyph: str) -> Container:
        """
        Builds a prev/next arrow button.

        Args:
            direction: "prev" or "next", used for id and click wiring.
            glyph: Character rendered inside the button.

        Returns:
            A Container styled as a circular arrow button.
        """
        return Container(
            id=f"{self.id}-arrow-{direction}",
            klass=f"q-carousel-arrow q-carousel-arrow-{direction}",
            text=glyph,
            props={
                "role": "button",
                "tabindex": "0",
                "aria-label": f"{direction.title()} slide",
            },
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "width": "32px",
                "height": "32px",
                "border-radius": "999px",
                "background": Theme.current.surface_elevated_color,
                "color": Theme.current.text_color,
                "cursor": "pointer",
                "flex": "0 0 auto",
            },
        )

    def build_script(self) -> Script:
        """
        Returns the script driving slide paging, dot/arrow navigation,
        autoplay, and pause/resume on interaction.

        Returns:
            A Script component with the slider's runtime behavior.
        """
        return Script(inner_html=f"""
        (function () {{
          var track = document.getElementById('{self.id}-track');
          var dotsRow = document.getElementById('{self.id}-dots');
          var prevBtn = document.getElementById('{self.id}-arrow-prev');
          var nextBtn = document.getElementById('{self.id}-arrow-next');
          if (!track) return;

          var slides = track.querySelectorAll('.q-carousel-item');
          var count = slides.length;
          var index = 0;
          var paused = false;
          var resumeTimer = null;
          var autoTimer = null;

          function goTo(i) {{
            index = {str(self.loop).lower()} ? (i + count) % count : Math.max(0, Math.min(count - 1, i));
            track.scrollTo({{ left: slides[index].offsetLeft, behavior: 'smooth' }});
            if (dotsRow) {{
              dotsRow.querySelectorAll('.q-carousel-dot').forEach(function (dot, di) {{
                dot.classList.toggle('q-carousel-dot-active', di === index);
              }});
            }}
          }}

          function pauseThenResume() {{
            paused = true;
            if (resumeTimer) clearTimeout(resumeTimer);
            resumeTimer = setTimeout(function () {{ paused = false; }}, {self.resume_delay});
          }}

          if (dotsRow) {{
            dotsRow.querySelectorAll('.q-carousel-dot').forEach(function (dot, i) {{
              dot.addEventListener('click', function () {{ goTo(i); pauseThenResume(); }});
            }});
          }}
          if (prevBtn) prevBtn.addEventListener('click', function () {{ goTo(index - 1); pauseThenResume(); }});
          if (nextBtn) nextBtn.addEventListener('click', function () {{ goTo(index + 1); pauseThenResume(); }});

          if ({str(self.pause_on_interaction).lower()}) {{
            ['pointerdown', 'wheel', 'touchstart'].forEach(function (evt) {{
              track.addEventListener(evt, pauseThenResume, {{ passive: true }});
            }});
          }}

          if ({str(self.autoplay).lower()}) {{
            autoTimer = setInterval(function () {{
              if (!paused) goTo(index + 1);
            }}, {self.interval});
          }}

          goTo(0);
        }})();
        """)
