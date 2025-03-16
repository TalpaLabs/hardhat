from textual.widgets import Static
from textual.containers import VerticalScroll

class RawResponses(Static):
    """Displays responses from CoreMiner"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.scroll_container: VerticalScroll | None = None
        
    def on_mount(self):
        self.update_content()

    def update_content(self):
        """Update content and scroll to bottom"""
        self.update(f"{self.data_store.get_responses_coreminer()}")
        self.parent.scroll_end(animate=False)

