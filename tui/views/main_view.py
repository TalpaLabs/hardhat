from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.events import Key
from ..widgets.command_input import CommandInput
from ..widgets.display_response import ResponseDisplay
from ..coreminer_interface import CoreMinerProcess
from ..widgets.base_container import BaseContainer

class MainView(Screen):
    CSS_PATH = "../css/main_view.css"

    def compose(self):
        """Creates UI layout."""
        yield Header()
        yield Horizontal(
            Static("Left Panel", id="left_panel"),
            Static("Right Panel", id="right_panel"),
            id="splitter",
        )
        yield Vertical(                
            CommandInput(),
            Button("Send", id="send_button"),
            ResponseDisplay(),
        )
        yield Footer()

    def on_mount(self):
        """Initialize Rust process."""
        self.process = CoreMinerProcess(rust_binary_path="../rust_dummy/target/release/rust_dummy")
        self.set_interval(0.5, self.check_coreminer_output)

    def check_coreminer_output(self):
        """Polls Rust process for responses."""
        response = self.process.get_response()
        if response:
            self.query_one(ResponseDisplay).update_response(response["message"])

    def on_button_pressed(self, event):
        """Handles button press."""
        if event.button.id == "send_button":
            self.send_command()

    def send_command(self):
        """Sends command from input field to Rust."""
        input_widget = self.query_one(CommandInput)
        command = input_widget.value.strip()
        if command:
            self.process.send_command(command)
            input_widget.clear()

    def on_key(self, event: Key) -> None:
        """Allow user to resize containers using left/right arrow keys."""
        left_panel = self.query_one("#left_panel")
        right_panel = self.query_one("#right_panel")

        # Get current width values (ensure they are floats)
        left_width = float(left_panel.styles.width.value)
        right_width = float(right_panel.styles.width.value)

        if event.key == "left":
            left_panel.styles.width = f"{max(10, left_width - 5)}%"
            right_panel.styles.width = f"{min(90, right_width + 5)}%"

        elif event.key == "right":
            left_panel.styles.width = f"{min(90, left_width + 5)}%"
            right_panel.styles.width = f"{max(10, right_width - 5)}%"

        self.refresh()  # Update UI
