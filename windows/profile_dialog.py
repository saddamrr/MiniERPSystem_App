# windows/profile_dialog.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from config import COMPANY_DATA
from utils import format_rupiah
import database_helper as DatabaseHelper

class ProfileDialog(QDialog):
    """Dialog untuk menampilkan profil pengguna dan perusahaan"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Profil Pengguna & Perusahaan")
        self.setFixedSize(650, 550)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                border-radius: 16px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                color: #10b981;
                left: 12px;
                padding: 0 8px;
            }
            QLabel {
                color: #1f2937;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton#closeBtn {
                background-color: #ef4444;
            }
            QPushButton#closeBtn:hover {
                background-color: #dc2626;
            }
            QFrame#infoFrame {
                background-color: #f1f5f9;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header = QLabel("👤 Profil Saya")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #10b981;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Two column layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left Column - User Info
        user_group = QGroupBox("Informasi Pengguna")
        user_layout = QVBoxLayout()
        user_layout.setSpacing(15)
        
        # Avatar
        avatar_frame = QFrame()
        avatar_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 60px;
                padding: 15px;
            }
        """)
        avatar_layout = QVBoxLayout()
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 64px;")
        avatar_layout.addWidget(avatar)
        avatar_frame.setLayout(avatar_layout)
        user_layout.addWidget(avatar_frame)
        
        # User details
        user_details = [
            ("Username", self.user['username']),
            ("Nama Lengkap", self.user['nama']),
            ("Role", "Administrator" if self.user['role'] == 'admin' else "Kasir"),
            ("Status", "🟢 Aktif")
        ]
        
        for label, value in user_details:
            row = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; min-width: 100px; color: #475569;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1f2937;")
            row.addWidget(label_widget)
            row.addWidget(value_widget)
            row.addStretch()
            user_layout.addLayout(row)
        
        user_group.setLayout(user_layout)
        content_layout.addWidget(user_group, 1)
        
        # Right Column - Company Info
        company_group = QGroupBox("Informasi Perusahaan")
        company_layout = QVBoxLayout()
        company_layout.setSpacing(12)
        
        # Logo
        logo_frame = QFrame()
        logo_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        logo_layout = QHBoxLayout()
        logo = QLabel("🌾")
        logo.setStyleSheet("font-size: 40px;")
        company_name = QLabel(COMPANY_DATA['nama'])
        company_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        logo_layout.addWidget(logo)
        logo_layout.addWidget(company_name)
        logo_layout.addStretch()
        logo_frame.setLayout(logo_layout)
        company_layout.addWidget(logo_frame)
        
        # Company details
        company_details = [
            ("Jenis Usaha", COMPANY_DATA['jenis_usaha']),
            ("Alamat", COMPANY_DATA['alamat']),
            ("Telepon", COMPANY_DATA['telp']),
            ("Email", COMPANY_DATA['email']),
            ("Website", COMPANY_DATA['website'])
        ]
        
        for label, value in company_details:
            row = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; min-width: 90px; color: #475569;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1f2937;")
            value_widget.setWordWrap(True)
            row.addWidget(label_widget)
            row.addWidget(value_widget, 1)
            company_layout.addLayout(row)
        
        company_group.setLayout(company_layout)
        content_layout.addWidget(company_group, 2)
        
        layout.addLayout(content_layout)
        
        # Info Frame
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QHBoxLayout()
        
        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 16px;")
        info_text = QLabel("Untuk mengubah data profil, silakan hubungi administrator.")
        info_text.setStyleSheet("color: #475569; font-size: 12px;")
        
        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Tutup")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(100, 40)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)