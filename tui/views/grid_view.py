from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.events import Key

class GridView(Screen):
    CSS_PATH = "../css/grid_view.css"

    def compose(self):
        """Creates UI layout."""
        yield Header()
        yield Static("Main_Window", classes="box main_window")
        yield Static("Small_window_1", classes="box small_window")
        yield Static("Small_window_2", classes="box small_window")
        yield Static("meidum_window", classes="box medium_window")
        yield Static("Comannd Input", classes="box command_input")
        yield Footer()