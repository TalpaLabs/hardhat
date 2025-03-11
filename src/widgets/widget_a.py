from textual.widgets import Static

class WidgetA(Static):
    """Example custom widget A."""
    def __init__(self, text: str = "I am Widget A"):
        super().__init__(text)
