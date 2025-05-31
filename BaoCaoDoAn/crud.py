import tkinter as tk
import os
import json
from tkinter import messagebox, ttk
from jsonhandle import JSONHandler
from auth_manager import AuthManager
import requests
from todoist_api_python.api import TodoistAPI
from tkcalendar import Calendar
from datetime import date

class BuildCrud (JSONHandler):
    def __init__(self, username, role):
        super().__init__()
        self.current_user = username
        self.current_role = role
        self.auth = AuthManager()

    def load_users(self):
        return self.auth.load_users()

    def delete_data(self):
        data = self.load_data()
        if not data:
            messagebox.showinfo("Thông báo", "Không có công việc để xóa.")
            return

        delete_window = tk.Toplevel()
        delete_window.title("Xóa công việc")
        delete_window.geometry("600x400")

        columns = ("Tiêu đề", "Mô tả", "Hạn chót", "Trạng thái")
        tree = ttk.Treeview(delete_window, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Mô tả" else 220)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, task in enumerate(data):
            status = " Hoàn thành" if task.get("done") else " Chưa hoàn thành"
            tree.insert("", "end", iid=idx, values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("deadline", ""),
                status
            ))

        def delete_task():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn công việc để xóa.")
                return
            idx = int(selected[0])
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa công việc này?")
            if confirm:
                data.pop(idx)
                self.save_data(data)
                messagebox.showinfo("Thành công", "Đã xóa công việc.")
                delete_window.destroy()

        tk.Button(delete_window, text="Xóa công việc", command=delete_task).pack(pady=10)

    def create_data(self):
        def save_new_task():
            title = entry_title.get()
            description = text_desc.get("1.0", tk.END).strip()
            deadline = calendar.get_date()
            done = done_var.get()  

            if not title or not deadline:
                messagebox.showwarning("Thiếu thông tin", "Tên công việc và ngày hết hạn")
                return

            task = {
                "title": title,
                "description": description,
                "deadline": deadline,
                "done": done
            }

            data = self.load_data()
            data.append(task)
            self.save_data(data)
            messagebox.showinfo("Thành công", "Đã thêm công việc mới!")
            window_create.destroy()

        window_create = tk.Toplevel()
        window_create.title("Tạo công việc mới")
        window_create.geometry("400x450")

        tk.Label(window_create, text="Tên công việc:").pack()
        entry_title = tk.Entry(window_create)
        entry_title.pack(fill="x", padx=10)

        tk.Label(window_create, text="Mô tả:").pack()
        text_desc = tk.Text(window_create, height=5)
        text_desc.pack(fill="x", padx=10)

        tk.Label(window_create, text="Hạn chót (DD-MM-YYYY):").pack()
        calendar = Calendar(window_create, selectmode='day', mindate=date.today(), date_pattern="dd-mm-yyyy", showothermonthdays=False)
        calendar.pack(pady=5)

        done_var = tk.BooleanVar()
        tk.Checkbutton(window_create, text="Đã hoàn thành", variable=done_var).pack(pady=5)

        tk.Button(window_create, text="Lưu", command=save_new_task).pack(pady=10)

    def read_data(self):
        data = self.load_data()
        if not data:
            messagebox.showinfo("Thông báo", "Không có công việc nào.")
            return

        view_window = tk.Toplevel()
        view_window.title("Danh sách công việc")
        view_window.geometry("1000x600")

        columns = ("Tiêu đề", "Mô tả", "Hạn chót", "Trạng thái")
        tree = ttk.Treeview(view_window, columns=columns, show="headings")

        columns = ("Tiêu đề", "Mô tả", "Hạn chót", "Trạng thái")
        tree = ttk.Treeview(view_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col != "Mô tả" else 250)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, task in enumerate(data):
            status = " Hoàn thành" if task.get("done") else " Chưa hoàn thành"
            tree.insert("", "end", iid=idx, values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("deadline", ""),
                status
            ))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def update_data(self):
        data = self.load_data()
        if not data:
            messagebox.showinfo("Thông báo", "Không có công việc để cập nhật.")
            return

        update_window = tk.Toplevel()
        update_window.title("Cập nhật trạng thái công việc")
        update_window.geometry("600x400")

        columns = ("Tiêu đề", "Mô tả", "Hạn chót", "Trạng thái")
        tree = ttk.Treeview(update_window, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Mô tả" else 220)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, task in enumerate(data):
            status = "Hoàn thành" if task.get("done") else "Chưa hoàn thành"
            tree.insert("", "end", iid=idx, values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("deadline", ""),
                status
            ))

        # Checkbox cập nhật trạng thái
        done_var = tk.BooleanVar()

        def on_select(event):
            selected = tree.selection()
            if selected:
                idx = int(selected[0])
                done_var.set(data[idx].get("done", False))

        tree.bind("<<TreeviewSelect>>", on_select)

        tk.Label(update_window, text="Đánh dấu hoàn thành:").pack(pady=5)
        cb_done = tk.Checkbutton(update_window, variable=done_var)
        cb_done.pack()

        def save_update():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn công việc cần cập nhật.")
                return

            idx = int(selected[0])
            data[idx]["done"] = done_var.get()
            self.save_data(data)
            messagebox.showinfo("Thành công", "Cập nhật trạng thái thành công!")
            update_window.destroy()

        tk.Button(update_window, text="Lưu cập nhật", command=save_update).pack(pady=10)

    def admin_view_tasks(self):
        users = self.load_users()
        if not users:
            messagebox.showinfo("Thông báo", "Chưa có tài khoản nào.")
            return

        select_window = tk.Toplevel()
        select_window.title("Chọn người dùng để xem công việc")
        select_window.geometry("300x400")

        tk.Label(select_window, text="Chọn người dùng:", font=("Arial", 12, "bold")).pack(pady=10)

        user_listbox = tk.Listbox(select_window)
        user_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for username in users.keys():
            user_listbox.insert(tk.END, username)

        def view_selected_user_tasks():
            selected = user_listbox.curselection()
            if not selected:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn người dùng.")
                return
            username = user_listbox.get(selected[0])
            select_window.destroy()
            self.show_tasks_of_user(username)

        tk.Button(select_window, text="Xem công việc", command=view_selected_user_tasks).pack(pady=10)

    def show_tasks_of_user(self, username):
        filename = self.get_data_file(username)
        if not os.path.exists(filename):
            messagebox.showinfo("Thông báo", f"Người dùng {username} chưa có công việc.")
            return

        with open(filename, "r") as f:
            data = json.load(f)

        view_window = tk.Toplevel()
        view_window.title(f"Công việc của {username}")
        view_window.geometry("800x400")

        tk.Label(view_window, text=f"Người dùng: {username}", font=("Arial", 12, "bold")).pack(pady=5)
        columns = ("Tiêu đề", "Mô tả", "Hạn chót", "Trạng thái")
        tree = ttk.Treeview(view_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col != "Mô tả" else 250)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, task in enumerate(data):
            status = "Hoàn thành" if task.get("done") else "Chưa hoàn thành"
            tree.insert("", "end", iid=idx, values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("deadline", ""),
                status
            ))

    def show_user_list(self):
        users = self.load_users()

        user_window = tk.Toplevel()
        user_window.title("Danh sách tài khoản")
        user_window.geometry("400x300")

        tree = ttk.Treeview(user_window, columns=("Username", "Role"), show="headings")
        tree.heading("Username", text="Tên đăng nhập")
        tree.heading("Role", text="Vai trò")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for username, info in users.items():
            tree.insert("", "end", values=(username, info["role"]))
        
    def fetch_data_from_api(self):
        url = "https://api.todoist.com/rest/v2/tasks"
        headers = {
            "Authorization": f"Bearer a66c26fae63662a12f8ca43e996735490339f867"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            todoist_tasks = response.json()

            # Dữ liệu hiện tại
            existing_data = self.load_data()

            # Tạo set chứa (title, deadline) của các task đã có để tránh trùng
            existing_task_keys = set(
                (task.get("title"), task.get("deadline")) for task in existing_data
            )

            new_tasks = []
            for task in todoist_tasks:
                title = task.get("content", "")
                deadline_raw = task.get("due", {}).get("date", "")
                deadline = ""
                if deadline_raw:
                    try:
                        deadline = date.fromisoformat(deadline_raw).strftime("%d-%m-%Y")
                    except ValueError:
                        deadline = deadline_raw

                task_key = (title, deadline)

                if task_key not in existing_task_keys:
                    new_tasks.append({
                        "title": title,
                        "description": task.get("description", ""),
                        "deadline": deadline,
                        "done": False
                    })

            # Thêm task mới nếu có
            if new_tasks:
                combined_data = existing_data + new_tasks
                self.save_data(combined_data)
                messagebox.showinfo("Thành công", f"Đã thêm {len(new_tasks)} task mới từ Todoist. Các task còn lại đã tồn tại.")
            else:
                messagebox.showinfo("Thông báo", "Tất cả các task từ Todoist đã tồn tại. Không có task mới được thêm.")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy API Todoist:\n{e}")