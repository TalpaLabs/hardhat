from textual.widgets import Static

class ResponseDisplay(Static):
    """Displays responses from CoreMiner"""
    def update_content(self):

        data_store = self.screen.data_store
        self.update(f"Response: {data_store.latest_response}")
