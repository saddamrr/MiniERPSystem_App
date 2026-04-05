# windows/dialogs.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah, safe_int
from styles import STYLE_ADD_BUTTON, STYLE_REFRESH_BUTTON, STYLE_DANGER_BUTTON

class AddProductDialog(QDialog):
    """Dialog untuk menambah produk baru"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Produk Baru")
        self.setFixedSize(500, 580)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLabel {
                color: #1e293b;
                font-weight: 500;
                font-size: 13px;
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
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit#error {
                border-color: #ef4444;
                background-color: #fef2f2;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
            }
            QPushButton#saveBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#saveBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#cancelBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e2e8f0;
            }
            QFrame#separator {
                background-color: #e2e8f0;
                max-height: 1px;
                margin: 12px 0;
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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("➕ Tambah Produk Baru")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #3b82f6; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        # Brand
        layout.addWidget(QLabel("Brand *"))
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Contoh: Kedelai Lokal")
        self.brand_input.setMinimumHeight(40)
        layout.addWidget(self.brand_input)
        
        # Harga Beli
        layout.addWidget(QLabel("Harga Beli per KG (Rp)"))
        self.harga_beli_input = QLineEdit()
        self.harga_beli_input.setPlaceholderText("Contoh: 8000")
        self.harga_beli_input.setMinimumHeight(40)
        layout.addWidget(self.harga_beli_input)
        
        # Harga Jual
        layout.addWidget(QLabel("Harga Jual per KG (Rp) *"))
        self.harga_jual_input = QLineEdit()
        self.harga_jual_input.setPlaceholderText("Contoh: 10000")
        self.harga_jual_input.setMinimumHeight(40)
        layout.addWidget(self.harga_jual_input)
        
        # Stok Awal
        layout.addWidget(QLabel("Stok Awal (Karung)"))
        self.stok_input = QLineEdit()
        self.stok_input.setPlaceholderText("Contoh: 100")
        self.stok_input.setText("0")
        self.stok_input.setMinimumHeight(40)
        layout.addWidget(self.stok_input)
        
        # Berat per Karung
        layout.addWidget(QLabel("Berat per Karung (KG)"))
        self.berat_input = QLineEdit()
        self.berat_input.setText("50")
        self.berat_input.setMinimumHeight(40)
        layout.addWidget(self.berat_input)
        
        # Stok Minimum
        layout.addWidget(QLabel("Stok Minimum (Karung)"))
        self.stok_min_input = QLineEdit()
        self.stok_min_input.setText("2")
        self.stok_min_input.setMinimumHeight(40)
        layout.addWidget(self.stok_min_input)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        layout.addWidget(separator)
        
        # Preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("Preview akan muncul setelah input")
        self.preview_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px 0;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        save_btn = QPushButton("Simpan")
        # save_btn.setObjectName("saveBtn")
        save_btn.setStyleSheet(STYLE_ADD_BUTTON)
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self.save_product)
        
        cancel_btn = QPushButton("Batal")
        # cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Preview update
        self.brand_input.textChanged.connect(self.update_preview)
        self.harga_jual_input.textChanged.connect(self.update_preview)
        self.stok_input.textChanged.connect(self.update_preview)
        self.berat_input.textChanged.connect(self.update_preview)
        self.update_preview()
        
        # Validation
        self.brand_input.textChanged.connect(self.clear_error)
        self.harga_jual_input.textChanged.connect(self.clear_error)
    
    def update_preview(self):
        try:
            brand = self.brand_input.text() or "-"
            harga_kg = safe_float(self.harga_jual_input.text())
            stok = safe_float(self.stok_input.text())
            berat = safe_float(self.berat_input.text())
            
            harga_karung = harga_kg * berat
            stok_kg = stok * berat
            nilai_stok = stok_kg * harga_kg
            
            self.preview_label.setText(
                f"📦 {brand}\n"
                f"Harga per karung: Rp {harga_karung:,.0f}\n"
                f"Total stok: {stok:.1f} karung / {stok_kg:.0f} KG\n"
                f"Nilai stok: Rp {nilai_stok:,.0f}"
            )
        except:
            self.preview_label.setText("Masukkan data dengan benar")
    
    def clear_error(self):
        self.error_label.setVisible(False)
        self.brand_input.setStyleSheet("")
        self.harga_jual_input.setStyleSheet("")
    
    def show_error(self, message):
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.setVisible(True)
        self.brand_input.setStyleSheet("border-color: #ef4444; background-color: #fef2f2;")
    
    def save_product(self):
        brand = self.brand_input.text().strip()
        
        if not brand:
            self.show_error("Brand harus diisi!")
            return
        
        if not self.harga_jual_input.text().strip():
            self.show_error("Harga Jual harus diisi!")
            return
        
        try:
            harga_jual = safe_float(self.harga_jual_input.text())
            if harga_jual <= 0:
                self.show_error("Harga Jual harus lebih dari 0!")
                return
            
            data = {
                'brand': brand,
                'kategori': 'Kedelai',
                'harga_beli_kg': safe_float(self.harga_beli_input.text()),
                'harga_jual_kg': harga_jual,
                'stok_karung': safe_float(self.stok_input.text()),
                'stok_kg': safe_float(self.stok_input.text()) * safe_float(self.berat_input.text()),
                'berat_per_karung': safe_float(self.berat_input.text()),
                'stok_minimum_karung': safe_float(self.stok_min_input.text())
            }
            
            result = DatabaseHelper.add_product(data)
            if result.get('status') == 'success':
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Pemberitahuan!")
                msg_box.setText(f"Produk '{brand}' berhasil ditambahkan!")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()
                self.accept()
            else:
                self.show_error(result.get('message', 'Gagal menambahkan produk'))
                
        except Exception as e:
            self.show_error(str(e))


class EditProductDialog(QDialog):
    """Dialog untuk edit produk"""
    
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Edit Produk - {product.get('brand', '')}")
        self.setFixedSize(500, 620)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLabel {
                color: #1e293b;
                font-weight: 500;
                font-size: 13px;
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
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit#readonly {
                background-color: #f8fafc;
                color: #64748b;
            }
            QLineEdit#error {
                border-color: #ef4444;
                background-color: #fef2f2;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
            }
            QPushButton#saveBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#saveBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#cancelBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e2e8f0;
            }
            QFrame#separator {
                background-color: #e2e8f0;
                max-height: 1px;
                margin: 12px 0;
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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel(f"✏️ Edit {self.product.get('brand', 'Produk')}")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #3b82f6; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Kode Barang (readonly)
        layout.addWidget(QLabel("Kode Barang"))
        kode_input = QLineEdit()
        kode_input.setText(self.product.get('kode_barang', '-'))
        kode_input.setReadOnly(True)
        kode_input.setObjectName("readonly")
        kode_input.setMinimumHeight(40)
        layout.addWidget(kode_input)
        
        # Brand
        layout.addWidget(QLabel("Brand *"))
        self.brand_input = QLineEdit()
        self.brand_input.setText(self.product.get('brand', ''))
        self.brand_input.setMinimumHeight(40)
        layout.addWidget(self.brand_input)
        
        # Harga Beli
        layout.addWidget(QLabel("Harga Beli per KG (Rp)"))
        self.harga_beli_input = QLineEdit()
        self.harga_beli_input.setText(str(self.product.get('harga_beli_kg', 0)))
        self.harga_beli_input.setMinimumHeight(40)
        layout.addWidget(self.harga_beli_input)
        
        # Harga Jual
        layout.addWidget(QLabel("Harga Jual per KG (Rp) *"))
        self.harga_jual_input = QLineEdit()
        self.harga_jual_input.setText(str(self.product.get('harga_jual_kg', 0)))
        self.harga_jual_input.setMinimumHeight(40)
        layout.addWidget(self.harga_jual_input)
        
        # Stok
        layout.addWidget(QLabel("Stok (Karung)"))
        self.stok_input = QLineEdit()
        self.stok_input.setText(str(self.product.get('stok_karung', 0)))
        self.stok_input.setMinimumHeight(40)
        layout.addWidget(self.stok_input)
        
        # Berat per Karung
        layout.addWidget(QLabel("Berat per Karung (KG)"))
        self.berat_input = QLineEdit()
        self.berat_input.setText(str(self.product.get('berat_per_karung', 50)))
        self.berat_input.setMinimumHeight(40)
        layout.addWidget(self.berat_input)
        
        # Stok Minimum
        layout.addWidget(QLabel("Stok Minimum (Karung)"))
        self.stok_min_input = QLineEdit()
        self.stok_min_input.setText(str(self.product.get('stok_minimum_karung', 2)))
        self.stok_min_input.setMinimumHeight(40)
        layout.addWidget(self.stok_min_input)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        layout.addWidget(separator)
        
        # Preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px 0;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        save_btn = QPushButton("Update")
        # save_btn.setObjectName("saveBtn")
        save_btn.setStyleSheet(STYLE_REFRESH_BUTTON)
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self.update_product)
        
        cancel_btn = QPushButton("Batal")
        # cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Preview update
        self.brand_input.textChanged.connect(self.update_preview)
        self.harga_jual_input.textChanged.connect(self.update_preview)
        self.stok_input.textChanged.connect(self.update_preview)
        self.berat_input.textChanged.connect(self.update_preview)
        self.update_preview()
        
        # Validation
        self.brand_input.textChanged.connect(self.clear_error)
        self.harga_jual_input.textChanged.connect(self.clear_error)
    
    def update_preview(self):
        try:
            brand = self.brand_input.text() or "-"
            harga_kg = safe_float(self.harga_jual_input.text())
            stok = safe_float(self.stok_input.text())
            berat = safe_float(self.berat_input.text())
            
            harga_karung = harga_kg * berat
            stok_kg = stok * berat
            nilai_stok = stok_kg * harga_kg
            
            self.preview_label.setText(
                f"📦 {brand}\n"
                f"Harga per karung: Rp {harga_karung:,.0f}\n"
                f"Total stok: {stok:.1f} karung / {stok_kg:.0f} KG\n"
                f"Nilai stok: Rp {nilai_stok:,.0f}"
            )
        except:
            self.preview_label.setText("Masukkan data dengan benar")
    
    def clear_error(self):
        self.error_label.setVisible(False)
        self.brand_input.setStyleSheet("")
        self.harga_jual_input.setStyleSheet("")
    
    def show_error(self, message):
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.setVisible(True)
        self.brand_input.setStyleSheet("border-color: #ef4444; background-color: #fef2f2;")
    
    def update_product(self):
        brand = self.brand_input.text().strip()
        
        if not brand:
            self.show_error("Brand harus diisi!")
            return
        
        if not self.harga_jual_input.text().strip():
            self.show_error("Harga Jual harus diisi!")
            return
        
        try:
            harga_jual = safe_float(self.harga_jual_input.text())
            if harga_jual <= 0:
                self.show_error("Harga Jual harus lebih dari 0!")
                return
            
            data = {
                'id_barang': self.product.get('id_barang'),
                'brand': brand,
                'harga_beli_kg': safe_float(self.harga_beli_input.text()),
                'harga_jual_kg': harga_jual,
                'stok_karung': safe_float(self.stok_input.text()),
                'stok_kg': safe_float(self.stok_input.text()) * safe_float(self.berat_input.text()),
                'berat_per_karung': safe_float(self.berat_input.text()),
                'stok_minimum_karung': safe_float(self.stok_min_input.text())
            }
            
            result = DatabaseHelper.update_product(self.product.get('id_barang'), data)
            if result.get('status') == 'success':
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Pemberitahuan!")
                msg_box.setText(f"Produk '{brand}' berhasil diupdate!")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()
                self.accept()
            else:
                self.show_error(result.get('message', 'Gagal update produk'))
                
        except Exception as e:
            self.show_error(str(e))

class ChangePasswordDialog(QDialog):
    """Dialog untuk ganti password"""
    
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Ganti Password")
        self.setFixedSize(450, 600)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 16px;
            }
            QLabel {
                color: #1f2937;
                font-size: 13px;
                font-weight: 500;
                margin-top: 8px;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #10b981;
                outline: none;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton#cancelBtn {
                background-color: #ef4444;
            }
            QPushButton#cancelBtn:hover {
                background-color: #dc2626;
            }
            QFrame {
                background-color: #fef2f2;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Title
        title = QLabel("🔐 Ganti Password")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username:"))
        user_label = QLabel(f"<b>{self.username}</b>")
        user_label.setStyleSheet("color: #10b981;")
        user_layout.addWidget(user_label)
        user_layout.addStretch()
        user_frame.setLayout(user_layout)
        layout.addWidget(user_frame)
        
        # Password Lama
        layout.addWidget(QLabel("Password Lama *"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Masukkan password lama")
        self.old_password.setMinimumHeight(40)
        layout.addWidget(self.old_password)
        
        # Password Baru
        layout.addWidget(QLabel("Password Baru *"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Minimal 8 karakter")
        self.new_password.setMinimumHeight(40)
        self.new_password.textChanged.connect(self.validate_password)
        layout.addWidget(self.new_password)
        
        # Konfirmasi Password
        layout.addWidget(QLabel("Konfirmasi Password Baru *"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Ketik ulang password baru")
        self.confirm_password.setMinimumHeight(40)
        self.confirm_password.textChanged.connect(self.validate_password)
        layout.addWidget(self.confirm_password)
        
        # Password strength indicator
        self.strength_frame = QFrame()
        self.strength_frame.setVisible(False)
        strength_layout = QVBoxLayout()
        strength_layout.setContentsMargins(10, 5, 10, 5)
        
        self.strength_label = QLabel()
        self.strength_label.setStyleSheet("font-size: 11px;")
        strength_layout.addWidget(self.strength_label)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e2e8f0;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #ef4444;
            }
        """)
        strength_layout.addWidget(self.strength_bar)
        
        self.strength_frame.setLayout(strength_layout)
        layout.addWidget(self.strength_frame)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 11px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #fef9e3;
                border: 1px solid #fde047;
            }
        """)
        info_layout = QHBoxLayout()
        info_icon = QLabel("🔒")
        info_icon.setStyleSheet("font-size: 14px;")
        info_text = QLabel("Password minimal 8 karakter, kombinasi huruf dan angka")
        info_text.setStyleSheet("color: #854d0e; font-size: 11px;")
        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        save_btn = QPushButton("Simpan Password")
        save_btn.clicked.connect(self.save_password)
        save_btn.setMinimumHeight(45)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def validate_password(self):
        """Validate password strength"""
        password = self.new_password.text()
        confirm = self.confirm_password.text()
        
        # Check password length
        if len(password) >= 8:
            self.strength_frame.setVisible(True)
            
            # Calculate strength
            strength = 0
            if len(password) >= 8:
                strength += 20
            if len(password) >= 10:
                strength += 10
            if any(c.isdigit() for c in password):
                strength += 20
            if any(c.isupper() for c in password):
                strength += 20
            if any(c.islower() for c in password):
                strength += 15
            if any(c in "!@#$%^&*" for c in password):
                strength += 15
            
            strength = min(strength, 100)
            
            # Set color based on strength
            if strength < 40:
                color = "#ef4444"
                text = "Password Lemah"
            elif strength < 70:
                color = "#f59e0b"
                text = "Password Sedang"
            else:
                color = "#10b981"
                text = "Password Kuat"
            
            self.strength_label.setText(text)
            self.strength_label.setStyleSheet(f"color: {color}; font-size: 11px;")
            self.strength_bar.setValue(strength)
            self.strength_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 3px;
                    background-color: #e2e8f0;
                }}
                QProgressBar::chunk {{
                    border-radius: 3px;
                    background-color: {color};
                }}
            """)
        else:
            self.strength_frame.setVisible(False)
        
        # Check confirmation
        if confirm and password != confirm:
            self.error_label.setText("❌ Password tidak cocok!")
            self.error_label.setVisible(True)
        else:
            self.error_label.setVisible(False)
    
    def save_password(self):
        """Save new password"""
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm = self.confirm_password.text()
        
        # Validations
        if not old_pass:
            QMessageBox.warning(self, "Error", "Password lama harus diisi!")
            return
        
        if not new_pass:
            QMessageBox.warning(self, "Error", "Password baru harus diisi!")
            return
        
        if len(new_pass) < 8:
            QMessageBox.warning(self, "Error", "Password minimal 8 karakter!")
            return
        
        if new_pass != confirm:
            QMessageBox.warning(self, "Error", "Konfirmasi password tidak cocok!")
            return
        
        # Check if new password is same as old
        if new_pass == old_pass:
            QMessageBox.warning(self, "Error", "Password baru tidak boleh sama dengan password lama!")
            return
        
        # Here you would call API to change password
        # For demo, just show success
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Pemberitahuan!")
        msg_box.setText(f"Password berhasil diubah!")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
        self.accept()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        title = QLabel("Ganti Password")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel(f"User: {self.username}"))
        
        layout.addWidget(QLabel("Password Baru:"))
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setMinimumHeight(40)
        layout.addWidget(self.new_pass)
        
        layout.addWidget(QLabel("Konfirmasi Password:"))
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.setMinimumHeight(40)
        layout.addWidget(self.confirm)
        
        info = QLabel("💡 Password minimal 6 karakter")
        info.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(info)
        
        btn_layout = QHBoxLayout()
        save = QPushButton("Simpan")
        save.setMinimumHeight(45)
        save.setStyleSheet(STYLE_ADD_BUTTON)
        save.clicked.connect(self.save_password)
        cancel = QPushButton("Batal")
        cancel.setMinimumHeight(45)
        cancel.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel.clicked.connect(self.reject)
        btn_layout.addWidget(save)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save_password(self):
        new_pass = self.new_pass.text()
        confirm = self.confirm.text()
        
        if not new_pass:
            QMessageBox.warning(self, "Error", "Password tidak boleh kosong!")
            return
        
        if new_pass != confirm:
            QMessageBox.warning(self, "Error", "Password tidak cocok!")
            return
        
        if len(new_pass) < 6:
            QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
            return
        
        QMessageBox.information(self, "Sukses", "✅ Password berhasil diubah!")
        self.accept()

