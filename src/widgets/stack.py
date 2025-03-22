from textual.widgets import Static

class Stack(Static):
    """
    A widget that displays the current stack of the debuggee.

    This widget retrieves stack data from a provided data store and updates its display with the latest
    stack information.
    """
    
    def __init__(self, data_store):
        """
        Initialize the Stack widget.

        Args:
            data_store: An object that provides stack data through the `get_stack` method.
        """
        super().__init__()
        self.data_store = data_store
        self._render_markup = False
        
    def on_mount(self):
        """
        Called when the widget is mounted on the screen.

        This method triggers the initial update of the widget's content by calling `update_content`.
        """
        self.update_content()

    def update_content(self):
        """
        Update the widget's content with the current stack information.

        This method retrieves stack data from the data store using the `get_stack` method
        and updates the widget's display with the retrieved information.
        """
        self.update(self.data_store.get_stack())
