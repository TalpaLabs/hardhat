import json

class FeedbackParser:
    def __init__(self, data_store):
        self.data_store = data_store

    def parse_feedback(self, feedback_dict):
        """
        Parse the raw feedback (JSON dict or string) and update
        the store accordingly.
        """
        # For example, if raw_data is a dict, you might do:
        if isinstance(feedback_dict, str):
            # possibly convert to dict
            try:
                feedback_dict = json.loads(feedback_dict)
            except:
                pass

        if isinstance(feedback_dict, dict):
            if "message" in feedback_dict:
                self.data_store.latest_response = feedback_dict["message"]
            else:
                self.data_store.latest_response = str(feedback_dict)
        else:
            # If it's not dict, just store its string
            self.data_store.latest_response = str(feedback_dict)
