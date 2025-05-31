import tkinter as tk
from tkinter import messagebox, ttk
from auth_manager import AuthManager
from crud import BuildCrud
from jsonhandle import JSONHandler
from tkinter import *
import hashlib

class LoginGUI:
    def __init__(self):
        self.auth = AuthManager()
        self.jsonhandle = JSONHandler()
        self.current_user = None
        self.current_role = None

    def load_users(self):
        return self.auth.load_users()

    def save_users(self, users):
        self.auth.save_users(users)

    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        role = self.role_var.get()
        users = self.load_users()

        if username in users:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
        elif not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ!")
        elif len(password) < 6:
            messagebox.showwarning("Yếu", "Mật khẩu phải có ít nhất 6 ký tự!")
        else:
            users[username] = {
                "password": self.hash_password(password),
                "role": role
            }
            self.save_users(users)
            messagebox.showinfo("Thành công", f"Đăng ký thành công với vai trò: {role}")
            self.register_window.destroy()

    def login_user(self):
        username = self.login_username.get()
        password = self.login_password.get()
        users = self.load_users()

        if username in users and users[username]["password"] == self.hash_password(password):
            role = users[username]["role"]
            self.current_user = username
            self.current_role = role
            self.user_role = role
            messagebox.showinfo("Thành công", f"Chào mừng {username} ({role})!")
            self.login_window.destroy()

            user_crud = BuildCrud(username, role)
            self.create_gui(user_crud, role)
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def open_register_window(self):
        self.register_window = tk.Toplevel(self.login_window)
        self.register_window.title("Đăng ký")
        self.register_window.geometry("300x250")

        tk.Label(self.register_window, text="Tên đăng nhập:").pack(pady=5)
        self.reg_username = tk.Entry(self.register_window)
        self.reg_username.pack(pady=5)

        tk.Label(self.register_window, text="Mật khẩu:").pack(pady=5)
        self.reg_password = tk.Entry(self.register_window, show="*")
        self.reg_password.pack(pady=5)

        tk.Label(self.register_window, text="Vai trò:").pack(pady=5)
        self.role_var = tk.StringVar(value="user")
        tk.Radiobutton(self.register_window, text="User", variable=self.role_var, value="user").pack()
        tk.Radiobutton(self.register_window, text="Admin", variable=self.role_var, value="admin").pack()

        tk.Button(self.register_window, text="Đăng ký", command=self.register_user).pack(pady=10)

    # ====== GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ===========  

    def create_gui(self, user_crud, role):
        root = tk.Tk()
        root.title("Hệ thống quản lý công việc cá nhân")
        root.geometry("500x650")
        root.config(bg="lightblue")

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10)

        # Tiêu đề
        tk.Label(root, text="Quản Lý Thông Tin", font=("Arial", 16, "bold"), bg="lightblue").pack(pady=20)

        # Cả admin và user đều có quyền đọc
        ttk.Button(root, text="Tạo Mới", command=user_crud.create_data).pack(fill="x", padx=20, pady=5)
        ttk.Button(root, text="Cập Nhật", command=user_crud.update_data).pack(fill="x", padx=20, pady=5)
        ttk.Button(root, text="Xóa", command=user_crud.delete_data).pack(fill="x", padx=20, pady=5)
        ttk.Button(root, text="Đọc Dữ Liệu", command=user_crud.read_data).pack(fill="x", padx=20, pady=5)

        if role == "admin":
            ttk.Button(root, text="Xem Tài Khoản", command=user_crud.show_user_list).pack(fill="x", padx=20, pady=5)
            ttk.Button(root, text="Xem Công Việc Người Dùng", command=user_crud.admin_view_tasks).pack(fill="x", padx=20, pady=5)

        ttk.Button(root, text="Lấy dữ liệu từ API", command=user_crud.fetch_data_from_api).pack(fill="x", padx=20, pady=5)
        
        ttk.Button(root, text="Kiểm tra dữ liệu JSON", command=user_crud.check_data_exists).pack(fill="x", padx=20, pady=5)

        root.mainloop()

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


    # ====== GIAO DIỆN ĐĂNG NHẬP BAN ĐẦU ===========
    def show_login(self):
        self.login_window = tk.Tk()
        self.login_window.title("Danh sách quản lý công việc cá nhân")
        self.login_window.geometry("800x500")
        self.login_window.configure(bg="#f0f2f5")
        
        # Tạo frame chứa toàn bộ nội dung
        main_frame = tk.Frame(self.login_window, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame chứa hình ảnh bên trái
        left_frame = tk.Frame(main_frame, bg="#f0f2f5")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        try:
            img = PhotoImage(file='login.png')
            # Resize ảnh để phù hợp với kích thước frame
            img_label = tk.Label(left_frame, image=img, bg="#f0f2f5")
            img_label.image = img  # Giữ reference để ảnh không bị garbage collected
            img_label.pack(fill="both", expand=True)
        except:
            # Nếu không có ảnh, hiển thị placeholder
            placeholder = tk.Label(left_frame, text="Hình ảnh ứng dụng", bg="#1877f2", fg="white", font=("Arial", 16), width=30, height=15)
            placeholder.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame chứa form đăng nhập bên phải
        right_frame = tk.Frame(main_frame, bg="#f0f2f5")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Tiêu đề form
        title_label = tk.Label(right_frame, text="Đăng nhập", bg="#f0f2f5", fg="#1877f2", font=("Arial", 24, "bold"))
        title_label.pack(pady=(20, 30))
        
        # Ô nhập tên đăng nhập
        username_frame = tk.Frame(right_frame, bg="#f0f2f5")
        username_frame.pack(fill="x", pady=5)
        tk.Label(username_frame, text="Tên đăng nhập:", bg="#f0f2f5", font=("Arial", 12)).pack(anchor="w")
        self.login_username = tk.Entry(username_frame, font=("Arial", 12), relief="flat", highlightthickness=1, highlightbackground="#dddfe2", highlightcolor="#1877f2")
        self.login_username.pack(fill="x", ipady=8)
        
        # Ô nhập mật khẩu
        password_frame = tk.Frame(right_frame, bg="#f0f2f5")
        password_frame.pack(fill="x", pady=5)
        tk.Label(password_frame, text="Mật khẩu:", bg="#f0f2f5", font=("Arial", 12)).pack(anchor="w")
        self.login_password = tk.Entry(password_frame, show="*", font=("Arial", 12), relief="flat", highlightthickness=1, highlightbackground="#dddfe2", highlightcolor="#1877f2")
        self.login_password.pack(fill="x", ipady=8)
        
        # Nút đăng nhập
        login_button = tk.Button(right_frame, text="Đăng nhập", command=self.login_user, bg="#1877f2", fg="white", font=("Arial", 12, "bold"), relief="flat", activebackground="#166fe5",padx=20, pady=10)
        login_button.pack(fill="x", pady=(20, 10))
        
        # Nút đăng ký
        register_button = tk.Button(right_frame, text="Đăng ký", command=self.open_register_window, bg="#42b72a", fg="white", font=("Arial", 12, "bold"), relief="flat", activebackground="#36a420",padx=20, pady=10)
        register_button.pack(fill="x")
        
        # Căn chỉnh khi thay đổi kích thước cửa sổ
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        self.login_window.mainloop()

    def hash_password(self, password):
        if len(password) < 6:
            return None
        return hashlib.sha256(password.encode()).hexdigest()