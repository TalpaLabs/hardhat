from textual.widgets import Static

class Disassembly(Static):
    """
    A widget that displays disassembly output from CoreMiner.

    This widget retrieves disassembly data from a provided data store and updates its display accordingly.
    Markup rendering is disabled to ensure that the raw disassembly text is shown.
    """

    def __init__(self, data_store):
        """
        Initialize the Disassembly widget.

        Args:
            data_store: An object providing disassembly information, expected to have a method `get_disassembly`
                        that returns the disassembly text as a string.
        """
        super().__init__()
        self.data_store = data_store
        self._render_markup = False
        
    def on_mount(self):
        """
        Called when the widget is mounted on the screen.

        This method triggers the initial update of the widget's content.
        """
        self.update_content()

    def update_content(self):
        """
        Update the widget's content with the latest disassembly output.

        This method retrieves disassembly data from the data store using `get_disassembly` and updates the
        widget's display accordingly.
        """
        self.update(self.data_store.get_disassembly())
