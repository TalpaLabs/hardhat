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
            ListView(id="widget_list"),  # Empty list at first
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_mount(self) -> None:
        """Add list items after the screen is mounted."""
        list_view = self.query_one("#widget_list", ListView)
        list_view.append(ListItem(Static("WidgetA"), id="WidgetA"))
        list_view.append(ListItem(Static("WidgetB"), id="WidgetB"))
        list_view.append(ListItem(Static("WidgetC"), id="WidgetC"))
        list_view.append(ListItem(Static("ResponseDisplay"), id="ResponseDisplay"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Close modal and return the selected widget."""
        choice = event.item.id
        self.dismiss(choice)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss(None)  # Close without selecting
