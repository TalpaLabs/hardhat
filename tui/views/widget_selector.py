from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem

class WidgetSelector(ModalScreen[str]):
    CSS_PATH = "../css/widget_selector.css"

    def compose(self) -> ComposeResult:
        yield Static("Choose a widget to add:", id="selector_title")
        yield ListView(id="widget_list")  # just yield the empty list for now

    def on_mount(self) -> None:
        """
        Called after the WidgetSelector is mounted, so now we can safely append items 
        without triggering the 'Can't mount before <widget> is mounted' error.
        """
        list_view = self.query_one("#widget_list", ListView)
        list_view.append(ListItem(Static("WidgetA"), id="WidgetA"))
        list_view.append(ListItem(Static("WidgetB"), id="WidgetB"))
        list_view.append(ListItem(Static("WidgetC"), id="WidgetC"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        choice = event.item.id
        self.dismiss(choice)

    def on_dismiss(self) -> None:
        if not self._is_result_set:
            self.dismiss(None)