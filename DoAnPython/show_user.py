import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from tkcalendar import DateEntry
from datetime import datetime

class ShowUser:    
    def admin_view_tasks(self):
        users = self.load_users()
        if not users:
            messagebox.showinfo("Thông báo", "Chưa có tài khoản nào.")
            return

        select_window = tk.Toplevel()
        select_window.title("Chọn người dùng để xem công việc")
        select_window.geometry("300x400")

        tk.Label(select_window, text="Chọn người dùng:", font=("Arial", 12, "bold")).pack(pady=10)

        search_var = tk.StringVar()
        search_entry = tk.Entry(select_window, textvariable=search_var)
        search_entry.pack(fill="x", padx=10)

        def filter_users():
            keyword = search_var.get().strip().lower()
            user_listbox.delete(0, tk.END)
            for username in users.keys():
                if keyword in username.lower():
                    user_listbox.insert(tk.END, username)

        tk.Button(select_window, text="Tìm kiếm", command=filter_users).pack(pady=5)

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
        all_tasks = self.load_data()
        if not all_tasks:
            messagebox.showinfo("Thông báo", "Chưa có công việc nào.")
            return
        
        data = []
        for task in all_tasks:
            assigned = task.get("assigned_to", [])
            if isinstance(assigned, str):
                assigned = [assigned]

            if username in assigned or username == task.get("created_by"):
                # Chỉ hiện nếu người được xem là chính admin HOẶC nếu user nằm trong danh sách assigned
                if username == task.get("created_by"):
                    if username in assigned:
                        data.append(task)
                elif username in assigned:
                    data.append(task)

        if not data:
            messagebox.showinfo("Thông báo", f"Người dùng {username} chưa có công việc.")
            return

        view_window = tk.Toplevel()
        view_window.title(f"Công việc của {username}")
        view_window.state("zoomed")

        top_frame = tk.Frame(view_window)
        top_frame.pack(fill="x", pady=5)

        back_button = tk.Button(top_frame, text="Quay lại", font=("Arial", 10, "bold"), command=lambda: [view_window.destroy(), self.admin_view_tasks()])
        back_button.pack(side="left", padx=10)

        tk.Label(view_window, text=f"Người dùng: {username}", font=("Arial", 12, "bold")).pack(pady=5)

        filter_frame = tk.Frame(view_window)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Tên công việc:").pack(side="left")
        title_entry = tk.Entry(filter_frame)
        title_entry.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Từ ngày:").pack(side="left")
        start_date_entry = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        start_date_entry.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Đến ngày:").pack(side="left")
        end_date_entry = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        end_date_entry.pack(side="left", padx=5)

        columns = ("Tiêu đề", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái",
                "Ưu tiên", "Tình trạng", "Danh mục", "Phân công cho")
        tree = ttk.Treeview(view_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Mô tả" else 250)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_filtered_data():
            keyword = title_entry.get().strip().lower()
            start_filter = start_date_entry.get_date()
            end_filter = end_date_entry.get_date()

            tree.delete(*tree.get_children())

            for task in data:
                title = task.get("title", "")
                description = task.get("description", "")
                start_str = task.get("start_date", "")
                end_str = task.get("deadline", "")
                status_display = "Hoàn thành" if task.get("done") else "Chưa hoàn thành"
                priority = task.get("priority", "")
                status = task.get("status", "")
                category = task.get("category", "")
                assigned = task.get("assigned_to", "")

                try:
                    end_dt = datetime.strptime(end_str, "%d-%m-%Y").date() if end_str else None
                except:
                    continue

                if keyword and keyword not in title.lower():
                    continue

                try:
                    start_dt = datetime.strptime(start_str, "%d-%m-%Y").date() if start_str else None
                    end_dt = datetime.strptime(end_str, "%d-%m-%Y").date() if end_str else None
                except:
                    continue

                # Nếu cả hai ngày đều không hợp lệ thì bỏ qua
                if not start_dt and not end_dt:
                    continue

                # Kiểm tra xem *bắt đầu hoặc kết thúc* có nằm trong khoảng lọc không
                if not (
                    (start_dt and start_filter <= start_dt <= end_filter) or
                    (end_dt and start_filter <= end_dt <= end_filter)
                ):
                    continue

                tree.insert("", "end", values=(
                    title, description, start_str, end_str,
                    status_display, priority, status, category, assigned
                ))

        tk.Button(filter_frame, text="Tìm kiếm", command=load_filtered_data).pack(side="left", padx=10)

        load_filtered_data()

    def show_user_list(self):
        users = self.load_users()

        user_window = tk.Toplevel()
        user_window.title("Danh sách tài khoản")
        user_window.geometry("400x350")

        search_frame = tk.Frame(user_window)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Tìm kiếm:").pack(side="left")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        tree = ttk.Treeview(user_window, columns=("Username", "Role"), show="headings")
        tree.heading("Username", text="Tên đăng nhập")
        tree.heading("Role", text="Vai trò")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def update_tree(*args):
            keyword = search_var.get().lower()

            for item in tree.get_children():
                tree.delete(item)

            for username, info in users.items():
                if keyword in username.lower() or keyword in info.get("role", "").lower():
                    tree.insert("", "end", values=(username, info.get("role", "")))
        search_var.trace_add("write", update_tree)
        update_tree()

    def update_task_tree(self, tasks):
        self.show_task_list(tasks)