from textual.widgets import Static

class ResponseDisplay(Static):
    """Displays responses from CoreMiner"""
    def update_response(self, message: str):
        self.update(f"Response: {message}")
