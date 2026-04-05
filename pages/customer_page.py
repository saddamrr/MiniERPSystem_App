# pages/customer_page.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah
from windows.dialogs import CustomerDialog
from utils import events, show_info
from styles import STYLE_ADD_BUTTON, STYLE_REFRESH_BUTTON
from windows.dialogs import CustomerDetailDialog

class CustomerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.customers = []
        self.current_page = 1
        self.items_per_page = 3
        self.total_pages = 1
        self.init_ui()
        self.load_customers()
        
        # Auto refresh setiap 30 detik
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_customers)
        self.timer.start(30000)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # ==================== HEADER ====================
        header = QHBoxLayout()
        
        title = QLabel("👥 Manajemen Pelanggan")
        title.setStyleSheet("font-size: 24px; font-weight: 600; color: #0f172a;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari nama atau telepon...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.search_customers)
        header.addWidget(self.search_input)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.load_customers)
        refresh_btn.setStyleSheet(STYLE_REFRESH_BUTTON)
        header.addWidget(refresh_btn)
        
        # Add button
        add_btn = QPushButton("+ Tambah Pelanggan")
        add_btn.setMinimumHeight(40)
        add_btn.setFixedWidth(140)
        add_btn.clicked.connect(self.add_customer)
        add_btn.setStyleSheet(STYLE_ADD_BUTTON)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # ==================== STATISTIK ====================
        stats_group = QGroupBox("📊 Statistik Pelanggan")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                color: #10b981;
                left: 12px;
                padding: 0 8px;
            }
        """)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Stat cards
        self.card_total = self.create_stat_card("👥 Total Pelanggan", "0", "#3b82f6")
        # self.card_poin = self.create_stat_card("⭐ Total Poin", "0", "#f59e0b")
        self.card_belanja = self.create_stat_card("💰 Total Belanja", "Rp 0", "#10b981")
        self.card_rata = self.create_stat_card("📊 Rata-rata Belanja", "Rp 0", "#8b5cf6")
        
        stats_layout.addWidget(self.card_total)
        # stats_layout.addWidget(self.card_poin)
        stats_layout.addWidget(self.card_belanja)
        stats_layout.addWidget(self.card_rata)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # ==================== TABEL PELANGGAN ====================
        table_group = QGroupBox("📋 Daftar Pelanggan")
        table_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                color: #10b981;
                left: 12px;
                padding: 0 8px;
            }
        """)
        table_layout = QVBoxLayout()
        
        # Scroll area untuk tabel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f1f5f9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 5px;
                min-height: 30px;
            }
        """)
        
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(6)
        self.customer_table.setHorizontalHeaderLabels([
            "Kode", "Nama", "No Telepon", "Alamat", "Email", "Aksi"
        ])
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set column widths
        self.customer_table.setColumnWidth(0, 80)
        self.customer_table.setColumnWidth(1, 200)
        self.customer_table.setColumnWidth(2, 120)
        self.customer_table.setColumnWidth(3, 220)
        self.customer_table.setColumnWidth(4, 180)
        self.customer_table.setColumnWidth(5, 120)
        
        self.customer_table.verticalHeader().setDefaultSectionSize(55)
        self.customer_table.verticalHeader().setVisible(False)

        self.customer_table.itemDoubleClicked.connect(self.mouseDoubleClickEvent)
        
        scroll_area.setWidget(self.customer_table)
        scroll_area.setMinimumHeight(450)
        
        table_layout.addWidget(scroll_area)
        
        # ==================== PAGINATION ====================
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        pagination_layout.addStretch()
        
        # Previous button
        self.prev_btn = QPushButton("◀ Sebelumnya")
        self.prev_btn.setFixedSize(100, 32)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton:disabled {
                background-color: #f8fafc;
                color: #cbd5e1;
            }
        """)
        pagination_layout.addWidget(self.prev_btn)
        
        # Page info
        self.page_info = QLabel("Halaman 1 dari 1")
        self.page_info.setStyleSheet("color: #64748b; font-size: 12px; margin: 0 15px;")
        pagination_layout.addWidget(self.page_info)
        
        # Next button
        self.next_btn = QPushButton("Selanjutnya ▶")
        self.next_btn.setFixedSize(100, 32)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton:disabled {
                background-color: #f8fafc;
                color: #cbd5e1;
            }
        """)
        pagination_layout.addWidget(self.next_btn)
        
        pagination_layout.addStretch()
        pagination_widget.setLayout(pagination_layout)
        
        table_layout.addWidget(pagination_widget)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # ==================== INFO ====================
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #fef9e3;
                border: 1px solid #fde047;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QHBoxLayout()
        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 12px;")
        info_text = QLabel("Tips: Double klik pada baris untuk melihat detail, atau klik tombol Edit untuk mengubah data.")
        info_text.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        self.setLayout(layout)
    
    def create_stat_card(self, title, value, color):
        """Create statistic card"""
        card = QFrame()
        card.setFixedSize(250, 150)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 500; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        return card
    
    def load_customers(self):
        """Load all customers from database"""
        try:
            self.customers = DatabaseHelper.get_customers()
            self.total_pages = max(1, (len(self.customers) + self.items_per_page - 1) // self.items_per_page)
            self.current_page = min(self.current_page, self.total_pages)
            self.update_page()
            self.update_stats()
        except Exception as e:
            print(f"Error loading customers: {e}")

    def update_page(self):
        """Update current page display"""
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_customers = self.customers[start:end]
        
        self.display_customers(page_customers)
        
        # Update pagination buttons
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        self.page_info.setText(f"Halaman {self.current_page} dari {self.total_pages}")

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_page()
    
    def display_customers(self, customers):
        """Display customers in table"""
        self.customer_table.setRowCount(len(customers))
        
        for i, c in enumerate(customers):
            # Kode
            kode_item = QTableWidgetItem(c.get('kode_pelanggan', '-'))
            kode_item.setForeground(QColor("#475569"))
            self.customer_table.setItem(i, 0, kode_item)
            
            # Nama
            nama_item = QTableWidgetItem(c.get('nama', '-'))
            nama_item.setForeground(QColor("#0f172a"))
            nama_item.setToolTip(c.get('nama', '-'))
            self.customer_table.setItem(i, 1, nama_item)
            
            # No Telepon
            telp_item = QTableWidgetItem(c.get('no_telp', '-'))
            telp_item.setForeground(QColor("#475569"))
            self.customer_table.setItem(i, 2, telp_item)
            
            # Alamat
            alamat = c.get('alamat', '-')
            alamat_short = alamat[:30] + '...' if len(alamat) > 30 else alamat
            alamat_item = QTableWidgetItem(alamat_short)
            alamat_item.setToolTip(alamat)
            alamat_item.setForeground(QColor("#475569"))
            self.customer_table.setItem(i, 3, alamat_item)
            
            # Email
            email_item = QTableWidgetItem(c.get('email', '-'))
            email_item.setForeground(QColor("#475569"))
            email_item.setToolTip(c.get('email', '-'))
            self.customer_table.setItem(i, 4, email_item)
            
            # Poin
            # poin = safe_float(c.get('poin', 0))
            # poin_item = QTableWidgetItem(f"{poin:,.0f}")
            # poin_item.setForeground(QColor("#f59e0b"))
            # self.customer_table.setItem(i, 5, poin_item)
            
            # Action buttons
            widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setSpacing(6)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 30)
            edit_btn.clicked.connect(lambda checked, cid=c.get('id_pelanggan'): self.edit_customer(cid))
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border-radius: 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            
            delete_btn = QPushButton("Hapus")
            delete_btn.setFixedSize(55, 30)
            delete_btn.clicked.connect(lambda checked, cid=c.get('id_pelanggan'), name=c.get('nama'): self.delete_customer(cid, name))
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border-radius: 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            widget.setLayout(btn_layout)
            self.customer_table.setCellWidget(i, 5, widget)
        
        # Alternating row colors
        for i in range(self.customer_table.rowCount()):
            for j in range(self.customer_table.columnCount()):
                item = self.customer_table.item(i, j)
                if item and i % 2 == 0:
                    item.setBackground(QColor(248, 250, 252))
    
    def update_stats(self):
        """Update statistics cards"""
        total_customers = len(self.customers)
        # total_poin = sum(safe_float(c.get('poin', 0)) for c in self.customers)
        total_belanja = sum(safe_float(c.get('total_belanja', 0)) for c in self.customers)
        rata_belanja = total_belanja / total_customers if total_customers > 0 else 0
        
        self.card_total.value_label.setText(str(total_customers))
        # self.card_poin.value_label.setText(f"{total_poin:,.0f}")
        self.card_belanja.value_label.setText(format_rupiah(total_belanja))
        self.card_rata.value_label.setText(format_rupiah(rata_belanja))
    
    def search_customers(self, text):
        """Search customers by name or phone"""
        if not text:
            self.load_customers()
        else:
            filtered = [c for c in self.customers if 
                       text.lower() in c.get('nama', '').lower() or 
                       text.lower() in c.get('no_telp', '')]
            self.customers = filtered
            self.total_pages = max(1, (len(self.customers) + self.items_per_page - 1) // self.items_per_page)
            self.current_page = 1
            self.update_page()
            self.update_stats()
        
    def add_customer(self):
        """Add new customer"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_customers()
            events.emit('customer_changed', {'action': 'add'})
            # QMessageBox.information(self, "Sukses", "✅ Pelanggan baru berhasil ditambahkan!")
    
    def edit_customer(self, customer_id):
        """Edit existing customer"""
        customer = next((c for c in self.customers if c.get('id_pelanggan') == customer_id), None)
        if customer:
            dialog = CustomerDialog(self, customer)
            if dialog.exec():
                self.load_customers()
                events.emit('customer_changed', {'action': 'update'})
                # QMessageBox.information(self, "Sukses", "✅ Data pelanggan berhasil diupdate!")
    
    def delete_customer(self, customer_id, customer_name):
        """Delete customer with confirmation"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"Apakah Anda yakin ingin menghapus pelanggan '{customer_name}'?")
        msg_box.setInformativeText("Data yang dihapus tidak dapat dikembalikan.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = DatabaseHelper.delete_customer(customer_id)
                if result.get('status') == 'success':
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Informasi Hapus")
                    msg_box.setText(f"Data pelanggan berhasil dihapus!")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.load_customers()
                    events.emit('customer_changed', {'action': 'delete'})
                else:
                    QMessageBox.warning(self, "Error", f"❌ Gagal menghapus: {result.get('message', 'Unknown error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {e}")
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click on table to view details"""
        index = self.customer_table.currentIndex()
        if index.isValid() and index.row() < len(self.customers):
            customer = self.customers[(self.current_page - 1) * self.items_per_page + index.row()]
            self.show_customer_detail(customer)

    def show_customer_detail(self, customer):
        """Show customer detail dialog"""
        dialog = CustomerDetailDialog(customer, self)
        dialog.exec()
        self.load_customers()