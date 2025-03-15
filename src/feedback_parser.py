import json

class FeedbackParser:
    def __init__(self, data_store):
        self.data_store = data_store

    def parse_feedback(self, feedback):
        """
        Parse the raw feedback (JSON dict or string) and update
        the store accordingly.
        """
        # For example, if raw_data is a dict, you might do:
        if isinstance(feedback, str):
            # possibly convert to dict
            try:
                feedback = json.loads(feedback)
            except:
                pass

        if isinstance(feedback, dict):
            if "message" in feedback:
                self.data_store.latest_response = feedback["message"]
            else:
                self.data_store.latest_response = str(feedback)
        else:
            # If it's not dict, just store its string
            self.data_store.latest_response = str(feedback)
