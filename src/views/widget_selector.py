"""
Module for providing a widget selector modal in the TUI.

This module defines the WidgetSelector class which displays a modal popup that allows users to select a widget
to add to their interface. The modal consists of a title, a list view with available widget options, and a cancel
button to close the modal without a selection.
"""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Static, ListView, ListItem, Button

class WidgetSelector(ModalScreen[str]):
    """
    Modal popup screen for selecting a widget.

    This modal displays a list of widget options for the user to choose from. The layout is organized in a grid and
    includes a title, a list view (populated with widget items upon mounting), and a cancel button to exit the modal
    without making a selection.

    Attributes:
        CSS_PATH (str): The file path to the CSS stylesheet that styles the widget selector modal.
    """
    
    CSS_PATH = "../css/widget_selector.tcss"

    def compose(self) -> ComposeResult:
        """
        Compose the layout of the widget selector modal.

        This method yields a grid layout containing:
          - A static widget that displays the prompt "Choose a widget to add:".
          - A list view widget that will be populated with widget options.
          - A cancel button to dismiss the modal without a selection.

        Returns:
            ComposeResult: A generator yielding the UI widgets that form the modal.
        """
        yield Grid(
            Static("Choose a widget to add:", id="selector_title"),
            ListView(id="widget_list"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_mount(self) -> None:
        """
        Populate the widget list after the modal is mounted.

        This method is called once the modal has been mounted to the screen. It locates the list view by its ID
        ("#widget_list") and appends several list items, each representing a different widget that the user can select.
        """
        list_view = self.query_one("#widget_list", ListView)
        list_view.append(ListItem(Static("Output"), id="Output"))
        list_view.append(ListItem(Static("Disassembly"), id="Disassembly"))
        list_view.append(ListItem(Static("Registers"), id="Registers"))
        list_view.append(ListItem(Static("Stack"), id="Stack"))
        list_view.append(ListItem(Static("Backtrace"), id="Backtrace"))
        list_view.append(ListItem(Static("RawResponses"), id="RawResponses"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """
        When the user selects an item from the list, this method retrieves the identifier of the selected widget
        and dismisses the modal, returning the chosen widget's identifier.

        Args:
            event (ListView.Selected): The event object containing details about the selected list item.
        """
        choice = event.item.id
        self.dismiss(choice)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        This method is triggered when the cancel button is pressed. It dismisses the modal without returning any
        widget selection, effectively canceling the widget selection process.

        Args:
            event (Button.Pressed): The event object containing details about the button press.
        """
        self.dismiss(None)
