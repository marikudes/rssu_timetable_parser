import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget

kivy.require("2.3.1")


class MyApp(App):
    def build(self) -> Widget:
        return Label(text="Hello world")


if __name__ == "__main__":
    MyApp().run()
