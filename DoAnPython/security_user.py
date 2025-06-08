from tkcalendar import Calendar
import tkinter as tk
import datetime
import hashlib
import json
from tkinter import simpledialog, messagebox, ttk

class SecurityUser:
    def __init__(self, login_window=None):
        self.login_window = login_window

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
        user_window.mainloop()

    def hash_password(self, password):
        if len(password) < 6:
            return None
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        try:
            with open("users.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_users(self, users):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    def on_hover(self):
        self.forgot_label.config(font=("Arial", 10, "underline"))

    def on_leave(self):
        self.forgot_label.config(font=("Arial", 10, "normal"))

    def forgot_password(self, event=None):
        users = self.load_users()
        username = simpledialog.askstring("Quên Mật Khẩu", "Nhập tên đăng nhập của bạn:", parent=self.login_window)
        if not username:
            messagebox.showwarning("Thông báo", "Bạn cần nhập tên đăng nhập!", parent=self.login_window)
            return

        if username not in users:
            messagebox.showerror("Lỗi", "Bạn chưa có tài khoản!", parent=self.login_window)
            return

        user_info = users[username]
        question = user_info.get("security_question", "Không có câu hỏi bảo mật")

        answer = simpledialog.askstring("Quên Mật Khẩu", f"Câu hỏi bảo mật:\n{question}", parent=self.login_window)
        if not answer or answer.strip().lower() != user_info.get("security_answer", "").lower():
            messagebox.showerror("Lỗi", "Trả lời câu hỏi bảo mật sai!", parent=self.login_window)
            return

        birthdate = self.ask_birthdate()
        if not birthdate:
            messagebox.showerror("Lỗi", "Vui lòng chọn ngày sinh!", parent=self.login_window)
            return

        try:
            input_date = datetime.datetime.strptime(birthdate, "%d/%m/%Y").strftime("%d/%m/%Y")
            stored_date = datetime.datetime.strptime(user_info.get("birthdate", ""), "%d/%m/%Y").strftime("%d/%m/%Y")
            if input_date != stored_date:
                messagebox.showerror("Lỗi", "Ngày sinh không đúng!", parent=self.login_window)
                return
        except:
            messagebox.showerror("Lỗi", "Định dạng ngày sinh không hợp lệ!", parent=self.login_window)
            return

        new_password = simpledialog.askstring("Quên Mật Khẩu", "Nhập mật khẩu mới:", parent=self.login_window, show="*")
        if not new_password or len(new_password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự!", parent=self.login_window)
            return

        users[username]["password"] = self.hash_password(new_password)
        self.save_users(users)
        messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=self.login_window)

    def ask_birthdate(self):
        def on_ok():
            selected = cal.get_date()  # MM/DD/YY
            date_obj = datetime.datetime.strptime(selected, "%m/%d/%y")
            self.selected_birthdate = date_obj.strftime("%d/%m/%Y")
            top.destroy()

        top = tk.Toplevel(self.login_window)
        top.title("Chọn ngày sinh")
        cal = Calendar(top, selectmode='day', date_pattern='mm/dd/yy')
        cal.pack(padx=10, pady=10)

        ok_btn = tk.Button(top, text="OK", command=on_ok)
        ok_btn.pack(pady=5)

        self.login_window.wait_window(top)
        return getattr(self, 'selected_birthdate', None)

    def update_days(self, *args):
        # Lấy giá trị tháng và năm hiện tại trong combobox
        month = self.month_var.get()
        year = self.year_var.get()
        
        if not month or not year:
            return
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return

        # Xác định số ngày tối đa trong tháng
        if month in [1,3,5,7,8,10,12]:
            max_days = 31
        elif month in [4,6,9,11]:
            max_days = 30
        else:  # Tháng 2
            # Kiểm tra năm nhuận
            if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
                max_days = 29
            else:
                max_days = 28

        # Cập nhật lại giá trị trong combobox ngày
        day_options = [str(i).zfill(2) for i in range(1, max_days + 1)]
        current_day = self.day_var.get()
        
        self.day_cb['values'] = day_options

        # Nếu ngày hiện tại lớn hơn số ngày tối đa mới, reset về ngày đầu tiên
        if current_day not in day_options:
            self.day_cb.set(day_options[0])
