from tkinter import messagebox

class CheckData():
    def check_data_exists(self):
        data = self.load_data()
        messagebox.showinfo("Thông tin", f"Tìm thấy {len(data)} công việc" if data else "Không có dữ liệu")

    def load_all_tasks(self):
        return self.load_data()
    
    def refresh_data(self):
        if hasattr(self, 'task_tree'):
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            tasks = self.load_data()  # Hoặc self.user_crud.load_data() nếu bạn chắc chắn user_crud có load_data()
            for task in tasks:
                assigned_to_str = ", ".join(task.get("assigned_to", [])) if isinstance(task.get("assigned_to"), list) else task.get("assigned_to", "")
                created_by = task.get("created_by", "Không rõ")
                self.task_tree.insert("", "end", values=(
                    task.get("title", ""),
                    task.get("description", ""),
                    task.get("start_date", ""),
                    task.get("deadline", ""),
                    task.get("priority", ""),
                    task.get("status", ""),
                    task.get("category", ""),
                    assigned_to_str,
                    created_by
                ))
