
from datetime import date, timedelta

from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle


# DARKSTREAK COLOURS
BG = "#080D16"
CARD = "#111C30"
INNER = "#0C1525"
BLUE = "#1769FF"
RED = "#E52340"
GREEN = "#36E6A1"
WHITE = "#F1F5FF"
MUTED = "#98AACA"
BORDER = "#203553"

ACTIVITIES = {
    "Coding": {
        "icon": "</>",
        "description": "Build your skills",
    },
    "Bible Study": {
        "icon": "+",
        "description": "Grow in faith",
    },
    "Revision": {
        "icon": "A+",
        "description": "Secure your future",
    },
}


def colour(value):
    return get_color_from_hex(value)


class RoundedCard(BoxLayout):
    def __init__(self, bg=CARD, **kwargs):
        super().__init__(**kwargs)
        self.background_colour = bg
        with self.canvas.before:
            Color(*colour(self.background_colour))
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)],
            )

        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


class DarkStreakApp(App):
    def build(self):
        self.title = "DARKSTREAK"
        self.store = JsonStore("darkstreak.json")

        # Each activity has its own saved dates.
        for activity in ACTIVITIES:
            if not self.store.exists(activity):
                self.store.put(activity, dates=[])

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(18), dp(16), dp(12)],
            spacing=dp(8),
        )

        with self.root_layout.canvas.before:
            Color(*colour(BG))
            self.background = RoundedRectangle(
                pos=self.root_layout.pos,
                size=self.root_layout.size,
            )

        self.root_layout.bind(
            pos=self.update_background,
            size=self.update_background,
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
        )

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            size_hint_y=None,
        )
        self.content.bind(
            minimum_height=self.content.setter("height")
        )

        scroll.add_widget(self.content)
        self.root_layout.add_widget(scroll)

        self.refresh_screen()
        return self.root_layout

    def update_background(self, *_):
        self.background.pos = self.root_layout.pos
        self.background.size = self.root_layout.size

    def get_dates(self, activity):
        return sorted(set(self.store.get(activity)["dates"]))

    def get_streak(self, activity):
        dates = set(self.get_dates(activity))
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Keep the streak alive until today if yesterday was completed.
        current = today if today.isoformat() in dates else yesterday

        if current.isoformat() not in dates:
            return 0

        streak = 0
        while current.isoformat() in dates:
            streak += 1
            current -= timedelta(days=1)

        return streak

    def checked_today(self, activity):
        return date.today().isoformat() in self.get_dates(activity)

    def check_in(self, activity):
        dates = self.get_dates(activity)
        today = date.today().isoformat()

        if today not in dates:
            dates.append(today)
            self.store.put(activity, dates=sorted(dates))

        self.refresh_screen()

    def undo_check_in(self, activity):
        dates = self.get_dates(activity)
        today = date.today().isoformat()

        if today in dates:
            dates.remove(today)
            self.store.put(activity, dates=dates)

        self.refresh_screen()

    def make_label(
        self,
        text,
        size=16,
        color=WHITE,
        bold=False,
        height=None,
        align="left",
    ):
        label = Label(
            text=text,
            font_size=sp(size),
            color=colour(color),
            bold=bold,
            halign=align,
            valign="middle",
            size_hint_y=None,
            height=dp(height or 32),
        )
        label.bind(
            size=lambda widget, value: setattr(
                widget, "text_size", value
            )
        )
        return label

    def make_button(self, text, bg, callback, height=52):
        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_down="",
            background_color=colour(bg),
            color=colour(WHITE),
            font_size=sp(15),
            bold=True,
        )
        button.bind(on_release=lambda *_: callback())
        return button

    def add_section(self, activity, details):
        dates = self.get_dates(activity)
        streak = self.get_streak(activity)
        completed = self.checked_today(activity)

        card = RoundedCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
        )
        card.bind(
            minimum_height=card.setter("height")
        )

        heading = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(12),
        )

        icon_card = RoundedCard(
            bg="#172D50",
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            radius=dp(14),
            padding=0,
        )
        icon_card.add_widget(
            self.make_label(
                details["icon"],
                size=23,
                color=BLUE,
                bold=True,
            )
        )

        name_box = BoxLayout(orientation="vertical", spacing=0)
        name_box.add_widget(
            self.make_label(activity.upper(), 19, WHITE, True, 30)
        )
        name_box.add_widget(
            self.make_label(details["description"], 13, MUTED, False, 25)
        )

        heading.add_widget(icon_card)
        heading.add_widget(name_box)
        card.add_widget(heading)

        # Separate statistics for this activity only.
        stats = BoxLayout(
            size_hint_y=None,
            height=dp(82),
            spacing=dp(8),
        )

        total_card = RoundedCard(
            bg=INNER,
            orientation="vertical",
            padding=dp(8),
            spacing=dp(2),
        )
        total_card.add_widget(
            self.make_label(str(len(dates)), 27, WHITE, True, 38, "center")
        )
        total_card.add_widget(
            self.make_label("TOTAL DAYS", 11, MUTED, False, 22, "center")
        )

        streak_card = RoundedCard(
            bg=INNER,
            orientation="vertical",
            padding=dp(8),
            spacing=dp(2),
        )
        streak_card.add_widget(
            self.make_label(str(streak), 27, GREEN, True, 38, "center")
        )
        streak_card.add_widget(
            self.make_label("DAY STREAK", 11, MUTED, False, 22, "center")
        )

        stats.add_widget(total_card)
        stats.add_widget(streak_card)
        card.add_widget(stats)

        if completed:
            status = "COMPLETED TODAY  ✓"
            status_color = GREEN
        else:
            status = "NOT COMPLETED TODAY"
            status_color = MUTED

        card.add_widget(
            self.make_label(status, 13, status_color, True, 30)
        )

        if completed:
            card.add_widget(
                self.make_button(
                    "UNDO TODAY'S CHECK-IN",
                    RED,
                    lambda: self.undo_check_in(activity),
                )
            )
        else:
            card.add_widget(
                self.make_button(
                    "I'VE COMPLETED THIS TODAY",
                    BLUE,
                    lambda: self.check_in(activity),
                )
            )

        # Activity-specific history: never mixed with other activities.
        card.add_widget(
            self.make_label("RECENT HISTORY", 13, MUTED, True, 28)
        )

        if dates:
            for saved_date in reversed(dates[-5:]):
                parsed = date.fromisoformat(saved_date)
                row = BoxLayout(
                    size_hint_y=None,
                    height=dp(32),
                    spacing=dp(6),
                )
                row.add_widget(
                    self.make_label(
                        parsed.strftime("%d %b %Y"),
                        13,
                        WHITE,
                        False,
                        30,
                    )
                )
                row.add_widget(
                    self.make_label(
                        "REPORTED",
                        12,
                        GREEN,
                        True,
                        30,
                        "right",
                    )
                )
                card.add_widget(row)
        else:
            card.add_widget(
                self.make_label(
                    "No check-ins yet. Start today!",
                    13,
                    MUTED,
                    False,
                    30,
                )
            )

        self.content.add_widget(card)

    def refresh_screen(self):
        self.content.clear_widgets()

        self.content.add_widget(
            self.make_label("DARKSTREAK", 31, WHITE, True, 55, "center")
        )
        self.content.add_widget(
            self.make_label(
                "YOUR DISCIPLINE. YOUR PROGRESS.",
                12,
                MUTED,
                False,
                30,
                "center",
            )
        )
        self.content.add_widget(
            self.make_label(
                date.today().strftime("%A, %d %B %Y"),
                16,
                WHITE,
                False,
                42,
                "center",
            )
        )

        self.content.add_widget(
            self.make_label("TODAY'S MISSIONS", 20, WHITE, True, 42)
        )

        for activity, details in ACTIVITIES.items():
            self.add_section(activity, details)

        self.content.add_widget(
            self.make_label(
                "One day at a time. Keep building.",
                12,
                MUTED,
                False,
                42,
                "center",
            )
        )


if __name__ == "__main__":
    DarkStreakApp().run()
