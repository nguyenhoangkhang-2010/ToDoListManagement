import tkinter as tk
import json
import os
from auth_manager import AuthManager
from tkinter import messagebox, ttk

class JSONHandler:
    def __init__(self, username= None, role = None):
        self.current_user = username
        self.current_role = role
    
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
        global current_user
        filename = self.get_data_file()
        with open(filename, "w", encoding= "utf-8") as f:
            json.dump(data, f, indent=4)

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
            status = "✅ Hoàn thành" if task.get("done") else "❌ Chưa hoàn thành"
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