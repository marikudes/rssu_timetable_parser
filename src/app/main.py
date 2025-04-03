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
from parser.timetableparser import TimeTableParser

BASE_DIR = Path(__file__).parent.resolve()


class ScheduleApp(App):
    def __init__(self) -> None:
        GroupListParser().save_data()

        json_path = BASE_DIR / "data" / "selected_group.json"
        self.selected_group = ""
        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list) and data:
                    self.selected_group = data[0]
                else:
                    self.selected_group = ""
        except (FileNotFoundError, json.JSONDecodeError, IndexError):
            with json_path.open("w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)

        if self.selected_group:
            TimeTableParser().save_data(group=self.selected_group)

        super().__init__()
        self.dropdown: DropDown | None = None
        self.root: Widget | None = None

    def build(self) -> Widget:
        kv_path = BASE_DIR / "kv" / "my.kv"
        self.root = Builder.load_file(str(kv_path))
        self.create_day_buttons(self.root)

        if self.root and hasattr(self.root.ids, "group_input"):
            self.root.ids.group_input.text = self.selected_group
        self.update_schedule(self.root, "Понедельник")
        return self.root

    def load_groups(self) -> list[str]:
        json_path = BASE_DIR / "data" / "groups.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                groups = json.load(file)
                return cast("list[str]", groups) if isinstance(groups, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_schedule(self) -> dict[str, list[dict[str, Any]]]:
        json_path = BASE_DIR / "data" / "schedule.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                schedule = json.load(file)
                if isinstance(schedule, dict):
                    return cast("dict[str, list[dict[str, Any]]]", schedule)
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
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

        date_keys = list(schedule.keys())
        days = self.get_days()
        day_index = days.index(selected_day)

        lessons = schedule[date_keys[day_index]] if date_keys and day_index < len(date_keys) else []

        if lessons:
            for lesson in lessons:
                lesson_text = (
                    f"{lesson.get('time', 'N/A')} - {lesson.get('subject', 'N/A')}\n"
                    f"{lesson.get('category', 'N/A')} - {lesson.get('teacher', 'N/A')}\n"
                    f"{lesson.get('address', 'N/A')} {lesson.get('auditorium', 'N/A')}"
                )
                lesson_label = Label(text=lesson_text, halign="left", valign="top")
                lesson_label.text_size = (lessons_container.width, None)
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
        TimeTableParser().save_data(group=self.selected_group)
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
