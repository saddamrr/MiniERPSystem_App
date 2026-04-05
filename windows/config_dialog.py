# windows/config_dialog.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from config_manager import ConfigManager
from styles import STYLE_ADD_BUTTON, STYLE_REFRESH_BUTTON, STYLE_DANGER_BUTTON

class ConfigDialog(QDialog):
    """Dialog untuk konfigurasi database"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.setWindowTitle("Konfigurasi Database")
        self.setFixedSize(550, 650)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 20px;
            }
            QLabel {
                color: #1e293b;
                font-weight: 500;
                margin-top: 6px;
                margin-bottom: 4px;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #1e293b;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #10b981;
                outline: none;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
                min-height: 40px;
            }
            QPushButton#testBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#testBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#saveBtn {
                background-color: #10b981;
                color: white;
            }
            QPushButton#saveBtn:hover {
                background-color: #059669;
            }
            QPushButton#cancelBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e2e8f0;
            }
            QFrame#statusFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
            QLabel#statusLabel {
                font-size: 12px;
                margin: 0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Container
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("⚙️ Konfigurasi Database")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Atur koneksi database untuk aplikasi")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Form Container
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        
        config = self.config_manager.get_db_config()
        
        # Host
        form_layout.addWidget(QLabel("Host *"))
        self.host_input = QLineEdit()
        self.host_input.setText(config['host'])
        self.host_input.setPlaceholderText("localhost")
        self.host_input.setMinimumHeight(40)
        form_layout.addWidget(self.host_input)
        
        # Port
        form_layout.addWidget(QLabel("Port *"))
        self.port_input = QLineEdit()
        self.port_input.setText(config['port'])
        self.port_input.setPlaceholderText("3306")
        self.port_input.setMinimumHeight(40)
        form_layout.addWidget(self.port_input)
        
        # Database
        form_layout.addWidget(QLabel("Nama Database *"))
        self.db_input = QLineEdit()
        self.db_input.setText(config['database'])
        self.db_input.setPlaceholderText("kasir_db")
        self.db_input.setMinimumHeight(40)
        form_layout.addWidget(self.db_input)
        
        # Username
        form_layout.addWidget(QLabel("Username *"))
        self.user_input = QLineEdit()
        self.user_input.setText(config['username'])
        self.user_input.setPlaceholderText("root")
        self.user_input.setMinimumHeight(40)
        form_layout.addWidget(self.user_input)
        
        # Password
        form_layout.addWidget(QLabel("Password"))
        self.pass_input = QLineEdit()
        self.pass_input.setText(config['password'])
        self.pass_input.setPlaceholderText("********")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setMinimumHeight(40)
        form_layout.addWidget(self.pass_input)
        
        # API URL
        form_layout.addWidget(QLabel("API URL *"))
        self.api_input = QLineEdit()
        self.api_input.setText(config['api_url'])
        self.api_input.setPlaceholderText("http://localhost/kasir_app/backend_api")
        self.api_input.setMinimumHeight(40)
        form_layout.addWidget(self.api_input)
        
        # Info
        info_label = QLabel("💡 Pastikan server database dan web server (XAMPP) berjalan")
        info_label.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 5px;")
        form_layout.addWidget(info_label)
        
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        # Status Frame
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout()
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.status_label = QLabel("Belum diuji")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        test_btn = QPushButton("🔌 Test Koneksi")
        test_btn.setObjectName("testBtn")
        test_btn.setMinimumHeight(44)
        test_btn.setStyleSheet(STYLE_REFRESH_BUTTON)
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)
        
        save_btn = QPushButton("💾 Simpan & Lanjut")
        save_btn.setObjectName("saveBtn")
        save_btn.setMinimumHeight(44)
        save_btn.setStyleSheet(STYLE_ADD_BUTTON)
        save_btn.clicked.connect(self.save_and_continue)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Keluar")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def test_connection(self):
        """Test koneksi database dan API"""
        # Simpan sementara config
        self.config_manager.update_db_config(
            host=self.host_input.text(),
            port=self.port_input.text(),
            database=self.db_input.text(),
            username=self.user_input.text(),
            password=self.pass_input.text(),
            api_url=self.api_input.text()
        )
        
        # Test database
        db_ok, db_msg = self.config_manager.test_connection()
        api_ok, api_msg = self.config_manager.test_api_connection()
        
        if db_ok and api_ok:
            self.status_icon.setStyleSheet("font-size: 12px; color: #10b981;")
            self.status_label.setText(f"✅ {db_msg} | {api_msg}")
            self.status_label.setStyleSheet("color: #10b981;")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Informasi")
            msg_box.setText("Database dan API terhubung.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
        elif db_ok and not api_ok:
            self.status_icon.setStyleSheet("font-size: 12px; color: #f59e0b;")
            self.status_label.setText(f"⚠️ Database OK | {api_msg}")
            self.status_label.setStyleSheet("color: #f59e0b;")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Peringatan")
            msg_box.setText(f"Database terhubung, tetapi API tidak terhubung.\n\n{api_msg}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
        else:
            self.status_icon.setStyleSheet("font-size: 12px; color: #ef4444;")
            self.status_label.setText(f"❌ {db_msg}")
            self.status_label.setStyleSheet("color: #ef4444;")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Peringatan")
            msg_box.setText(f"Database tidak terhubung.\n\n{db_msg}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
    
    def save_and_continue(self):
        """Simpan konfigurasi dan lanjutkan"""
        if not self.host_input.text() or not self.db_input.text() or not self.user_input.text():
            QMessageBox.warning(self, "Error", "Host, Nama Database, dan Username harus diisi!")
            return
        
        # Test koneksi sebelum simpan
        self.config_manager.update_db_config(
            host=self.host_input.text(),
            port=self.port_input.text(),
            database=self.db_input.text(),
            username=self.user_input.text(),
            password=self.pass_input.text(),
            api_url=self.api_input.text()
        )
        
        db_ok, db_msg = self.config_manager.test_connection()
        api_ok, api_msg = self.config_manager.test_api_connection()
        
        if db_ok and api_ok:
            self.config_manager.save_config()
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Informasi")
            msg_box.setText("Konfigurasi berhasil disimpan.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            self.accept()
        elif db_ok and not api_ok:
            # Database OK tapi API gagal, tanya apakah tetap simpan
            reply = QMessageBox.question(
                self,
                "Peringatan",
                f"⚠️ Database terhubung, tetapi API gagal:\n{api_msg}\n\nApakah tetap ingin menyimpan konfigurasi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config_manager.save_config()
                self.accept()
        else:
            QMessageBox.warning(self, "Error", f"❌ Koneksi gagal:\n{db_msg}\n\nPastikan konfigurasi benar!")