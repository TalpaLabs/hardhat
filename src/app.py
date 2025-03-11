from textual.app import App
from views.main_view import MainView

class HardHat(App):
    """Main Textual application."""
    def on_mount(self):
        self.push_screen(MainView())

if __name__ == "__main__":
    HardHat().run()