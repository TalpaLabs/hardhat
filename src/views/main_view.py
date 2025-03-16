from textual.screen import Screen
from textual.app import ComposeResult
from textual.events import Key
from textual.containers import ScrollableContainer, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    TabbedContent,
    TabPane,
    Static,
)

# Diferent Screens
from views.widget_selector import WidgetSelector

#Coreminer API
from coreminer_interface import CoreMinerProcess

# Central Data Store
from data_store import DataStore

# Import of custom widgets
from widgets.raw_responses import RawResponses
from widgets.registers import Registers
from widgets.stack import Stack
from widgets.output import Output
from widgets.disassembly import Disassembly


class MainView(Screen):
    CSS_PATH = "../css/main_view.tcss"

    def __init__(self) -> None:
        super().__init__()
        # Keep your tab counters and add_tab_map from earlier
        self.tab_counters = {
            "main_tabs": 0,
            "small_tabs_1": 0,
            "small_tabs_2": 0,
            "medium_tabs": 0,
        }
        self.add_tab_map = {
            "main_tabs":    "add_main",
            "small_tabs_1": "add_small_1",
            "small_tabs_2": "add_small_2",
            "medium_tabs":  "add_medium",
        }

        # Command history storage
        self.command_history: list[str] = []
        self.history_index: int = 0  # Will track which command in history is displayed

        self.data_store = DataStore()

    def compose(self) -> ComposeResult:
        """Creates UI layout including an interactive command line at the bottom."""
        yield Header()

        # Main window
        with TabbedContent(initial="add_main", id="main_tabs", classes="box main_window"):
            with TabPane("\\[+]", id="add_main"):
                yield Button("Add Tab", id="add_main_tabs")

        # Small window #1
        with TabbedContent(initial="add_small_1", id="small_tabs_1", classes="box small_window"):
            with TabPane("\\[+]", id="add_small_1"):
                yield Button("Add Tab", id="add_small_tabs_1")

        # Small window #2
        with TabbedContent(initial="add_small_2", id="small_tabs_2", classes="box small_window"):
            with TabPane("\\[+]", id="add_small_2"):
                yield Button("Add Tab", id="add_small_tabs_2")

        # Medium window
        with TabbedContent(initial="add_medium", id="medium_tabs", classes="box medium_window"):
            with TabPane("\\[+]", id="add_medium"):
                yield Button("Add Tab", id="add_medium_tabs")

        # Command Line Input
        yield Input(
            placeholder="Enter command...",
            classes="box command_input",
            id="command_input",
        )

        yield Footer()

    # ─────────────────────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ─────────────────────────────────────────────────────────────────────────
    def on_mount(self):
        """Initialize CoreMiner process."""
        self.process = CoreMinerProcess(self.data_store)
        self.set_interval(0.1, self.check_coreminer_output)

    def check_coreminer_output(self):
        """Polls CoreMiner for responses."""
        response = self.process.get_response()
        if response:
            self.update_all_widgets()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle '[+] Add Tab' buttons and any 'delete_*' buttons."""
        button_id = event.button.id

        # If it's an "add_" button, open the WidgetSelector modal
        if button_id.startswith("add_"):
            # e.g. "add_main_tabs" -> tabbed_content_id = "main_tabs"
            tabbed_content_id = button_id.replace("add_", "")
            self.app.push_screen(
                WidgetSelector(),
                callback=lambda choice: self._on_widget_choice(choice, tabbed_content_id)
            )

        elif button_id.startswith("delete_"):
            self.delete_tab(button_id)

    def on_key(self, event: Key) -> None:
        """
        Capture Up/Down arrow keys for the command_input
        to allow cycling through command history.
        """
        # We'll only do this if the command_input is focused
        command_input = self.query_one("#command_input", Input)
        if not command_input.has_focus:
            return

        if event.key == "up":
            event.stop()
            if self.history_index > 0:
                self.history_index -= 1
            if 0 <= self.history_index < len(self.command_history):
                command_input.value = self.command_history[self.history_index]
        elif event.key == "down":
            event.stop()
            if self.history_index < len(self.command_history):
                self.history_index += 1
            if self.history_index == len(self.command_history):
                command_input.value = ""
            else:
                command_input.value = self.command_history[self.history_index]

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter in the command_input, storing commands in history."""
        if event.input.id == "command_input":
            command = event.value.strip()
            if command:
                self.process_command(command)
            event.input.value = ""
            self.history_index = len(self.command_history)

    # ─────────────────────────────────────────────────────────────────────────
    # LOGIC FOR PROCESSING COMMANDS
    # ─────────────────────────────────────────────────────────────────────────
    def process_command(self, command: str) -> None:
        """Append Command to history and send """
        self.command_history.append(command)
        self.process.parse_command(command)
        

    # ─────────────────────────────────────────────────────────────────────────
    # ADD / DELETE TABS
    # ─────────────────────────────────────────────────────────────────────────
    def _on_widget_choice(self, choice: str | None, tabbed_content_id: str) -> None:
        """
        Called when the user closes the WidgetSelector modal.
        `choice` is "WidgetA", "WidgetB", "WidgetC", or None if canceled.
        """
        if choice is not None:
            self.add_tab(tabbed_content_id, choice)

    def add_tab(self, tabbed_content_id: str, widget_name: str) -> None:
        """Insert a new tab with the chosen widget, before the '[+]' tab."""
        if tabbed_content_id not in self.add_tab_map:
            print(f"No such tabbed content: {tabbed_content_id}")
            return

        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)

        # Increment counter for naming/ID
        self.tab_counters[tabbed_content_id] += 1
        counter_value = self.tab_counters[tabbed_content_id]
        new_tab_id = f"{tabbed_content_id}_tab_{counter_value}"
        new_tab_name = f"{widget_name}"

        # Build the chosen widget
        widget = self._create_widget(widget_name)

        # Container with the widget + a delete button
        delete_button_id = f"delete_{tabbed_content_id}_{new_tab_id}"
        content_container = ScrollableContainer(
            VerticalScroll(
            widget
            ),
            Button("Close Tab",  id=delete_button_id),
        )

        # Insert before the "[+]" tab
        add_tab_id = self.add_tab_map[tabbed_content_id]
        tabbed_content.add_pane(
            TabPane(new_tab_name, content_container, id=new_tab_id),
            before=add_tab_id,
        )
        tabbed_content.active = new_tab_id

    def delete_tab(self, delete_button_id: str) -> None:
        """
        Remove a tab, given the button ID "delete_{tabbed_content_id}_{tab_id}".
        E.g.: "delete_main_tabs_main_tabs_tab_3"
        """
        remainder = delete_button_id.removeprefix("delete_")

        tabbed_content_id = None
        tab_id = None
        for candidate_id in self.add_tab_map:
            prefix = candidate_id + "_"
            if remainder.startswith(prefix):
                tabbed_content_id = candidate_id
                tab_id = remainder[len(prefix):]
                break

        if not tabbed_content_id or not tab_id:
            return

        # Make sure we don't remove the "[+]" tab
        if tab_id == self.add_tab_map[tabbed_content_id]:
            return

        # Remove the pane
        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)
        tabbed_content.remove_pane(tab_id)

    # ─────────────────────────────────────────────────────────────────────────
    # FACTORY FOR WIDGETS & Udaten the Content
    # ─────────────────────────────────────────────────────────────────────────
    def _create_widget(self, widget_name: str):
        """Return an instance of the selected widget by name."""
        if widget_name == "RawResponses":
            return RawResponses(self.data_store)
        elif widget_name == "Registers":
            return Registers(self.data_store)
        elif widget_name == "Stack":
            return Stack(self.data_store)
        elif widget_name == "Output":
            return Output(self.data_store)
        elif widget_name == "Disassembly":
            return Disassembly(self.data_store)
        else:
            return Static(f"Unknown widget: {widget_name}")

    def update_all_widgets(self) -> None:
        """
        Use queries to locate every TabPane (besides the '[+]' tab), then
        find any child widget with an 'update_content()' method and call it.
        """
        for tabbed_content_id, plus_tab_id in self.add_tab_map.items():
            # Get the TabbedContent by its ID
            tabbed_content = self.query_one(f"#{tabbed_content_id}", expect_type=TabbedContent)

            # Query for all TabPane children in this TabbedContent
            panes = tabbed_content.query("TabPane")

            for pane in panes:
                # Skip the '[+]' tab by comparing pane.id to plus_tab_id
                if pane.id == plus_tab_id:
                    continue

                # Inside this tab, find any widget with an update_content() method
                for child in pane.query():
                    if hasattr(child, "update") and callable(child.update_content):
                        child.update_content()

