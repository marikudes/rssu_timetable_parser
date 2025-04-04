import json
from pathlib import Path
from typing import ClassVar, cast

from kivy.app import App
from kivy.clock import Clock
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
    DAYS: ClassVar[list[str]] = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.dropdown: DropDown | None = None
        self.root: Widget | None = None
        self.groups_cache: list[str] | None = None
        self.schedule_cache: dict[str, list[dict[str, str]]] | None = None
        self._load_selected_group()
        Clock.schedule_once(self._load_initial_data, 0)

    def _load_initial_data(self, _dt: float) -> None:
        GroupListParser().save_data()
        if self.selected_group:
            TimeTableParser().save_data(group=self.selected_group)

    def _validate_selected_group_data(self, data: list[str]) -> str:
        if not data:
            raise ValueError("Invalid data format: list is empty")
        return data[0]

    def _check_data_type(self, data: object) -> list[str]:
        if not isinstance(data, list):
            raise TypeError("Invalid data format: not a list")
        return data

    def _load_selected_group(self) -> None:
        json_path = BASE_DIR / "data" / "selected_group.json"
        self.selected_group = ""
        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
                validated_data = self._check_data_type(data)
                self.selected_group = self._validate_selected_group_data(validated_data)
        except FileNotFoundError:
            with json_path.open("w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, TypeError, ValueError):
            self.selected_group = ""

    def build(self) -> Widget:
        kv_path = BASE_DIR / "kv" / "my.kv"
        self.root = Builder.load_file(str(kv_path))
        self.create_day_buttons(self.root)
        if self.root and hasattr(self.root.ids, "group_input"):
            self.root.ids.group_input.text = self.selected_group
        self.update_schedule(self.root, "Понедельник")
        return self.root

    def load_groups(self) -> list[str]:
        if self.groups_cache is not None:
            return self.groups_cache
        json_path = BASE_DIR / "data" / "groups.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                groups = json.load(file)
                self.groups_cache = cast("list[str]", groups) if isinstance(groups, list) else []
                return self.groups_cache
        except (FileNotFoundError, json.JSONDecodeError):
            self.groups_cache = []
            return self.groups_cache

    def load_schedule(self) -> dict[str, list[dict[str, str]]]:
        if self.schedule_cache is not None:
            return self.schedule_cache
        json_path = BASE_DIR / "data" / "schedule.json"
        try:
            with json_path.open(encoding="utf-8") as file:
                schedule = json.load(file)
                self.schedule_cache = (
                    cast("dict[str, list[dict[str, str]]]", schedule)
                    if isinstance(schedule, dict)
                    else {}
                )
                return self.schedule_cache
        except (FileNotFoundError, json.JSONDecodeError):
            self.schedule_cache = {}
            return self.schedule_cache

    def get_days(self) -> list[str]:
        return self.DAYS

    def create_day_buttons(self, root: Widget) -> None:
        days_container = root.ids.days_container
        if not days_container.children:
            for day in self.DAYS:
                btn = ToggleButton(
                    text=day, group="days", on_press=lambda _, d=day: self.update_schedule(root, d)
                )
                if day == "Понедельник":
                    btn.state = "down"
                days_container.add_widget(btn)

    def format_lesson_text(self, lesson: dict[str, str]) -> str:
        return (
            f"{lesson.get('time', 'N/A')} - {lesson.get('subject', 'N/A')}\n"
            f"{lesson.get('category', 'N/A')} - {lesson.get('teacher', 'N/A')}\n"
            f"{lesson.get('address', 'N/A')} {lesson.get('auditorium', 'N/A')}"
        )

    def update_schedule(self, root: Widget, selected_day: str) -> None:
        schedule = self.load_schedule()
        lessons_container = root.ids.lessons_container
        lessons_container.clear_widgets()

        date_keys = list(schedule.keys())
        day_index = self.DAYS.index(selected_day)

        lessons = schedule[date_keys[day_index]] if date_keys and day_index < len(date_keys) else []

        if lessons:
            for lesson in lessons:
                lesson_label = Label(
                    text=self.format_lesson_text(lesson),
                    halign="left",
                    valign="top",
                )
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

        matching_groups = [group for group in groups if input_text in group.lower()][:10]

        for group in matching_groups:
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
        self.schedule_cache = None

        if self.dropdown:
            self.dropdown.dismiss()
        if self.root:
            current_day = next(
                btn.text for btn in self.root.ids.days_container.children if btn.state == "down"
            )
            self.update_schedule(self.root, current_day)


if __name__ == "__main__":
    ScheduleApp().run()
