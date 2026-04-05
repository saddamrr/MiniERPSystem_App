# pages/profile_page.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from config import COMPANY_DATA
from windows.dialogs import ChangePasswordDialog

class ProfilePage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        title = QLabel("👤 Profil Pengguna")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)
        
        # Two column layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left column - User Info
        left_card = QFrame()
        left_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        left_layout = QVBoxLayout()
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 80px; background-color: #f3f4f6; border-radius: 60px; padding: 20px;")
        left_layout.addWidget(avatar)
        
        left_layout.addSpacing(10)
        
        # User details
        user_title = QLabel("Informasi Pengguna")
        user_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60; margin-top: 10px;")
        left_layout.addWidget(user_title)
        
        user_details = [
            ("Username", self.user['username']),
            ("Nama Lengkap", self.user['nama']),
            ("Role", "Administrator" if self.user['role'] == 'admin' else "Kasir"),
        ]
        
        for label, value in user_details:
            row = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; min-width: 100px; color: #4b5563;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1f2937;")
            row.addWidget(label_widget)
            row.addWidget(value_widget)
            row.addStretch()
            left_layout.addLayout(row)
        
        left_card.setLayout(left_layout)
        
        # Right column - Company Info
        right_card = QFrame()
        right_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        right_layout = QVBoxLayout()
        
        company_title = QLabel("🏢 Informasi Perusahaan")
        company_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        right_layout.addWidget(company_title)
        
        company_details = [
            ("Nama Perusahaan", COMPANY_DATA['nama']),
            ("Jenis Usaha", COMPANY_DATA['jenis_usaha']),
            ("Alamat", COMPANY_DATA['alamat']),
            ("Telepon", COMPANY_DATA['telp']),
            ("Email", COMPANY_DATA['email']),
            ("Website", COMPANY_DATA['website']),
        ]
        
        for label, value in company_details:
            row = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; min-width: 110px; color: #4b5563;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1f2937;")
            value_widget.setWordWrap(True)
            row.addWidget(label_widget)
            row.addWidget(value_widget, 1)
            row.addStretch()
            right_layout.addLayout(row)
        
        right_card.setLayout(right_layout)
        
        content_layout.addWidget(left_card, 1)
        content_layout.addWidget(right_card, 2)
        layout.addLayout(content_layout)
        
        # Button
        btn = QPushButton("🔑 Ganti Password")
        btn.setObjectName("secondary")
        btn.setMinimumHeight(45)
        btn.setFixedWidth(200)
        btn.clicked.connect(self.change_password)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def change_password(self):
        dialog = ChangePasswordDialog(self.user['username'])
        dialog.exec()