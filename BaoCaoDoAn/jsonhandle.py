import json
import os

class JSONHandler:
    def get_data_file(self, username=None):
        if username is None:
            username = self.current_user
        return f"data_{username}.json"

    def load_data(self):
        filename = self.get_data_file()
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self, data):
        filename = self.get_data_file()
        with open(filename, "w", encoding= "utf-8") as f:
            json.dump(data, f, indent=4)