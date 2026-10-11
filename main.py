
import json
from datetime import date, timedelta
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore

KV = """
BoxLayout:
    orientation: "vertical"
    padding: "18dp"
    spacing: "12dp"

    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "[b]DARKSTREAK[/b]"
        markup: True
        font_size: "30sp"
        color: 0.65, 0.55, 1, 1
        size_hint_y: None
        height: "55dp"

    Label:
        id: today
        text: ""
        color: 0.7, 0.7, 0.78, 1
        size_hint_y: None
        height: "30dp"

    Label:
        text: "Small steps. Strong streaks."
        color: 1, 1, 1, 1
        font_size: "18sp"
        size_hint_y: None
        height: "35dp"

    GridLayout:
        id: activities
        cols: 1
        spacing: "12dp"
"""


class DarkStreak(App):
    def build(self):
        self.title = "DARKSTREAK"
        self.store = JsonStore(
            str(Path(self.user_data_dir) / "progress.json")
        )

        self.root = Builder.load_string(KV)
        self.root.ids.today.text = date.today().strftime(
            "%A, %d %B %Y"
        )
        self.show_activities()
        return self.root

    def get_days(self, activity):
        if self.store.exists(activity):
            return self.store.get(activity)["days"]
        return []

    def get_streak(self, activity):
        days = set(self.get_days(activity))
        current = date.today()

        if current.isoformat() not in days:
            current -= timedelta(days=1)

        count = 0
        while current.isoformat() in days:
            count += 1
            current -= timedelta(days=1)

        return count

    def show_activities(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        area = self.root.ids.activities
        area.clear_widgets()

        for activity in ["Coding", "Bible Study", "Revision"]:
            done = date.today().isoformat() in self.get_days(activity)
            streak = self.get_streak(activity)

            card = BoxLayout(
                orientation="vertical",
                padding="10dp",
                spacing="4dp",
                size_hint_y=None,
                height="125dp"
            )

            card.add_widget(Label(
                text=activity,
                font_size="20sp",
                color=(1, 1, 1, 1)
            ))

            card.add_widget(Label(
                text=f"{'Completed' if done else 'Not completed'}"
                     f"  |  🔥 {streak} day streak",
                color=(0.72, 0.72, 0.8, 1)
            ))

            button = Button(
                text="Completed ✓" if done else "Mark completed",
                background_normal="",
                background_color=(
                    (0.15, 0.48, 0.32, 1) if done
                    else (0.40, 0.27, 0.75, 1)
                ),
                size_hint_y=None,
                height="42dp",
                disabled=done
            )
            button.bind(
                on_release=lambda btn, name=activity:
                self.mark_done(name)
            )

            card.add_widget(button)
            area.add_widget(card)

    def mark_done(self, activity):
        days = self.get_days(activity)
        today = date.today().isoformat()

        if today not in days:
            days.append(today)

        self.store.put(activity, days=days)
        self.show_activities()


if __name__ == "__main__":
    DarkStreak().run()
