from textual.screen import Screen
from textual.containers import Grid, Vertical
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static, Button
from textual.app import ComposeResult

class GridView(Screen):
    CSS_PATH = "../css/grid_view.css"

    def __init__(self) -> None:
        super().__init__()
        # Counters to give each dynamically created tab a unique name/ID
        self.tab_counters = {
            "main_tabs": 0,
            "small_tabs_1": 0,
            "small_tabs_2": 0,
            "medium_tabs": 0,
        }
        # Map each TabbedContent ID to the ID of its "Add" tab
        self.add_tab_map = {
            "main_tabs":    "add_main",
            "small_tabs_1": "add_small_1",
            "small_tabs_2": "add_small_2",
            "medium_tabs":  "add_medium",
        }

    def compose(self) -> ComposeResult:
        """Creates UI layout"""
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

        yield Static("Command Input", classes="box command_input")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle both '[+]' Add Tab and 'Delete' button presses."""
        button_id = event.button.id

        if button_id.startswith("add_"):
            # Example: "add_main_tabs" -> tabbed_content_id = "main_tabs"
            tabbed_content_id = button_id.replace("add_", "")
            self.add_tab(tabbed_content_id)
        elif button_id.startswith("delete_"):
            # Format we’ll use: "delete_{tabbed_content_id}_{tab_id}"
            self.delete_tab(button_id)

    def add_tab(self, tabbed_content_id: str) -> None:
        """Dynamically insert a new tab BEFORE the '[+]' tab"""
        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)

        # Increment counter for naming / ID
        self.tab_counters[tabbed_content_id] += 1
        counter_value = self.tab_counters[tabbed_content_id]

        # Build the new tab's ID and title
        new_tab_id = f"{tabbed_content_id}_tab_{counter_value}"
        new_tab_name = f"Tab {counter_value}"

        # We'll create the content for this tab, including a delete button
        new_tab_content = self._create_tab_content(tabbed_content_id, new_tab_id, new_tab_name)

        # Insert the pane before the 'Add' tab so the 'Add' tab is always last
        add_tab_id = self.add_tab_map[tabbed_content_id]
        tabbed_content.add_pane(
            TabPane(new_tab_name, new_tab_content, id=new_tab_id),
            before=add_tab_id,
        )

        # Activate the new tab
        tabbed_content.active = new_tab_id

    def delete_tab(self, delete_button_id: str) -> None:
        """
        Extract tabbed_content_id + tab_id from the delete button ID,
        then remove that tab from the corresponding TabbedContent.
        The button ID has the format: "delete_{tabbed_content_id}_{tab_id}"
        """
        # Example: delete_button_id = "delete_main_tabs_tab_3"
        remainder = delete_button_id[len("delete_"):]

        # Find the tabbed_content_id among known IDs
        for candidate_id in self.add_tab_map.keys():
            prefix = candidate_id + "_"
            if remainder.startswith(prefix):
                # Found which candidate ID is used
                tabbed_content_id = candidate_id
                # The rest of the string after that prefix is the actual tab ID
                tab_id = remainder[len(prefix):]
                break
        else:
            # If none of the known IDs match as a prefix, something is off
            return

        # Now we have tabbed_content_id = "main_tabs"
        # and tab_id = "main_tabs_tab_3"
        tabbed_content = self.query_one(f"#{tabbed_content_id}", TabbedContent)

        # Make sure we don't remove the "Add" tab by accident
        if tab_id == self.add_tab_map[tabbed_content_id]:
            return

        # Remove the specified pane by ID
        tabbed_content.remove_pane(tab_id)


    def _create_tab_content(self, tabbed_content_id: str, tab_id: str, tab_name: str) -> Vertical:
        """
        Builds the content (widgets) inside the newly created tab, including
        a Delete button that knows when clicked which TabbedContent ID and tab ID to remove.
        """
        # Our plan: nest a Static or a container widget that includes
        # the text plus the button. We'll store the "delete" button ID
        # in a known pattern so we can parse it in on_button_pressed.
        delete_button_id = f"delete_{tabbed_content_id}_{tab_id}"

        # Use a Vertical container for the text and the delete button.
        return Vertical(
            Static(f"Content for {tab_name}\n"),
            Button("[x] Delete Tab", id=delete_button_id),
        )
