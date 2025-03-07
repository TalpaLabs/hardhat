from textual.widgets import Static

class WidgetC(Static):
    """Example custom widget C."""
    def __init__(self, text: str = "I am Widget C"):
        super().__init__(text)