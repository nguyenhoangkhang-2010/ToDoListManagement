import json
import os
from tkinter import messagebox

class JSONHandler:
    DATA_FILE = "tasks.json" 

    def get_data_file(self, username=None):
        if username is None:
            return self.DATA_FILE
        return f"data_{username}.json"

    def load_data(self, username=None):
        filename = self.get_data_file(username)
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self, data, username=None):
        filename = self.get_data_file(username)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_task(self, task):
        tasks = self.load_data()
        for t in tasks:
            if t["title"] == task["title"]:
                messagebox.showwarning("Cảnh báo", "Công việc đã tồn tại!")
                return False
        tasks.append(task)
        self.save_data(tasks)
        assigned_users = task.get("assigned_to", [])
        for username in assigned_users:
            user_tasks = self.load_data(username)
            if any(t.get("title") == task["title"] for t in user_tasks):
                continue
            user_tasks.append(task)
            self.save_data(user_tasks, username)
        messagebox.showinfo("Thành công", "Đã thêm công việc và cập nhật cho user.")
        return True