class CustomerDialog(QDialog):
    """Dialog untuk tambah/edit pelanggan"""
    
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Tambah Pelanggan" if not customer else f"Edit Pelanggan - {customer.get('nama', '')}")
        
        # Atur ukuran berdasarkan mode
        if customer:
            self.setFixedSize(500, 620)  # Lebih tinggi untuk edit mode
        else:
            self.setFixedSize(500, 550)  # Ukuran normal untuk tambah
        
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLabel {
                color: #1e293b;
                font-weight: 500;
                font-size: 13px;
                margin-bottom: 4px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #1e293b;
                min-height: 20px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit#error, QTextEdit#error {
                border-color: #ef4444;
                background-color: #fef2f2;
            }
            QTextEdit {
                min-height: 60px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
            }
            QPushButton#saveBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#saveBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#cancelBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e2e8f0;
            }
            QFrame#separator {
                background-color: #e2e8f0;
                max-height: 1px;
                margin: 16px 0;
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
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area untuk konten yang mungkin panjang
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Container widget
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("👤 Informasi Pelanggan" if not self.customer else "✏️ Edit Pelanggan")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #0f172a; margin-bottom: 4px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form Container
        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)
        
        # Kode Pelanggan (edit mode)
        if self.customer:
            form_layout.addWidget(QLabel("Kode Pelanggan"))
            kode_label = QLabel(self.customer.get('kode_pelanggan', '-'))
            kode_label.setStyleSheet("""
                background-color: #f8fafc;
                padding: 12px;
                border-radius: 8px;
                color: #475569;
                font-size: 13px;
                font-weight: normal;
            """)
            form_layout.addWidget(kode_label)
        
        # Nama
        form_layout.addWidget(QLabel("Nama Lengkap *"))
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Masukkan nama lengkap")
        self.nama_input.setMinimumHeight(40)
        if self.customer:
            self.nama_input.setText(self.customer.get('nama', ''))
        form_layout.addWidget(self.nama_input)
        
        # No Telepon
        form_layout.addWidget(QLabel("No Telepon"))
        self.telp_input = QLineEdit()
        self.telp_input.setPlaceholderText("Masukkan nomor telepon")
        self.telp_input.setMinimumHeight(40)
        if self.customer:
            self.telp_input.setText(self.customer.get('no_telp', ''))
        form_layout.addWidget(self.telp_input)
        
        # Email
        form_layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Masukkan alamat email")
        self.email_input.setMinimumHeight(40)
        if self.customer:
            self.email_input.setText(self.customer.get('email', ''))
        form_layout.addWidget(self.email_input)
        
        # Alamat
        form_layout.addWidget(QLabel("Alamat"))
        self.alamat_input = QTextEdit()
        self.alamat_input.setMinimumHeight(80)
        self.alamat_input.setMaximumHeight(100)
        self.alamat_input.setPlaceholderText("Masukkan alamat lengkap")
        if self.customer:
            self.alamat_input.setText(self.customer.get('alamat', ''))
        form_layout.addWidget(self.alamat_input)
        
        # Info tambahan untuk edit mode
        if self.customer:
            # Separator
            separator = QFrame()
            separator.setObjectName("separator")
            form_layout.addWidget(separator)
            
            # Label info
            info_title = QLabel("📊 Statistik Pelanggan")
            info_title.setStyleSheet("font-weight: 600; color: #1e293b; margin-bottom: 8px;")
            form_layout.addWidget(info_title)
            
            # Info layout dalam grid
            info_grid = QGridLayout()
            info_grid.setSpacing(20)
            info_grid.setContentsMargins(0, 0, 0, 0)
            
            # Poin
            poin_label = QLabel("⭐ Poin")
            poin_label.setStyleSheet("color: #64748b; font-size: 12px;")
            poin_value_num = safe_float(self.customer.get('poin', 0))
            poin_value = QLabel(f"{poin_value_num:,.0f}")
            poin_value.setStyleSheet("color: #f59e0b; font-size: 18px; font-weight: 600;")
            info_grid.addWidget(poin_label, 0, 0)
            info_grid.addWidget(poin_value, 1, 0)
            
            # Total Belanja
            total_label = QLabel("💰 Total Belanja")
            total_label.setStyleSheet("color: #64748b; font-size: 12px;")
            total_value_num = safe_float(self.customer.get('total_belanja', 0))
            total_value = QLabel(f"Rp {total_value_num:,.0f}")
            total_value.setStyleSheet("color: #10b981; font-size: 18px; font-weight: 600;")
            info_grid.addWidget(total_label, 0, 1)
            info_grid.addWidget(total_value, 1, 1)
            
            # Terakhir Transaksi
            last_trans = self.customer.get('terakhir_transaksi', '-')
            if last_trans and last_trans != '-':
                last_label = QLabel("🕐 Terakhir Transaksi")
                last_label.setStyleSheet("color: #64748b; font-size: 12px;")
                last_value = QLabel(last_trans[:19] if len(last_trans) > 19 else last_trans)
                last_value.setStyleSheet("color: #475569; font-size: 13px;")
                info_grid.addWidget(last_label, 0, 2)
                info_grid.addWidget(last_value, 1, 2)
            
            info_grid.setColumnStretch(0, 1)
            info_grid.setColumnStretch(1, 1)
            info_grid.setColumnStretch(2, 1)
            form_layout.addLayout(info_grid)
        
        layout.addLayout(form_layout)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 8px 0;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        save_btn = QPushButton("Simpan")
        save_btn.setStyleSheet(STYLE_ADD_BUTTON)
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self.save_customer)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Setup validation
        self.nama_input.textChanged.connect(self.clear_error)
        self.telp_input.textChanged.connect(self.clear_error)
    
    def clear_error(self):
        """Clear error indicator"""
        self.error_label.setVisible(False)
        self.nama_input.setStyleSheet("")
        self.telp_input.setStyleSheet("")
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.setVisible(True)
        self.nama_input.setStyleSheet("border-color: #ef4444; background-color: #fef2f2;")
    
    def save_customer(self):
        """Save customer data"""
        nama = self.nama_input.text().strip()
        
        if not nama:
            self.show_error("Nama pelanggan harus diisi!")
            return
        
        data = {
            'nama': nama,
            'no_telp': self.telp_input.text().strip(),
            'email': self.email_input.text().strip(),
            'alamat': self.alamat_input.toPlainText().strip()
        }
        
        if self.customer:
            # Update existing
            data['id_pelanggan'] = self.customer['id_pelanggan']
            result = DatabaseHelper.update_customer(self.customer['id_pelanggan'], data)
            success_msg = "Pelanggan berhasil diupdate"
        else:
            # Add new
            result = DatabaseHelper.add_customer(data)
            success_msg = "Pelanggan baru berhasil ditambahkan"
        
        if result.get('status') == 'success':
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText(f"{success_msg}!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            self.accept()
        else:
            self.show_error(result.get('message', 'Gagal menyimpan data'))

# windows/dialogs.py - CustomerDetailDialog

# windows/dialogs.py - CustomerDetailDialog dengan scroll

class CustomerDetailDialog(QDialog):
    """Dialog untuk melihat detail pelanggan"""
    
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(f"Detail Pelanggan - {customer.get('nama', '')}")
        self.setFixedSize(550, 600)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 20px;
            }
            QLabel {
                color: #1e293b;
            }
            QFrame#headerFrame {
                background-color: #f8fafc;
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 10px;
            }
            QFrame#infoFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame#statsFrame {
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
            }
            QLabel#sectionTitle {
                font-size: 14px;
                font-weight: 600;
                color: #0f172a;
                margin-bottom: 12px;
            }
            QLabel#statValue {
                font-size: 18px;
                font-weight: 600;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
                min-height: 36px;
            }
            QPushButton#closeBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#closeBtn:hover {
                background-color: #e2e8f0;
            }
            QPushButton#editBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#editBtn:hover {
                background-color: #2563eb;
            }
            QFrame#separator {
                background-color: #e2e8f0;
                max-height: 1px;
                margin: 12px 0;
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
        # Main layout dengan scroll area
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
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header dengan avatar
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setStyleSheet("""
            font-size: 48px;
            background-color: #e2e8f0;
            border-radius: 50px;
            padding: 12px;
        """)
        header_layout.addWidget(avatar)
        
        # Info nama dan kode
        name_layout = QVBoxLayout()
        name_label = QLabel(self.customer.get('nama', '-'))
        name_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a;")
        name_layout.addWidget(name_label)
        
        code_label = QLabel(f"Kode: {self.customer.get('kode_pelanggan', '-')}")
        code_label.setStyleSheet("color: #64748b; font-size: 12px;")
        name_layout.addWidget(code_label)
        
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Informasi Kontak
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)
        
        info_title = QLabel("📋 Informasi Kontak")
        info_title.setObjectName("sectionTitle")
        info_layout.addWidget(info_title)
        
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        info_grid.setColumnStretch(1, 1)
        
        info_items = [
            ("📞 Telepon", self.customer.get('no_telp', '-')),
            ("✉️ Email", self.customer.get('email', '-')),
            ("📍 Alamat", self.customer.get('alamat', '-'))
        ]
        
        for i, (icon, value) in enumerate(info_items):
            label = QLabel(icon)
            label.setStyleSheet("font-size: 14px; min-width: 32px;")
            info_grid.addWidget(label, i, 0)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #1e293b;")
            value_label.setWordWrap(True)
            info_grid.addWidget(value_label, i, 1)
        
        info_layout.addLayout(info_grid)
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Statistik
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(12)
        
        stats_title = QLabel("📊 Statistik Belanja")
        stats_title.setObjectName("sectionTitle")
        stats_layout.addWidget(stats_title)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        stats_grid.setColumnStretch(0, 1)
        stats_grid.setColumnStretch(1, 1)
        stats_grid.setColumnStretch(2, 1)
        
        # Poin
        # poin_value = safe_float(self.customer.get('poin', 0))
        # poin_label = QLabel("⭐ Poin")
        # poin_label.setStyleSheet("color: #64748b; font-size: 11px;")
        # poin_value_label = QLabel(f"{poin_value:,.0f}")
        # poin_value_label.setStyleSheet("color: #f59e0b; font-size: 20px; font-weight: 600;")
        # stats_grid.addWidget(poin_label, 0, 0)
        # stats_grid.addWidget(poin_value_label, 1, 0)
        
        # Total Belanja
        total_value = safe_float(self.customer.get('total_belanja', 0))
        total_label = QLabel("💰 Total Belanja")
        total_label.setStyleSheet("color: #64748b; font-size: 11px;")
        total_value_label = QLabel(f"Rp {total_value:,.0f}")
        total_value_label.setStyleSheet("color: #10b981; font-size: 20px; font-weight: 600;")
        stats_grid.addWidget(total_label, 0, 1)
        stats_grid.addWidget(total_value_label, 1, 1)
        
        # Jumlah Transaksi
        # trans_count = self.customer.get('jumlah_transaksi', 0)
        # trans_label = QLabel("🔄 Transaksi")
        # trans_label.setStyleSheet("color: #64748b; font-size: 11px;")
        # trans_value_label = QLabel(f"{safe_int(trans_count)}")
        # trans_value_label.setStyleSheet("color: #3b82f6; font-size: 20px; font-weight: 600;")
        # stats_grid.addWidget(trans_label, 0, 2)
        # stats_grid.addWidget(trans_value_label, 1, 2)
        
        stats_layout.addLayout(stats_grid)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        stats_layout.addWidget(separator)
        
        # Ringkasan
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)
        
        # rata_rata = total_value / safe_int(trans_count) if safe_int(trans_count) > 0 else 0
        
        # Bergabung
        joined = self.customer.get('created_at', '-')
        joined_date = joined[:10] if joined and len(joined) > 10 else '-'
        
        summary_items = [
            ("🕐 Bergabung", joined_date),
            ("🕐 Terakhir", self.customer.get('terakhir_transaksi', '-')[:19] if self.customer.get('terakhir_transaksi') else '-')
        ]
        
        for label, value in summary_items:
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #64748b; font-size: 10px;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 500;")
            value_widget.setWordWrap(True)
            item_layout.addWidget(label_widget)
            item_layout.addWidget(value_widget)
            item_widget.setLayout(item_layout)
            summary_layout.addWidget(item_widget)
        
        stats_layout.addLayout(summary_layout)
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        edit_btn = QPushButton("✏️ Edit Pelanggan")
        edit_btn.setObjectName("editBtn")
        edit_btn.setMinimumHeight(40)
        edit_btn.setStyleSheet(STYLE_ADD_BUTTON)
        edit_btn.clicked.connect(self.edit_customer)
        
        close_btn = QPushButton("Tutup")
        close_btn.setObjectName("closeBtn")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def edit_customer(self):
        """Open edit customer dialog"""
        self.close()
        dialog = CustomerDialog(self.parent(), self.customer)
        if dialog.exec():
            # Refresh parent
            if hasattr(self.parent(), 'load_customers'):
                self.parent().load_customers()

