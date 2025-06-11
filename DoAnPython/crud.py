import tkinter as tk
import os
import json
from tkinter import messagebox, ttk
from json_handle import JSONHandler
from show_user import ShowUser
from auth_manager import AuthManager
from get_API import GetApi
from check_data import CheckData
from tkcalendar import DateEntry
from datetime import date, datetime

class BuildCrud (JSONHandler, ShowUser, CheckData, GetApi):
    def __init__(self, username, role):
        self.current_user = username
        self.current_role = role
        self.display_frame = None
        self.auth = AuthManager()

    def set_display_frame(self, parent_frame):
        # Frame tìm kiếm
        self.search_frame = tk.Frame(parent_frame, bg="white")
        self.search_frame.pack(fill="x", padx=5, pady=5)

        # Tên công việc
        tk.Label(self.search_frame, text="Tìm tên công việc:", bg="white").pack(side="left", padx=(10, 2))
        self.search_title_entry = tk.Entry(self.search_frame)
        self.search_title_entry.pack(side="left", padx=5)

        # Ngày bắt đầu
        tk.Label(self.search_frame, text="Từ ngày:", bg="white").pack(side="left", padx=(10, 2))
        self.search_start_date = DateEntry(self.search_frame, date_pattern="dd-mm-yyyy")
        self.search_start_date.pack(side="left", padx=5)

        # Ngày kết thúc
        tk.Label(self.search_frame, text="Đến ngày:", bg="white").pack(side="left", padx=(10, 2))
        self.search_end_date = DateEntry(self.search_frame, date_pattern="dd-mm-yyyy")
        self.search_end_date.pack(side="left", padx=5)

        # Nút tìm kiếm
        tk.Button(self.search_frame, text="Tìm kiếm", command=self.search_tasks).pack(side="left", padx=10)

        # Frame hiển thị
        self.display_frame = tk.Frame(parent_frame, bg="white")
        self.display_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def clear_display(self):
        if self.display_frame:
            for widget in self.display_frame.winfo_children():
                widget.destroy()

    def load_users(self):
        return self.auth.load_users()

    def delete_data(self):
        if not hasattr(self, "task_tree") or not self.task_tree.get_children():
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu để thực hiện việc xóa.")
            return

        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn công việc để xóa.")
            return

        selected_iid = selected[0]
        values = self.task_tree.item(selected_iid)["values"]

        if not values or len(values) < 3:
            messagebox.showerror("Lỗi", "Không thể xác định công việc cần xóa.")
            return

        task_title = values[0]
        task_deadline = values[3]

        data = self.load_data()

        index_to_delete = -1
        for idx, task in enumerate(data):
            if task.get("title") == task_title and task.get("deadline") == task_deadline:
                # Kiểm tra quyền xóa
                assigned_to = task.get("assigned_to", [])
                if isinstance(assigned_to, str):
                    assigned_to = [assigned_to]

                # Nếu không phải admin và công việc không phải do chính mình thì không được xóa
                if self.current_role != "admin" and self.current_user not in assigned_to:
                    messagebox.showwarning("Không được phép", "Bạn không thể xóa công việc được phân công bởi người khác.")
                    return

                index_to_delete = idx
                break

        if index_to_delete == -1:
            messagebox.showerror("Lỗi", "Không tìm thấy công việc trong dữ liệu.")
            return

        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa công việc '{task_title}'?")
        if not confirm:
            return

        data.pop(index_to_delete)
        self.save_data(data)
        self.task_tree.delete(selected_iid)
        self.clear_display()
        self.show_task_list(data)

        messagebox.showinfo("Thành công", f"Đã xóa công việc '{task_title}'.")

    def create_data(self):
        def load_user_list_from_json(file_path="users.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    users = json.load(f)
                return list(users.keys())
            except Exception as e:
                print("Lỗi khi đọc users.json:", e)
                return []

        user_list = load_user_list_from_json()  # Load danh sách người dùng

        def save_new_task():
            title = entry_title.get()
            description = text_desc.get("1.0", tk.END).strip()
            start_date = date_entry_start.get_date()
            end_date = date_entry_end.get_date()
            priority = combo_priority.get()
            status = combo_status.get()
            category = combo_category.get()

            # Lấy nhiều người được phân công
            if self.current_role == "admin":
                selected_indices = listbox_assigned_to.curselection()
                if not selected_indices:
                    messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ít nhất một người được phân công.")
                    return
                assigned_to = [listbox_assigned_to.get(i) for i in selected_indices]
            else:
                assigned_to = [self.current_user]

            if not title:
                messagebox.showwarning("Thiếu thông tin", "Tên công việc không được để trống.")
                return

            if start_date > end_date:
                messagebox.showwarning("Lỗi ngày", "Ngày bắt đầu không được lớn hơn ngày kết thúc!")
                return

            data = self.load_data()

            for existing_task in data:
                if existing_task.get("title") == title:
                    existing_assigned = existing_task.get("assigned_to", [])
                    if isinstance(existing_assigned, str):
                        existing_assigned = [existing_assigned]

                    if set(existing_assigned).intersection(set(assigned_to)):
                        messagebox.showwarning("Trùng công việc", f"Công việc với tên '{title}' đã tồn tại cho người được phân công.")
                        return

            task = {
                "title": title,
                "description": description,
                "start_date": start_date.strftime("%d-%m-%Y"),
                "deadline": end_date.strftime("%d-%m-%Y"),
                "priority": priority,
                "status": status,
                "category": category,
                "assigned_to": assigned_to,
                "created_by": self.current_user
            }

            data.append(task)
            self.save_data(data)
            messagebox.showinfo("Thành công", "Đã thêm công việc mới!")
            window_create.destroy()

            # Hiển thị trên treeview hoặc tạo mới list
            if hasattr(self, "task_tree") and self.task_tree.winfo_exists():
                self.task_tree.insert("", "end", values=(
                    task["title"],
                    task["description"],
                    task["start_date"],
                    task["deadline"],
                    task["priority"],
                    task["status"],
                    task["category"],
                    ", ".join(task["assigned_to"]),
                    task["created_by"]
                ))
            else:
                self.show_task_list([task])

        window_create = tk.Toplevel()
        window_create.title("Tạo công việc mới")
        window_create.state("zoomed")

        tk.Label(window_create, text="Tên công việc:").pack(pady=(10, 0))
        entry_title = tk.Entry(window_create)
        entry_title.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(window_create, text="Mô tả:").pack()
        text_desc = tk.Text(window_create, height=5)
        text_desc.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(window_create, text="Ngày bắt đầu:").pack()
        date_entry_start = DateEntry(window_create, date_pattern='dd-mm-yyyy', mindate=date.today())
        date_entry_start.pack(pady=5)

        tk.Label(window_create, text="Ngày kết thúc:").pack()
        date_entry_end = DateEntry(window_create, date_pattern='dd-mm-yyyy', mindate=date.today())
        date_entry_end.pack(pady=5)

        tk.Label(window_create, text="Mức độ ưu tiên:").pack()
        combo_priority = ttk.Combobox(window_create, values=["Cao", "Trung bình", "Thấp"])
        combo_priority.current(1)
        combo_priority.pack(fill="x", padx=10, pady=5)

        tk.Label(window_create, text="Trạng thái:").pack()
        combo_status = ttk.Combobox(window_create, values=["Đang làm", "Hoàn thành", "Hoãn", "Chưa hoàn thành"])
        combo_status.current(0)
        combo_status.pack(fill="x", padx=10, pady=5)

        tk.Label(window_create, text="Danh mục:").pack()
        combo_category = ttk.Combobox(window_create, values=["Cá nhân", "Công việc", "Học tập"])
        combo_category.current(0)
        combo_category.pack(fill="x", padx=10, pady=5)

        if self.current_role == "admin":
        # Admin được phân công nhiều người
            tk.Label(window_create, text="Phân công cho (chọn 1 hoặc nhiều):").pack()
            listbox_assigned_to = tk.Listbox(window_create, selectmode="multiple", height=6)
            for user in user_list:
                listbox_assigned_to.insert(tk.END, user)
            listbox_assigned_to.pack(fill="x", padx=10, pady=5)
        else:
            listbox_assigned_to = None  # Không tạo Listbox cho user

        tk.Button(window_create, text="Lưu", command=save_new_task).pack(pady=10)

    def show_task_list(self, tasks):
        if not self.display_frame:
            return

        # Khai báo các cột đầy đủ, thêm "Người tạo"
        columns = ("Tiêu đề", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc",
                "Ưu tiên", "Trạng thái", "Danh mục", "Phân công cho", "Người tạo")

        # Tạo Treeview nếu chưa có hoặc đã bị destroy
        if not hasattr(self, 'task_tree') or not self.task_tree.winfo_exists():
            self.task_tree = ttk.Treeview(self.display_frame, columns=columns, show="headings")

            for col in columns:
                self.task_tree.heading(col, text=col)

                if col == "Mô tả":
                    self.task_tree.column(col, width=200)
                elif col in ("Ngày bắt đầu", "Ngày kết thúc"):
                    self.task_tree.column(col, width=110)
                elif col == "Phân công cho":
                    self.task_tree.column(col, width=130)
                elif col == "Người tạo":
                    self.task_tree.column(col, width=100)
                elif col in ("Ưu tiên", "Trạng thái", "Danh mục"):
                    self.task_tree.column(col, width=100)
                else:
                    self.task_tree.column(col, width=120)

            self.task_tree.pack(fill="both", expand=True)

        else:
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

        for task in tasks:
            assigned_to_str = ", ".join(task.get("assigned_to", [])) if isinstance(task.get("assigned_to"), list) else task.get("assigned_to", "")

            if "created_by" not in task:
                task["created_by"] = "Không rõ"

            self.task_tree.insert("", "end", values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("start_date", ""),
                task.get("deadline", ""),
                task.get("priority", ""),
                task.get("status", ""),
                task.get("category", ""),
                assigned_to_str,
                task["created_by"]
            ))

    def normalize_tasks(self, tasks):
        for task in tasks:
            # Chuẩn hóa assigned_to luôn là list không rỗng hoặc list rỗng
            assigned = task.get("assigned_to", [])
            if isinstance(assigned, str):
                assigned = assigned.strip()
                if assigned == "":
                    assigned = []
                else:
                    assigned = [assigned]
            elif not isinstance(assigned, list):
                assigned = []
            task["assigned_to"] = assigned

            # Đảm bảo có trường created_by, nếu không có gán "admin" hoặc giá trị mặc định
            if "created_by" not in task or not task["created_by"]:
                task["created_by"] = "admin"

        return tasks

    def read_data(self):
        data = self.load_data()
        print("Tổng công việc:", len(data) if data else 0)

        if not data:
            messagebox.showinfo("Thông báo", "Không có công việc nào.")
            return

        data = self.normalize_tasks(data)

        # Nếu là admin, xem được toàn bộ công việc
        if self.current_role == "admin":
            self.clear_display()
            self.show_task_list(data)
            return

        # Nếu là user, chỉ xem được công việc được phân công cho mình
        current_user = self.current_user.strip()
        filtered_data = []

        for task in data:
            assigned_to = task.get("assigned_to", [])
            if isinstance(assigned_to, str):
                assigned_to = [assigned_to.strip()]
            elif not isinstance(assigned_to, list):
                assigned_to = []

            if current_user in assigned_to:
                filtered_data.append(task)

        print(f"Công việc được phân cho '{self.current_user}':", len(filtered_data))

        if not filtered_data:
            messagebox.showinfo("Thông báo", "Bạn chưa được phân công công việc nào.")
            return

        self.clear_display()
        self.show_task_list(filtered_data)

    def update_data(self):
        data = self.load_data()
        if not data:
            messagebox.showinfo("Thông báo", "Không có công việc để cập nhật.")
            return

        def load_user_list_from_json(file_path="users.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    users = json.load(f)
                return list(users.keys())
            except Exception as e:
                print("Lỗi khi đọc users.json:", e)
                return []

        user_list = load_user_list_from_json()

        update_window = tk.Toplevel()
        update_window.title("Cập nhật công việc")
        update_window.state("zoomed")

        columns = ("Tiêu đề", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc",
                "Ưu tiên", "Trạng thái", "Danh mục", "Phân công cho")
        tree = ttk.Treeview(update_window, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150 if col != "Mô tả" else 250)
        tree.pack(fill="x", padx=10, pady=10, expand=True)

        def normalize_assigned_to(task):
            assigned = task.get("assigned_to", [])
            if isinstance(assigned, str):
                assigned = assigned.strip()
                assigned = [assigned] if assigned else []
            elif not isinstance(assigned, list):
                assigned = []
            return assigned

        filtered_data = []
        for task in data:
            if self.current_role == "admin" or task.get("created_by") == self.current_user:
                filtered_data.append(task)

        for idx, task in enumerate(filtered_data):
            assigned_to_str = ", ".join(normalize_assigned_to(task))
            tree.insert("", "end", iid=idx, values=(
                task.get("title", ""),
                task.get("description", ""),
                task.get("start_date", ""),
                task.get("deadline", ""),
                task.get("priority", ""),
                task.get("status", ""),
                task.get("category", ""),
                assigned_to_str
            ))

        form_frame = tk.Frame(update_window)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(form_frame, text="Tên công việc:").pack(anchor="w")
        entry_title = tk.Entry(form_frame)
        entry_title.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Mô tả:").pack(anchor="w")
        entry_desc = tk.Text(form_frame, height=4)
        entry_desc.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Ngày bắt đầu:").pack(anchor="w")
        entry_start = DateEntry(form_frame, date_pattern="dd-mm-yyyy", mindate=date.today())
        entry_start.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Ngày kết thúc:").pack(anchor="w")
        entry_deadline = DateEntry(form_frame, date_pattern="dd-mm-yyyy", mindate=date.today())
        entry_deadline.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Mức độ ưu tiên:").pack(anchor="w")
        combo_priority = ttk.Combobox(form_frame, values=["Cao", "Trung bình", "Thấp"])
        combo_priority.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Trạng thái:").pack(anchor="w")
        combo_status = ttk.Combobox(form_frame, values=["Đang làm", "Hoàn thành", "Hoãn", "Chưa hoàn thành"])
        combo_status.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Danh mục:").pack(anchor="w")
        combo_category = ttk.Combobox(form_frame, values=["Cá nhân", "Công việc", "Học tập"])
        combo_category.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Phân công cho:").pack(anchor="w")
        if self.current_role == "admin":
            listbox_assigned_to = tk.Listbox(form_frame, selectmode="multiple", height=5, exportselection=False)
            for user in user_list:
                listbox_assigned_to.insert(tk.END, user)
            listbox_assigned_to.pack(fill="x", pady=2)
        else:
            listbox_assigned_to = None

        selected_index = [None]

        def on_select(event):
            selected = tree.selection()
            if selected:
                idx = int(selected[0])
                selected_index[0] = idx
                task = filtered_data[idx]

                entry_title.delete(0, tk.END)
                entry_title.insert(0, task.get("title", ""))

                entry_desc.delete("1.0", tk.END)
                entry_desc.insert("1.0", task.get("description", ""))

                try:
                    entry_start.set_date(datetime.strptime(task.get("start_date", ""), "%d-%m-%Y"))
                except:
                    pass

                try:
                    entry_deadline.set_date(datetime.strptime(task.get("deadline", ""), "%d-%m-%Y"))
                except:
                    pass

                combo_priority.set(task.get("priority", "Trung bình"))
                combo_status.set(task.get("status", "Đang làm"))
                combo_category.set(task.get("category", "Cá nhân"))

                assigned_users = normalize_assigned_to(task)

                if self.current_role == "admin" and listbox_assigned_to:
                    listbox_assigned_to.selection_clear(0, tk.END)
                    for i, user in enumerate(user_list):
                        if user in assigned_users:
                            listbox_assigned_to.selection_set(i)

        tree.bind("<<TreeviewSelect>>", on_select)

        def fix_popup_position(date_entry):
            def on_focus(_):
                entry_y = date_entry.winfo_rooty()
                win_y = update_window.winfo_rooty()
                win_height = update_window.winfo_height()
                relative_y = entry_y - win_y
                if relative_y > win_height - 250:
                    date_entry.configure(popup_down=False)
                else:
                    date_entry.configure(popup_down=True)
            date_entry.bind("<FocusIn>", on_focus)

        fix_popup_position(entry_start)
        fix_popup_position(entry_deadline)

        def save_update():
            idx = selected_index[0]
            if idx is None:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn công việc để cập nhật.")
                return

            # Kiểm tra quyền cập nhật
            task_owner = data[idx].get("created_by", "")
            if self.current_role != "admin" and task_owner != self.current_user:
                messagebox.showwarning("Không được phép", "Bạn chỉ có thể cập nhật công việc do bạn tạo.")
                return

            idx = selected_index[0]
            if idx is None:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn công việc để cập nhật.")
                return

            title = entry_title.get().strip()
            description = entry_desc.get("1.0", tk.END).strip()
            start_date_str = entry_start.get()
            deadline_str = entry_deadline.get()
            priority = combo_priority.get()
            status = combo_status.get()
            category = combo_category.get()

            if self.current_role == "admin" and listbox_assigned_to:
                selected_indices = listbox_assigned_to.curselection()
                assigned_to = [user_list[i] for i in selected_indices]
            else:
                assigned_to = [self.current_user]

            if not title:
                messagebox.showwarning("Thiếu thông tin", "Tên công việc không được để trống.")
                return

            try:
                start_date_dt = datetime.strptime(start_date_str, "%d-%m-%Y")
                deadline_dt = datetime.strptime(deadline_str, "%d-%m-%Y")
            except ValueError:
                messagebox.showwarning("Lỗi định dạng ngày", "Định dạng ngày không hợp lệ.")
                return

            if start_date_dt > deadline_dt:
                messagebox.showwarning("Lỗi ngày", "Ngày bắt đầu không được lớn hơn ngày kết thúc.")
                return

            # Kiểm tra trùng tên task (loại trừ chính task đang sửa)
            title_normalized = title.strip().lower()
            current_creator = data[idx].get("created_by", self.current_user)

            if any(i != idx and 
                t.get("title", "").strip().lower() == title_normalized and 
                t.get("created_by", "") == current_creator
                for i, t in enumerate(data)):
                messagebox.showwarning("Trùng tên", "Bạn đã có một công việc với tiêu đề này.")
                return

            updated_task = {
                "title": title,
                "description": description,
                "start_date": start_date_str,
                "deadline": deadline_str,
                "priority": priority,
                "status": status,
                "category": category,
                "assigned_to": assigned_to,
                "created_by": current_creator
            }

            data[idx] = updated_task
            self.save_data(data)
            messagebox.showinfo("Thành công", "Cập nhật công việc thành công!")

            update_window.destroy()
            self.clear_display()
            self.show_task_list(data)

        tk.Button(update_window, text="Lưu cập nhật", command=save_update).pack(pady=10)

    def delete_all_tasks(self):
        tasks = self.load_data()
        if not tasks:
            messagebox.showinfo("Thông báo", "Không có công việc nào để xóa.")
            return

        if self.current_role == "admin":
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả công việc không?"):
                self.save_data([])
                messagebox.showinfo("Thành công", "Đã xóa tất cả công việc.")
                self.clear_display()
                self.show_task_list([])
        else:
            # User thường chỉ được xóa công việc họ tạo
            user_tasks = [task for task in tasks if task.get("created_by", "") == self.current_user]
            
            if not user_tasks:
                messagebox.showinfo("Thông báo", "Bạn không có công việc nào để xóa.")
                return

            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả công việc do bạn tạo không?"):
                remaining_tasks = [task for task in tasks if task.get("created_by", "") != self.current_user]
                self.save_data(remaining_tasks)
                messagebox.showinfo("Thành công", "Đã xóa tất cả công việc của bạn.")
                self.clear_display()
                self.show_task_list(remaining_tasks)

    def search_tasks(self):
        keyword = self.search_title_entry.get().lower().strip()
        from_date_str = self.search_start_date.get()
        to_date_str = self.search_end_date.get()

        try:
            from_date = datetime.strptime(from_date_str, "%d-%m-%Y")
            to_date = datetime.strptime(to_date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Lỗi định dạng", "Ngày không đúng định dạng.")
            return

        if from_date > to_date:
            messagebox.showwarning("Lỗi ngày", "Từ ngày không được lớn hơn đến ngày.")
            return

        data = self.load_data()
        results = []

        for task in data:
            task_title = task.get("title", "").lower()
            start_date_str = task.get("start_date", "")
            deadline_str = task.get("deadline", "")

            try:
                start_date = datetime.strptime(start_date_str, "%d-%m-%Y") if start_date_str else None
                deadline = datetime.strptime(deadline_str, "%d-%m-%Y") if deadline_str else None
            except ValueError:
                continue 

            if not start_date and not deadline:
                continue

            if not (
                (start_date and from_date <= start_date <= to_date) or
                (deadline and from_date <= deadline <= to_date)
            ):
                continue

            if keyword not in task_title:
                continue

            results.append(task)

        self.clear_display()
        if results:
            self.show_task_list(results)
        else:
            messagebox.showinfo("Kết quả", "Không tìm thấy công việc phù hợp.")