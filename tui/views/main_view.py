from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Header, Footer, Button
from ..widgets.command_input import CommandInput
from ..widgets.display_response import ResponseDisplay
from ..coreminer_interface import CoreMinerProcess

class MainView(Screen):
    def compose(self):
        """Creates UI layout."""
        yield Header()
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