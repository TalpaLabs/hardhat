from textual.widgets import Static

class WidgetB(Static):
    """Example custom widget B."""
    def __init__(self, text: str = "I am Widget B"):
        super().__init__(text)
