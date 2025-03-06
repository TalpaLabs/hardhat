from textual.screen import Screen
from textual.containers import Grid, Vertical
from textual.widgets import (
    Header,
    Footer,
    TabbedContent,
    TabPane,
    Static,
    Button,
    Input,
)
from textual.app import ComposeResult
from textual import events

class GridView(Screen):
    CSS_PATH = "../css/grid_view.css"

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

    def compose(self) -> ComposeResult:
        """Creates UI layout including an interactive command line at the bottom."""
        yield Header()

        # Main window
        with TabbedContent(initial="add_main", id="main_tabs", classes="box main_window"):
            with TabPane("\[+]", id="add_main"):
                yield Button("[+] Add Tab", id="add_main_tabs")

        # Small window #1
        with TabbedContent(initial="add_small_1", id="small_tabs_1", classes="box small_window"):
            with TabPane("\[+]", id="add_small_1"):
                yield Button("[+] Add Tab", id="add_small_tabs_1")

        # Small window #2
        with TabbedContent(initial="add_small_2", id="small_tabs_2", classes="box small_window"):
            with TabPane("\[+]", id="add_small_2"):
                yield Button("[+] Add Tab", id="add_small_tabs_2")

        # Medium window
        with TabbedContent(initial="add_medium", id="medium_tabs", classes="box medium_window"):
            with TabPane("\[+]", id="add_medium"):
                yield Button("[+] Add Tab", id="add_medium_tabs")

        # Command Line Input
        yield Input(
            placeholder="Enter command...",
            classes="box command_input",
            id="command_input",
        )

        yield Footer()

    # -------------------------------------------------------------------------
    # TAB ADD / DELETE LOGIC 
    # -------------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id.startswith("add_"):
            tabbed_content_id = button_id.replace("add_", "")
            self.add_tab(tabbed_content_id)
        elif button_id.startswith("delete_"):
            self.delete_tab(button_id)

    def add_tab(self, tabbed_content_id: str) -> None:
        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)

        self.tab_counters[tabbed_content_id] += 1
        counter_value = self.tab_counters[tabbed_content_id]

        new_tab_id = f"{tabbed_content_id}_tab_{counter_value}"
        new_tab_name = f"Tab {counter_value}"
        new_tab_content = self._create_tab_content(tabbed_content_id, new_tab_id, new_tab_name)

        add_tab_id = self.add_tab_map[tabbed_content_id]
        tabbed_content.add_pane(
            TabPane(new_tab_name, new_tab_content, id=new_tab_id),
            before=add_tab_id,
        )
        tabbed_content.active = new_tab_id

    def delete_tab(self, delete_button_id: str) -> None:
        remainder = delete_button_id[len("delete_"):]
        
        tabbed_content_id = None
        tab_id = None
        for candidate_id in self.add_tab_map.keys():
            prefix = candidate_id + "_"
            if remainder.startswith(prefix):
                tabbed_content_id = candidate_id
                tab_id = remainder[len(prefix):]
                break

        if not tabbed_content_id or not tab_id:
            return

        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)
        if tab_id == self.add_tab_map[tabbed_content_id]:
            return

        tabbed_content.remove_pane(tab_id)

    def _create_tab_content(self, tabbed_content_id: str, tab_id: str, tab_name: str) -> Vertical:
        delete_button_id = f"delete_{tabbed_content_id}_{tab_id}"
        return Vertical(
            Static(f"Content for {tab_name}\n"),
            Button("[x] Delete Tab", id=delete_button_id),
        )

    # -------------------------------------------------------------------------
    # COMMAND LINE LOGIC
    # -------------------------------------------------------------------------
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when user presses Enter in any Input widget."""
        if event.input.id == "command_input":
            command = event.value.strip()
            if command:
                self.process_command(command)
            # Clear input
            event.input.value = ""
            # Reset the history_index to "end"
            self.history_index = len(self.command_history)

    def process_command(self, command: str) -> None:
        """Handle the logic for a typed command."""
        self.command_history.append(command)
        print(f"User command: {command}")

    def on_key(self, event: events.Key) -> None:
        """
        Capture Up/Down arrow keys when the command_input is focused,
        and cycle through command history.
        """
        # Chek that the command_input is focused
        command_input = self.query_one("#command_input", Input)
        if not command_input.has_focus:
            return  # Only respond to arrow keys if the user is editing the command input

        if event.key == "up":
            event.stop()
            # Move history index up if possible
            if self.history_index > 0:
                self.history_index -= 1

            # If we have items in history, show them
            if 0 <= self.history_index < len(self.command_history):
                command_input.value = self.command_history[self.history_index]

        elif event.key == "down":
            event.stop()
            # Move history index down if possible
            if self.history_index < len(self.command_history):
                self.history_index += 1

            # If the index equals the length, clear the input
            if self.history_index == len(self.command_history):
                command_input.value = ""
            else:
                command_input.value = self.command_history[self.history_index]
