from textual.widgets import Input

class CommandInput(Input):
    """Simple input field"""
    def __init__(self):
        super().__init__(placeholder="Type command...")
