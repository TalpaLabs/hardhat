from textual.widgets import Static

class RawResponses(Static):
    """
    A widget for displaying the raw JSON responses received from CoreMiner via HardHat.

    This widget retrieves JSON response data from a provided data store and displays it as raw text.
    Markup rendering is disabled to ensure the JSON is shown exactly as it is received. Once the content
    is updated, the parent container is scrolled to the bottom to reveal the latest output.
    """
    
    def __init__(self, data_store):
        """
        Initialize the RawResponses widget.

        Args:
            data_store: An object that provides JSON responses through the `get_responses_coreminer` method.
        """
        super().__init__()
        self.data_store = data_store
        self._render_markup = False
        
    def on_mount(self):
        """
        Called when the widget is mounted on the screen.

        This method triggers the initial content update for displaying the raw JSON responses.
        """
        self.update_content()

    def update_content(self):
        """
        Update the widget's content with the latest JSON responses and scroll to the bottom.

        This method retrieves the raw JSON responses from the data store using the `get_responses_coreminer`
        method, updates the display with this information, and scrolls the parent container to the bottom
        without animation.
        """
        self.update(self.data_store.get_responses_coreminer())
        self.parent.scroll_end(animate=False)
