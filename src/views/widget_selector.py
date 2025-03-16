from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Static, ListView, ListItem, Button

class WidgetSelector(ModalScreen[str]):
    """Modal popup for selecting a widget."""
    
    CSS_PATH = "../css/widget_selector.tcss"

    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Choose a widget to add:", id="selector_title"),
            ListView(id="widget_list"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_mount(self) -> None:
        """Add list items after the screen is mounted."""
        list_view = self.query_one("#widget_list", ListView)
        list_view.append(ListItem(Static("Registers"), id="Registers"))
        list_view.append(ListItem(Static("RawResponses"), id="RawResponses"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Close modal and return the selected widget."""
        choice = event.item.id
        self.dismiss(choice)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle cancle button presses."""
        self.dismiss(None)  # Close without selecting
