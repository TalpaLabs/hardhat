from typing import Optional

class DataStore:
    """
    A container for all shared state/data.
    Widgets can query this to get the information they need.
    """

    def __init__(self):
        self.responses_coreminer: Optional[str] = None

    def set_responses_coreminer(self, response: str) -> None:
        """Appends the new response instead of replacing."""
        if self.responses_coreminer:
            self.responses_coreminer += f"\n{response}"
        else:
            self.responses_coreminer = response

    def get_responses_coreminer(self) -> Optional[str]:
        """Retrieve the latest response."""
        return self.responses_coreminer
