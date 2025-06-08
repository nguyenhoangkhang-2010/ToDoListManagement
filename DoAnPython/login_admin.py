import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar

class LoginAdmin:
    def create_admin_account_window(self):
        window = tk.Toplevel(self.root)
        window.title("Tạo tài khoản admin mới")
        window.geometry("400x500")
        window.configure(bg="#f0f2f5")

        def add_label_entry(text, show=None):
            tk.Label(window, text=text, bg="#f0f2f5", font=("Arial", 12)).pack(pady=(10, 5))
            entry = tk.Entry(window, font=("Arial", 12), show=show)
            entry.pack(fill="x", padx=20)
            return entry

        # Tên đăng nhập
        username_entry = add_label_entry("Tên đăng nhập:")
        # Mật khẩu
        password_entry = add_label_entry("Mật khẩu:", show="*")

        # Ngày sinh
        tk.Label(window, text="Ngày sinh:", bg="#f0f2f5", font=("Arial", 12)).pack(pady=(10, 5))
        birthdate_var = tk.StringVar()
        birthdate_entry = tk.Entry(window, font=("Arial", 12), textvariable=birthdate_var, state="readonly")
        birthdate_entry.pack(fill="x", padx=20)

        def select_birthdate():
            top = tk.Toplevel(window)
            top.title("Chọn ngày sinh")
            cal = Calendar(top, selectmode="day", date_pattern="dd/mm/yyyy")
            cal.pack(padx=10, pady=10)
            def get_date():
                birthdate_var.set(cal.get_date())
                top.destroy()
            tk.Button(top, text="Chọn", command=get_date).pack(pady=5)
        tk.Button(window, text="Chọn ngày sinh", command=select_birthdate).pack(pady=(5, 10))

        # Câu hỏi bảo mật
        question_entry = add_label_entry("Câu hỏi bảo mật:")
        # Câu trả lời
        answer_entry = add_label_entry("Câu trả lời:")

        def save_admin():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            birthdate = birthdate_var.get()
            question = question_entry.get().strip()
            answer = answer_entry.get().strip()

            if not all([username, password, birthdate, question, answer]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
                return

            users = self.load_users()
            if username in users:
                messagebox.showerror("Lỗi", "Tài khoản đã tồn tại.")
                return

            if len(password) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự.")
                return

            users[username] = {
                "password": self.hash_password(password),
                "role": "admin",
                "birthdate": birthdate,
                "security_question": question,
                "security_answer": answer
            }

            self.save_users(users)
            messagebox.showinfo("Thành công", f"Tạo tài khoản admin '{username}' thành công.")
            window.destroy()

        tk.Button(window, text="Tạo tài khoản", command=save_admin, bg="#1877f2", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
