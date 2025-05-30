import json
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import *
import hashlib

class AuthManager:
    USERS_FILE = "users.json"

# ======= QUẢN LÝ USER ===========
    def __init__(self):
        self.current_users = None
        self.current_role = None

    def load_users(self):
        if not os.path.exists(self.USERS_FILE):
            return {}
        with open(self.USERS_FILE, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.USERS_FILE, "w") as f:
            json.dump(users, f)