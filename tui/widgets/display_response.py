from textual.widgets import Static

class ResponseDisplay(Static):
    """Displays responses from CoreMiner"""
    def update_content(self, message: str):
        self.update(f"Response: {message}")
