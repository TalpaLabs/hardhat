from textual.containers import Container
from textual.widgets import Select, Static

class BaseContainer(Container):
    """A container that can be resized and display different types of content."""
    
    def __init__(self, title: str):
        super().__init__()
        self.title = title

    def compose(self):
        """Defines the resizable container layout."""
        yield Static(f"{self.title} (Resize me!)", id="title")
        yield Select(
            options=[
                ("Show Logs", "logs"),
                ("Show Debug Info", "debug"),
                ("Show Stats", "stats"),
            ],
            id="content_selector"
        )
        yield Static("", id="content_display")

    def on_mount(self):
        """Set up event handlers for dynamic content switching."""
        self.query_one("#content_selector").on_change = self.update_content

    def update_content(self, event):
        """Updates displayed content based on user selection."""
        selection = event.value
        content_display = self.query_one("#content_display")

        if selection == "logs":
            content_display.update("Displaying logs...")
        elif selection == "debug":
            content_display.update("Debugging Information...")
        elif selection == "stats":
            content_display.update("Statistics Panel...")