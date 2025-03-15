from typing import Optional

class DataStore:
    """
    A container for all shared state/data.
    Widgets can query this to get the information they need.
    """

    def __init__(self):
        self.latest_response: Optional[str] = None
        # Add any other shared data here, e.g.:
        # self.user_info = {}
        # self.some_list = []

    def set_latest_response(self, response: str) -> None:
        self.latest_response = response
