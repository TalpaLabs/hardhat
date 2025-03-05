from textual.app import App
from .views.main_view import MainView
from .views.grid_view import GridView

class HardHat(App):
    """Main Textual application."""
    def on_mount(self):
        self.push_screen(GridView())