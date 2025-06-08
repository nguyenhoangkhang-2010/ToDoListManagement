import tkinter as tk
from tkinter import messagebox, ttk
import datetime

class RegisterUser:   
    def register_user(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        role = self.role_var.get().strip()
        question = self.security_question_var.get().strip()
        answer = self.security_answer.get().strip().lower()

        day = self.day_var.get()
        month = self.month_var.get()
        year = self.year_var.get()
        birthdate = f"{day}/{month}/{year}"

        users = self.load_users()

        if username in users:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
            return
        elif not username or not password or not question or not answer or not day or not month or not year:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ!")
            return
        elif len(password) < 6:
            messagebox.showwarning("Yếu", "Mật khẩu phải có ít nhất 6 ký tự!")
            return

        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "security_question": question,
            "security_answer": answer,
            "birthdate": birthdate
        }

        self.save_users(users)
        messagebox.showinfo("Thành công", f"{username} đã đăng ký thành công!")
        self.register_window.destroy()

    def open_register_window(self):
        self.register_window = tk.Toplevel(self.login_window)
        self.register_window.title("Đăng ký")
        self.register_window.geometry("300x500")

        tk.Label(self.register_window, text="Tên đăng nhập:").pack(pady=5)
        self.reg_username = tk.Entry(self.register_window)
        self.reg_username.pack(pady=5)

        tk.Label(self.register_window, text="Mật khẩu:").pack(pady=5)
        self.reg_password = tk.Entry(self.register_window, show="*")
        self.reg_password.pack(pady=5)

        self.role_var = tk.StringVar(value="user")

        tk.Label(self.register_window, text="Câu hỏi bảo mật:").pack(pady=5)
        self.security_question_var = tk.StringVar(value="Tên món đồ yêu thích của bạn là gì?")
        security_questions = [
            "Tên món đồ bạn yêu thích là gì?",
            "Tên thú cưng đầu tiên?",
            "Quê quán của bạn ở đâu?",
        ]
        self.security_question_menu = ttk.Combobox(self.register_window, textvariable=self.security_question_var, values=security_questions, state="readonly")
        self.security_question_menu.pack(pady=5)

        # Trả lời câu hỏi bảo mật
        tk.Label(self.register_window, text="Trả lời câu hỏi:").pack(pady=5)
        self.security_answer = tk.Entry(self.register_window)
        self.security_answer.pack(pady=5)

        # Ngày sinh (dạng chọn)
        tk.Label(self.register_window, text="Ngày/Tháng/Năm sinh:").pack(pady=5)

        birth_frame = tk.Frame(self.register_window)
        birth_frame.pack(pady=5)

        # Ngày
        self.day_var = tk.StringVar()
        day_options = [str(i).zfill(2) for i in range(1, 32)]
        self.day_cb = ttk.Combobox(birth_frame, textvariable=self.day_var, values=day_options, width=5, state="readonly")
        today = datetime.datetime.now()
        self.day_cb.set(str(today.day).zfill(2))
        self.day_cb.pack(side="left", padx=2)

        # Tháng
        self.month_var = tk.StringVar()
        month_options = [str(i).zfill(2) for i in range(1, 13)]
        self.month_cb = ttk.Combobox(birth_frame, textvariable=self.month_var, values=month_options, width=5, state="readonly")
        today = datetime.datetime.now()
        self.month_cb.set(str(today.month).zfill(2))
        self.month_cb.pack(side="left", padx=2)
        self.month_var.trace('w', self.update_days)

        # Năm
        self.year_var = tk.StringVar()
        current_year = datetime.datetime.now().year

        # Cho chọn năm từ 1900 đến năm hiện tại
        year_options = [str(i) for i in range(1900, current_year + 1)]
        self.year_cb = ttk.Combobox(birth_frame, textvariable=self.year_var, values=year_options, width=7, state="readonly")
        self.year_cb.set(str(current_year))  # mặc định là năm hiện tại
        self.year_cb.pack(side="left", padx=2)
        self.year_var.trace('w', self.update_days)

        tk.Button(self.register_window, text="Đăng ký", command=self.register_user).pack(pady=10)