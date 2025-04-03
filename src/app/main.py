import json
from pathlib import Path
from typing import Any, cast

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from parser.getgroupslist import GroupListParser

BASE_DIR = Path(__file__).parent.resolve()


class ScheduleApp(App):
    def __init__(self) -> None:
        json_path = BASE_DIR / "data" / "groups.json"
        with json_path.open("w", encoding="utf-8") as file:
            group_list = GroupListParser().response()["suggestions"]
            json.dump(group_list, file, ensure_ascii=False, indent=4)

        json_path = BASE_DIR / "data" / "selected_group.json"
        with json_path.open(encoding="utf-8") as file:
            self.selected_group: str = json.load(file)[0]

        super().__init__()
        self.dropdown: DropDown | None = None
        self.root: Widget | None = None

    def build(self) -> Widget:
        kv_path = BASE_DIR / "kv" / "my.kv"
        try:
            self.root = Builder.load_file(str(kv_path))
        except FileNotFoundError:
            print(f"Error: Could not find {kv_path}")
            raise
        self.create_day_buttons(self.root)

        if self.root and hasattr(self.root.ids, "group_input"):
            self.root.ids.group_input.text = self.selected_group
        self.update_schedule(self.root, "Понедельник")
        return self.root

    def load_groups(self) -> list[str]:
        json_path = BASE_DIR / "data" / "groups.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                return cast("list[str]", json.load(file))
        except FileNotFoundError:
            print(f"Error: Could not find {json_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode {json_path}")
            return []

    def load_schedule(self) -> dict[str, dict[str, Any]]:
        json_path = BASE_DIR / "data" / "schedule.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                return cast("dict[str, dict[str, Any]]", json.load(file))
        except FileNotFoundError:
            print(f"Error: Could not find {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode {json_path}")
            return {}

    def get_days(self) -> list[str]:
        return ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    def create_day_buttons(self, root: Widget) -> None:
        days_container = root.ids.days_container
        for day in self.get_days():
            btn = ToggleButton(
                text=day, group="days", on_press=lambda _, d=day: self.update_schedule(root, d)
            )
            if day == "Понедельник":
                btn.state = "down"
            days_container.add_widget(btn)

    def update_schedule(self, root: Widget, selected_day: str) -> None:
        schedule = self.load_schedule()
        lessons_container = root.ids.lessons_container
        lessons_container.clear_widgets()
        day_label = Label(text=selected_day, font_size="24sp", color=(1, 0, 0, 1))
        lessons_container.add_widget(day_label)

        if self.selected_group and self.selected_group in schedule:
            group_schedule = schedule[self.selected_group]
            lessons = group_schedule.get(selected_day, [])
        else:
            lessons = []

        if lessons:
            for lesson in lessons:
                lesson_label = Label(text=f"{lesson['time']} - {lesson['subject']}")
                lessons_container.add_widget(lesson_label)
        else:
            no_lessons_label = Label(text="Нет уроков", font_size="18sp", color=(0.5, 0.5, 0.5, 1))
            lessons_container.add_widget(no_lessons_label)

    def update_group_suggestions(self, text_input: TextInput) -> None:
        if not text_input.focus or not self.root:
            return
        if not self.dropdown:
            self.dropdown = DropDown()
        self.dropdown.clear_widgets()
        groups = self.load_groups()
        input_text = text_input.text.lower()
        for group in groups:
            if input_text in group.lower():
                btn = Button(text=group, size_hint_y=None, height=44)
                btn.bind(on_release=lambda btn: self.select_group(btn.text, text_input))
                self.dropdown.add_widget(btn)
        if self.dropdown.children and not self.dropdown.parent:
            self.dropdown.open(text_input)
        elif not self.dropdown.children and self.dropdown.parent:
            self.dropdown.dismiss()

    def show_group_dropdown(self, text_input: TextInput) -> None:
        self.update_group_suggestions(text_input)

    def select_group(self, group: str, text_input: TextInput) -> None:
        json_path = BASE_DIR / "data" / "selected_group.json"
        text_input.text = group
        self.selected_group = group

        with json_path.open("w", encoding="utf-8") as file:
            json.dump([group], file, ensure_ascii=False, indent=4)

        if self.dropdown:
            self.dropdown.dismiss()
        if self.root:
            current_day = next(
                btn.text for btn in self.root.ids.days_container.children if btn.state == "down"
            )
            self.update_schedule(self.root, current_day)


if __name__ == "__main__":
    ScheduleApp().run()
