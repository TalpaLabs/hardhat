from textual.widgets import Static

class Output(Static):
    """
    A widget for displaying general responses from CoreMiner that do not have a specific widget.

    This widget retrieves the output from a provided data store and displays it.
    Markup rendering is disabled to ensure that raw text output is shown.
    After updating the content, the widget's parent container is scrolled to the bottom to allways show the newest entry.
    """
    
    def __init__(self, data_store):
        """
        Initialize the Output widget.

        Args:
            data_store: An object that provides debuggee output data through the `get_output` method.
        """
        super().__init__()
        self.data_store = data_store
        self._render_markup = False
        
    def on_mount(self):
        """
        Called when the widget is mounted on the screen.

        This method triggers the initial content update upon widget mounting.
        """
        self.update_content()

    def update_content(self):
        """
        Update the widget's content and scroll to the bottom.

        This method retrieves the latest output from the data store using `get_output`,
        updates the display with this output, and scrolls the parent container to the bottom without animation.
        """
        self.update(self.data_store.get_output())
        self.parent.scroll_end(animate=False)
