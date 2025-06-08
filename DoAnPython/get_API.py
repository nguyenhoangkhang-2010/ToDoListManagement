import requests
from datetime import date
from tkinter import messagebox
import json
import os

class GetApi:
    DATA_FILE = "tasks.json"

    def load_data(self):
        if not os.path.exists(self.DATA_FILE):
            return []
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_data(self, data):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def fetch_data_from_api(self, current_user):
        url = "https://api.todoist.com/rest/v2/tasks"
        headers = {
            "Authorization": "Bearer a66c26fae63662a12f8ca43e996735490339f867"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            todoist_tasks = response.json()

            existing_data = self.load_data()
            # Phải so sánh thêm assigned_to để tránh trùng task giữa các user
            existing_task_keys = set((task.get("title"), task.get("deadline"), task.get("assigned_to")) for task in existing_data)

            new_tasks = []
            for task in todoist_tasks:
                title = task.get("content", "")
                description = task.get("description", "") or "Không có mô tả"
                deadline_raw = task.get("due", {}).get("date", "")
                deadline = ""
                if deadline_raw:
                    try:
                        deadline = date.fromisoformat(deadline_raw).strftime("%d-%m-%Y")
                    except ValueError:
                        deadline = deadline_raw

                start_date = date.today().strftime("%d-%m-%Y")

                priority_level = {
                    4: "Cao",
                    3: "Trung bình",
                    2: "Thấp",
                    1: "Thấp"
                }
                priority = priority_level.get(task.get("priority", 1), "Thấp")

                status = "Chưa hoàn thành"
                category = "Công việc"
                assigned_to = current_user  # Gán cho người đang lấy dữ liệu

                task_key = (title, deadline, assigned_to)
                if task_key not in existing_task_keys:
                    new_tasks.append({
                        "title": title,
                        "description": description,
                        "start_date": start_date,
                        "deadline": deadline,
                        "priority": priority,
                        "status": status,
                        "category": category,
                        "assigned_to": assigned_to
                    })

            if new_tasks:
                combined_data = existing_data + new_tasks
                self.save_data(combined_data)
                messagebox.showinfo("Thành công", f"Đã thêm {len(new_tasks)} task mới từ Todoist.")
            else:
                messagebox.showinfo("Thông báo", "Không có task mới từ Todoist.")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu từ Todoist:\n{e}")