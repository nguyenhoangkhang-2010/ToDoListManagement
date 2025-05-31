import json
import os

class AuthManager:
    USERS_FILE = "users.json"
    def load_users(self):
        if not os.path.exists(self.USERS_FILE):
            return {}
        with open(self.USERS_FILE, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.USERS_FILE, "w") as f:
            json.dump(users, f)