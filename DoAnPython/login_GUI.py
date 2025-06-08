import tkinter as tk
from tkinter import messagebox, ttk
from auth_manager import AuthManager
from crud import BuildCrud
from json_handle import JSONHandler
from security_user import SecurityUser
from register_user import RegisterUser
from tkinter import PhotoImage
from check_data import CheckData
from get_API import GetApi
from login_admin import LoginAdmin
import hashlib
import json
import os

class LoginGUI(SecurityUser, CheckData, RegisterUser, GetApi, LoginAdmin):
    def __init__(self):
        self.auth = AuthManager()
        self.jsonhandle = JSONHandler()
        self.check = CheckData()
        self.api = GetApi()
        self.current_user = None
        self.current_role = None

    def load_users(self):
        return self.auth.load_users()

    def save_users(self, users):
        self.auth.save_users(users)

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

    # ====== GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ===========  

    def create_gui(self, user_crud, role):
        self.root = tk.Tk()
        self.root.title("Hệ thống quản lý công việc cá nhân")
        self.root.state("zoomed")
        self.root.config(bg="lightblue")

        # ===== MENU BAR =====
        menubar = tk.Menu(self.root)

        # Menu Tài khoản với nút Đăng xuất
        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="Đăng xuất", command=self.logout)  # Có thể thêm biểu tượng bằng emoji
        menubar.add_cascade(label=f"Tài khoản của {self.current_user}", menu=account_menu)

        self.root.config(menu=menubar)

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10)

        left_frame = tk.Frame(self.root, bg="#d0e1f9", width=220)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(left_frame, text="Chức năng", font=("Arial", 16, "bold"), bg="#d0e1f9").pack(pady=15)

        # Đảm bảo truyền right_frame vào hàm setup_search_ui
        user_crud.set_display_frame(right_frame)

        # Các nút chức năng
        ttk.Button(left_frame, text="Tạo Mới", command=user_crud.create_data).pack(fill="x", pady=6)
        ttk.Button(left_frame, text="Cập Nhật", command=user_crud.update_data).pack(fill="x", pady=6)
        ttk.Button(left_frame, text="Xóa", command=user_crud.delete_data).pack(fill="x", pady=6)
        ttk.Button(left_frame, text="Đọc Dữ Liệu", command=user_crud.read_data).pack(fill="x", pady=6)

        if role == "admin":
            ttk.Button(left_frame, text="Xem Tài Khoản", command=user_crud.show_user_list).pack(fill="x", pady=6)
            ttk.Button(left_frame, text="Xem Công Việc Người Dùng", command=user_crud.admin_view_tasks).pack(fill="x", pady=6)
            account_menu.add_separator()
            account_menu.add_command(label="Tạo tài khoản admin", command=self.create_admin_account_window)

        ttk.Label(left_frame, text=f"Đăng nhập: {self.current_user}", font=("Arial", 12, "italic"), background="lightblue").pack(side="bottom", pady=20)    

        ttk.Button(left_frame, text="Lấy dữ liệu từ API", command=lambda: user_crud.fetch_data_from_api(self.current_user)).pack(fill="x", pady=6)
        ttk.Button(left_frame, text="Kiểm tra dữ liệu JSON", command=user_crud.check_data_exists).pack(fill="x", pady=6)
        ttk.Button(left_frame, text="Xóa tất cả công việc", command=user_crud.delete_all_tasks).pack(fill="x", pady=6)

        self.root.mainloop()

    # ====== GIAO DIỆN ĐĂNG NHẬP BAN ĐẦU ===========
    def show_login(self):
        self.login_window = tk.Tk()
        self.login_window = self.login_window
        self.login_window.title("Danh sách quản lý công việc cá nhân")
        self.login_window.geometry("800x500")
        self.login_window.configure(bg="#f0f2f5")
        SecurityUser.login_window = self.login_window
        
        # Tạo frame chứa toàn bộ nội dung
        main_frame = tk.Frame(self.login_window, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame chứa hình ảnh bên trái
        left_frame = tk.Frame(main_frame, bg="#f0f2f5")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        label1 = tk.Label(left_frame, text="Chào mừng bạn đến với nhóm 12", bg="#f0f2f5", fg="#1877f2", font=("Arial", 16, "bold"))
        label1.pack(pady=(20, 5))

        label2 = tk.Label(left_frame, text="Quản lý công việc cá nhân", bg="#f0f2f5", fg="#000000", font=("Arial Rounded MT", 14, "bold"))
        label2.pack(pady=(0, 10))

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
        
        #Quên mật khẩu
        forgot_label = tk.Label(right_frame, text="Quên mật khẩu?", fg="blue", bg="#f0f2f5", font=("Arial", 10), cursor="hand2")
        forgot_label.pack(pady=(0, 10))

        # Gán vào thuộc tính để sử dụng trong hàm on_hover và on_leave
        self.forgot_label = forgot_label

        # Bắt sự kiện hover và click
        forgot_label.bind("<Enter>", lambda e: self.on_hover())
        forgot_label.bind("<Leave>", lambda e: self.on_leave())
        forgot_label.bind("<Button-1>", self.forgot_password)

        # Nút đăng ký
        register_button = tk.Button(right_frame, text="Đăng ký", command=self.open_register_window, bg="#42b72a", fg="white", font=("Arial", 12, "bold"), relief="flat", activebackground="#36a420",padx=20, pady=10)
        register_button.pack(fill="x")
        
        # Căn chỉnh khi thay đổi kích thước cửa sổ
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        self.login_window.mainloop()

    def logout(self):
        self.root.destroy()      
        self.show_login()        