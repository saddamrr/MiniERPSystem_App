# windows/login_window.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import requests
from styles import STYLE
from windows.main_window import MainWindow
from config import API_URL
from database_helper import DatabaseHelper
from config import COMPANY_DATA

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(450, 500)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_pos = None
        self.setStyleSheet(STYLE)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 50, 40, 50)
        
        logo = QLabel("APP")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 70px;")
        layout.addWidget(logo)
        
        title = QLabel(COMPANY_DATA['nama'])
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #10b981;")
        layout.addWidget(title)
        
        # subtitle = QLabel("SARI ALAM")
        # subtitle.setAlignment(Qt.AlignCenter)
        # subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        # layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: 600; color: #374151;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #10b981;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: 600; color: #374151;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #10b981;
            }
        """)
        layout.addWidget(self.password_input)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        btn_login = QPushButton("LOGIN")
        btn_login.clicked.connect(self.login)
        btn_login.setMinimumHeight(45)
        btn_login.setStyleSheet("font-size: 14px;")
        layout.addWidget(btn_login)

        # Loading indicator
        self.loading = QProgressBar()
        self.loading.setFixedHeight(3)
        self.loading.setTextVisible(False)
        self.loading.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f3f4f6;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 2px;
            }
        """)
        self.loading.setVisible(False)
        layout.addWidget(self.loading)
        
        # info = QLabel("Demo: admin / admin123")
        # info.setAlignment(Qt.AlignCenter)
        # info.setStyleSheet("color: #95a5a6; font-size: 11px; margin-top: 10px;")
        # layout.addWidget(info)
        
        self.setLayout(layout)
    
    def login(self):
        """Authenticate user from database"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("Username dan password harus diisi!")
            return
        
        # Show loading
        self.loading.setVisible(True)
        self.loading.setValue(0)
        
        try:
            # Call API untuk login
            response = requests.post(
                f"{API_URL}/login.php",
                json={
                    "username": username,
                    "password": password
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    user = result.get('user', {})
                    # Login berhasil
                    self.main_app = MainWindow(user)
                    self.main_app.show()
                    self.close()
                else:
                    self.show_error(result.get('message', 'Username atau password salah!'))
            else:
                self.show_error("Gagal terhubung ke server!")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Tidak dapat terhubung ke server! Pastikan server berjalan.")
        except requests.exceptions.Timeout:
            self.show_error("Timeout koneksi! Periksa jaringan Anda.")
        except Exception as e:
            print(f"Login error: {e}")
            self.show_error(f"Error: {str(e)}")
        finally:
            self.loading.setVisible(False)
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.status_label.setVisible(True)
        
        # Clear password
        self.password_input.clear()
        self.password_input.setFocus()