# windows/dialogs.py - AddStockDialog dengan opsi update harga

class AddStockDialog(QDialog):
    """Dialog untuk menambah stok ke produk yang sudah ada dengan opsi update harga"""
    
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Tambah Stok - {product.get('brand', '')}")
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
                margin-top: 8px;
                margin-bottom: 2px;
            }
            QLineEdit, QDoubleSpinBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #10b981;
            }
            QRadioButton {
                color: #1e293b;
                font-size: 13px;
                margin-right: 20px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:checked {
                background-color: #10b981;
                border-radius: 8px;
            }
            QGroupBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: 500;
            }
            QGroupBox::title {
                left: 12px;
                padding: 0 8px;
                color: #10b981;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                border: none;
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
            QFrame#infoFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 10px;
                border: 1px solid #e2e8f0;
            }
            QFrame#previewFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
                border: 1px solid #e2e8f0;
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
        """)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel(f"📦 Tambah Stok - {self.product.get('brand', '')}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info produk
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        stok_saat_ini = safe_float(self.product.get('stok_karung', 0))
        harga_saat_ini = safe_float(self.product.get('harga_jual_kg', 0))
        
        info_text = f"""
        <b>Brand:</b> {self.product.get('brand', '-')}<br>
        <b>Kode:</b> {self.product.get('kode_barang', '-')}<br>
        <b>Harga Saat Ini:</b> Rp {harga_saat_ini:,.0f}/KG<br>
        <b>Stok Saat Ini:</b> {stok_saat_ini:.1f} karung ({stok_saat_ini * 50:.0f} KG)
        """
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.RichText)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Form
        # Keterangan
        layout.addWidget(QLabel("Keterangan (Opsional)"))
        self.keterangan_input = QLineEdit()
        self.keterangan_input.setPlaceholderText("Contoh: Pembelian dari supplier A")
        self.keterangan_input.setMinimumHeight(40)
        layout.addWidget(self.keterangan_input)
        
        # Jumlah Stok Ditambahkan
        layout.addWidget(QLabel("Jumlah Stok Ditambahkan (Karung) *"))
        self.jumlah_input = QLineEdit()
        self.jumlah_input.setPlaceholderText("Contoh: 50")
        self.jumlah_input.setMinimumHeight(40)
        layout.addWidget(self.jumlah_input)
        
        # Harga Beli (untuk pencatatan)
        layout.addWidget(QLabel("Harga Beli per KG (Rp) - Untuk Catatan"))
        self.harga_beli_input = QLineEdit()
        self.harga_beli_input.setPlaceholderText("Contoh: 8500")
        self.harga_beli_input.setMinimumHeight(40)
        layout.addWidget(self.harga_beli_input)
        
        # ==================== OPSI UPDATE HARGA ====================
        price_group = QGroupBox("Opsi Update Harga Jual")
        price_layout = QVBoxLayout()
        price_layout.setSpacing(10)
        
        # Radio buttons
        self.keep_price_radio = QRadioButton("Gunakan harga lama (Rp " + f"{harga_saat_ini:,.0f}" + "/KG)")
        self.keep_price_radio.setStyleSheet("""
            QRadioButton {
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px;
            }

            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #888;
                background-color: #fff;
            }

            QRadioButton::indicator:hover {
                border: 2px solid #555;
            }

            QRadioButton::indicator:checked {
                background-color: #2ecc71;   /* hijau industrial */
                border: 2px solid #27ae60;
            }

            QRadioButton::indicator:unchecked {
                background-color: #f5f5f5;
                border: 2px solid #aaa;
            }
            """)
        self.keep_price_radio.setChecked(True)
        self.update_price_radio = QRadioButton("Update dengan harga baru")
        self.update_price_radio.setStyleSheet("""
            QRadioButton {
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px;
            }

            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #888;
                background-color: #fff;
            }

            QRadioButton::indicator:hover {
                border: 2px solid #555;
            }

            QRadioButton::indicator:checked {
                background-color: #2ecc71;   /* hijau industrial */
                border: 2px solid #27ae60;
            }

            QRadioButton::indicator:unchecked {
                background-color: #f5f5f5;
                border: 2px solid #aaa;
            }
            """)
        
        price_layout.addWidget(self.keep_price_radio)
        price_layout.addWidget(self.update_price_radio)
        
        # Input harga baru
        self.new_price_layout = QHBoxLayout()
        self.new_price_layout.addWidget(QLabel("Harga Baru per KG (Rp):"))
        self.new_price_input = QLineEdit()
        self.new_price_input.setPlaceholderText("Contoh: 12000")
        self.new_price_input.setMinimumHeight(40)
        self.new_price_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f7fa;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px;
            }

            QLineEdit:focus {
                border: 1px solid #2ecc71;
                background-color: #ffffff;
            }

            QLineEdit:disabled {
                background-color: #e0e0e0;
                color: #888;
                border: 1px solid #bbb;
            }
            """)    
        if self.update_price_radio.isChecked():
            self.new_price_input.setEnabled(True)
        else:
            self.new_price_input.setEnabled(False)
        self.new_price_layout.addWidget(self.new_price_input, 1)
        
        price_layout.addLayout(self.new_price_layout)
        
        # Connect radio buttons
        self.update_price_radio.toggled.connect(self.on_price_option_changed)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # Preview
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("Preview akan muncul setelah input")
        self.preview_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px 0;")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        save_btn = QPushButton("💾 Tambah Stok")
        # save_btn.setObjectName("saveBtn")
        save_btn.setStyleSheet(STYLE_ADD_BUTTON)
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self.add_stock)
        
        cancel_btn = QPushButton("❌ Batal")
        # cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Update preview
        self.jumlah_input.textChanged.connect(self.update_preview)
        self.new_price_input.textChanged.connect(self.update_preview)
        self.update_price_radio.toggled.connect(self.update_preview)
        self.update_preview()
    
    def on_price_option_changed(self, checked):
        """Saat opsi update harga dipilih"""
        self.new_price_input.setEnabled(checked)
        self.update_preview()
    
    def update_preview(self):
        try:
            brand = self.product.get('brand', '-')
            stok_saat_ini = safe_float(self.product.get('stok_karung', 0))
            harga_saat_ini = safe_float(self.product.get('harga_jual_kg', 0))
            jumlah_tambah = float(self.jumlah_input.text()) if self.jumlah_input.text() else 0
            stok_baru = stok_saat_ini + jumlah_tambah
            kg_tambah = jumlah_tambah * 50
            kg_baru = stok_baru * 50
            
            # Harga yang akan digunakan
            if self.update_price_radio.isChecked() and self.new_price_input.text():
                harga_baru = float(self.new_price_input.text())
                harga_terpakai = harga_baru
                status_harga = f"🔄 Harga diupdate: Rp {harga_saat_ini:,.0f} → Rp {harga_baru:,.0f}/KG"
            else:
                harga_terpakai = harga_saat_ini
                status_harga = f"💰 Harga tetap: Rp {harga_saat_ini:,.0f}/KG"
            
            # Nilai stok
            nilai_stok_lama = stok_saat_ini * 50 * harga_saat_ini
            nilai_tambahan = jumlah_tambah * 50 * harga_terpakai
            nilai_stok_baru = (stok_baru * 50 * harga_terpakai)
            
            self.preview_label.setText(
                f"📦 {brand}\n"
                f"📊 Stok Saat Ini: {stok_saat_ini:.1f} karung ({stok_saat_ini * 50:.0f} KG)\n"
                f"➕ Ditambah: {jumlah_tambah:.1f} karung ({kg_tambah:.0f} KG)\n"
                f"📊 Stok Baru: {stok_baru:.1f} karung ({kg_baru:.0f} KG)\n"
                f"{status_harga}\n"
                f"💎 Nilai Stok Lama: Rp {nilai_stok_lama:,.0f}\n"
                f"💎 Nilai Tambahan: Rp {nilai_tambahan:,.0f}\n"
                f"💎 Nilai Stok Baru: Rp {nilai_stok_baru:,.0f}"
            )
        except:
            self.preview_label.setText("Masukkan jumlah stok dengan benar")
    
    def add_stock(self):
        """Menambah stok ke produk yang sudah ada (dengan opsi update harga)"""
        if not self.jumlah_input.text().strip():
            self.show_error("Jumlah stok harus diisi!")
            return
        
        try:
            jumlah_tambah = float(self.jumlah_input.text())
            if jumlah_tambah <= 0:
                self.show_error("Jumlah stok harus lebih dari 0!")
                return
            
            stok_saat_ini = safe_float(self.product.get('stok_karung', 0))
            stok_baru = stok_saat_ini + jumlah_tambah
            kg_baru = stok_baru * 50
            
            # Tentukan harga jual baru
            if self.update_price_radio.isChecked() and self.new_price_input.text():
                harga_baru = float(self.new_price_input.text())
                if harga_baru <= 0:
                    self.show_error("Harga baru harus lebih dari 0!")
                    return
                update_harga = True
            else:
                harga_baru = safe_float(self.product.get('harga_jual_kg', 0))
                update_harga = False
            
            # Data untuk update
            update_data = {
                'id_barang': self.product.get('id_barang'),
                'brand': self.product.get('brand'),
                'harga_beli_kg': float(self.harga_beli_input.text()) if self.harga_beli_input.text() else self.product.get('harga_beli_kg', 0),
                'harga_jual_kg': harga_baru,
                'stok_karung': stok_baru,
                'stok_kg': kg_baru,
                'berat_per_karung': self.product.get('berat_per_karung', 50),
                'stok_minimum_karung': self.product.get('stok_minimum_karung', 2)
            }
            
            # Update stok di database
            result = DatabaseHelper.update_product(self.product.get('id_barang'), update_data)
            
            if result.get('status') == 'success':
                # Tambahkan log stok
                keterangan = self.keterangan_input.text().strip() or "Penambahan stok manual"
                if update_harga:
                    keterangan += f" (Harga diupdate dari Rp {self.product.get('harga_jual_kg', 0):,.0f} menjadi Rp {harga_baru:,.0f}/KG)"
                
                DatabaseHelper.add_stock_log(
                    id_barang=self.product.get('id_barang'),
                    kode_barang=self.product.get('kode_barang', '-'),
                    brand=self.product.get('brand', '-'),
                    jenis_transaksi='MASUK',
                    jumlah_karung=jumlah_tambah,
                    jumlah_kg=jumlah_tambah * 50,
                    stok_sebelum_karung=stok_saat_ini,
                    stok_sebelum_kg=stok_saat_ini * 50,
                    stok_sesudah_karung=stok_baru,
                    stok_sesudah_kg=kg_baru,
                    keterangan=keterangan,
                    user="Admin"
                )
                
                msg = f"✅ Stok berhasil ditambahkan!\n\n"
                msg += f"Brand: {self.product.get('brand')}\n"
                msg += f"Ditambah: {jumlah_tambah:.1f} karung\n"
                msg += f"Stok Baru: {stok_baru:.1f} karung\n"
                if update_harga:
                    msg += f"Harga Baru: Rp {harga_baru:,.0f}/KG"
                else:
                    msg += f"Harga Tetap: Rp {harga_baru:,.0f}/KG"
                
                QMessageBox.information(self, "Sukses", msg)
                self.accept()
            else:
                self.show_error(result.get('message', 'Gagal menambahkan stok'))
                
        except ValueError as e:
            self.show_error(f"Format angka tidak valid: {e}")
        except Exception as e:
            self.show_error(str(e))
    
    def show_error(self, message):
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.setVisible(True)