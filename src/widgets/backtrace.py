from textual.widgets import Static

class Backtrace(Static):
    """
    A widget that displays the backtrace of the debuggee.
    """
    
    def __init__(self, data_store):
        """
        Initialize the Backtrace widget.

        Args:
            data_store: An object that provides register data through the `get_registers` method.
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
        Update the widget's content with the latest backtrace.

        This method retrieves backtrace data from the data store using the `get_backtrace` method
        and updates the widget's display with this information.
        """
        self.update(self.data_store.get_backtrace())
