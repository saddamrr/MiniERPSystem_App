# pages/stock_page.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah
from windows.dialogs import AddProductDialog, EditProductDialog
from styles import STYLE_REFRESH_BUTTON, STYLE_ADD_BUTTON
from windows.dialogs import AddStockDialog

class StockPage(QWidget):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current_page = 1
        self.items_per_page = 3
        self.total_pages = 1
        self.init_ui()
        self.load_stock()
        
        # Auto refresh timer setiap 30 detik
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_stock)
        self.timer.start(30000)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # ==================== HEADER ====================
        header = QHBoxLayout()
        
        title = QLabel("📦 Manajemen Stok Barang")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1f2937;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari brand...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.search_stock)
        header.addWidget(self.search_input)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.load_stock)
        refresh_btn.setStyleSheet(STYLE_REFRESH_BUTTON)
        header.addWidget(refresh_btn)
        
        # Add button
        add_btn = QPushButton("+ Tambah Barang")
        add_btn.setMinimumHeight(40)
        add_btn.setFixedWidth(150)
        add_btn.setStyleSheet(STYLE_ADD_BUTTON)
        add_btn.clicked.connect(self.add_product)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # ==================== STATISTIK STOK ====================
        stats_group = QGroupBox("📊 Statistik Stok")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
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
        self.card_total_brand = self.create_stat_card("🏷️ Total Brand", "0", "#10b981")
        self.card_total_stok = self.create_stat_card("📦 Total Stok", "0 Karung", "#3b82f6")
        self.card_total_kg = self.create_stat_card("⚖️ Total KG", "0 KG", "#f59e0b")
        self.card_stok_menipis = self.create_stat_card("⚠️ Stok Menipis", "0 Brand", "#ef4444")
        self.card_nilai_stok = self.create_stat_card("💰 Nilai Stok", "Rp 0", "#8b5cf6")
        
        stats_layout.addWidget(self.card_total_brand)
        stats_layout.addWidget(self.card_total_stok)
        stats_layout.addWidget(self.card_total_kg)
        stats_layout.addWidget(self.card_stok_menipis)
        stats_layout.addWidget(self.card_nilai_stok)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # ==================== TABEL STOK ====================
        table_group = QGroupBox("📋 Daftar Stok Barang")
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
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
        """)
        
        # Container untuk tabel
        table_container = QWidget()
        table_container_layout = QVBoxLayout()
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(9)  # Tambah 1 kolom
        self.stock_table.setHorizontalHeaderLabels([
            "Kode", "Brand", "Harga/KG", "Harga/Karung", 
            "Stok (Karung)", "Stok (KG)", "Status", "Terakhir Update", "Aksi"
        ])
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setSelectionMode(QTableWidget.SingleSelection)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stock_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set column widths
        self.stock_table.setColumnWidth(0, 80)   # Kode
        self.stock_table.setColumnWidth(1, 140)  # Brand
        self.stock_table.setColumnWidth(2, 90)   # Harga/KG
        self.stock_table.setColumnWidth(3, 110)  # Harga/Karung
        self.stock_table.setColumnWidth(4, 100)  # Stok (Karung)
        self.stock_table.setColumnWidth(5, 80)   # Stok (KG)
        self.stock_table.setColumnWidth(6, 100)  # Status
        self.stock_table.setColumnWidth(7, 180)  # Terakhir Update
        self.stock_table.setColumnWidth(8, 110)   # Aksi
        
        # Set row height
        self.stock_table.verticalHeader().setDefaultSectionSize(55)
        self.stock_table.verticalHeader().setVisible(False)
        
        table_container_layout.addWidget(self.stock_table)
        table_container.setLayout(table_container_layout)
        
        scroll_area.setWidget(table_container)
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
        
        # ==================== INFORMASI ====================
        # info_frame = QFrame()
        # info_frame.setStyleSheet("""
        #     QFrame {
        #         background-color: #fef9e3;
        #         border: 1px solid #fde047;
        #         border-radius: 8px;
        #         padding: 10px;
        #     }
        # """)
        # info_layout = QHBoxLayout()
        # info_icon = QLabel("ℹ️")
        # info_icon.setStyleSheet("font-size: 14px;")
        # info_text = QLabel("💡 Tips: Double klik pada baris untuk melihat detail, atau klik tombol Edit untuk mengubah data.")
        # info_text.setStyleSheet("color: #854d0e; font-size: 12px;")
        # info_layout.addWidget(info_icon)
        # info_layout.addWidget(info_text)
        # info_layout.addStretch()
        # info_frame.setLayout(info_layout)
        # layout.addWidget(info_frame)
        
        self.setLayout(layout)
    
    def create_stat_card(self, title, value, color):
        """Create statistic card"""
        card = QFrame()
        card.setFixedSize(250, 150)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #e5e7eb;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        return card
    
    def load_stock(self):
        """Load stock data from database"""
        try:
            self.products = DatabaseHelper.get_products()
            self.total_pages = max(1, (len(self.products) + self.items_per_page - 1) // self.items_per_page)
            self.current_page = min(self.current_page, self.total_pages)
            self.update_page()
            self.update_stats()
        except Exception as e:
            print(f"Error loading stock: {e}")

    def update_page(self):
        """Update current page display"""
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_products = self.products[start:end]
        
        self.display_stock(page_products)
        
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
    
    def display_stock(self, products):
        """Display stock in table"""
        self.stock_table.setRowCount(len(products))
        
        for i, p in enumerate(products):
            try:
                kode = p.get('kode_barang', '-')
                brand = p.get('brand', '-')
                batch = p.get('batch', '-') if not p.get('is_parent', True) else '-'
                harga_kg = safe_float(p.get('harga_jual_kg', 0))
                berat = safe_float(p.get('berat_per_karung', 50))
                harga_karung = harga_kg * berat
                stok = safe_float(p.get('stok_karung', 0))
                stok_min = safe_float(p.get('stok_minimum_karung', 2))
                stok_kg = safe_float(p.get('stok_kg', 0))
                updated = p.get('updated_at', p.get('created_at', '-'))[:19]
                is_parent = p.get('is_parent', True)
                
                # Status
                if stok <= 0:
                    status = "Habis"
                    status_color = "#ef4444"
                elif stok <= stok_min:
                    status = "Stok Menipis"
                    status_color = "#f59e0b"
                else:
                    status = "Stok Aman"
                    status_color = "#10b981"
                
                self.stock_table.setItem(i, 0, QTableWidgetItem(kode))
                self.stock_table.setItem(i, 1, QTableWidgetItem(brand))
                
                # Batch item
                # batch_item = QTableWidgetItem(batch)
                # if not is_parent:
                #     batch_item.setForeground(QColor("#3b82f6"))
                # self.stock_table.setItem(i, 2, batch_item)
                
                self.stock_table.setItem(i, 2, QTableWidgetItem(f"Rp {harga_kg:,.0f}"))
                self.stock_table.setItem(i, 3, QTableWidgetItem(f"Rp {harga_karung:,.0f}"))
                
                stok_item = QTableWidgetItem(f"{stok:.1f}")
                if stok <= stok_min:
                    stok_item.setBackground(QColor(254, 226, 226))
                self.stock_table.setItem(i, 4, stok_item)
                
                self.stock_table.setItem(i, 5, QTableWidgetItem(f"{stok_kg:.0f}"))
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.stock_table.setItem(i, 6, status_item)
                
                self.stock_table.setItem(i, 7, QTableWidgetItem(updated))
                
                # Action buttons
                widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                btn_layout.setSpacing(6)
                
                # Tombol Tambah Stok (hanya untuk produk parent)
                if is_parent:
                    add_stock_btn = QPushButton("➕ Stok")
                    add_stock_btn.setFixedSize(70, 30)
                    add_stock_btn.setCursor(Qt.PointingHandCursor)
                    add_stock_btn.setToolTip("Tambah stok baru dengan harga berbeda")
                    add_stock_btn.clicked.connect(lambda checked, pid=p.get('id_barang'): self.add_stock(pid))
                    add_stock_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #8b5cf6;
                            color: white;
                            border-radius: 6px;
                            font-size: 10px;
                        }
                        QPushButton:hover {
                            background-color: #7c3aed;
                        }
                    """)
                    btn_layout.addWidget(add_stock_btn)
                
                # Edit button
                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(65, 30)
                edit_btn.clicked.connect(lambda checked, pid=p.get('id_barang'): self.edit_product(pid))
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
                
                # Delete button
                delete_btn = QPushButton("Hapus")
                delete_btn.setFixedSize(65, 30)
                delete_btn.clicked.connect(lambda checked, pid=p.get('id_barang'), name=brand: self.delete_product(pid, name))
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
                self.stock_table.setCellWidget(i, 8, widget)
                
            except Exception as e:
                print(f"Error displaying stock row {i}: {e}")
                continue
        
        # Alternating row colors
        for i in range(self.stock_table.rowCount()):
            for j in range(self.stock_table.columnCount()):
                item = self.stock_table.item(i, j)
                if item and i % 2 == 0:
                    item.setBackground(QColor(248, 250, 252))
    
    def update_stats(self):
        """Update statistics cards"""
        total_brand = len(self.products)
        total_stok = sum(safe_float(p.get('stok_karung', 0)) for p in self.products)
        total_kg = sum(safe_float(p.get('stok_kg', 0)) for p in self.products)
        stok_menipis = sum(1 for p in self.products if safe_float(p.get('stok_karung', 0)) <= safe_float(p.get('stok_minimum_karung', 2)))
        nilai_stok = sum(safe_float(p.get('stok_kg', 0)) * safe_float(p.get('harga_jual_kg', 0)) for p in self.products)
        
        self.card_total_brand.value_label.setText(str(total_brand))
        self.card_total_stok.value_label.setText(f"{total_stok:.1f} Karung")
        self.card_total_kg.value_label.setText(f"{total_kg:.0f} KG")
        self.card_stok_menipis.value_label.setText(f"{stok_menipis} Brand")
        self.card_nilai_stok.value_label.setText(format_rupiah(nilai_stok))
    
    def search_stock(self, text):
        """Search stock by brand or code"""
        if not text:
            self.load_stock()
        else:
            filtered = [p for p in self.products if 
                       text.lower() in p.get('brand', '').lower() or 
                       text.lower() in p.get('kode_barang', '').lower()]
            self.products = filtered
            self.total_pages = max(1, (len(self.products) + self.items_per_page - 1) // self.items_per_page)
            self.current_page = 1
            self.update_page()
            self.update_stats()
    
    def add_product(self):
        """Add new product"""
        dialog = AddProductDialog(self)
        if dialog.exec():
            self.load_stock()
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText(f"Produk berhasil ditambahkan!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
    
    def edit_product(self, product_id):
        """Edit existing product"""
        product = next((p for p in self.products if p.get('id_barang') == product_id), None)
        if product:
            dialog = EditProductDialog(product, self)
            if dialog.exec():
                self.load_stock()

                old_stok_karung = safe_float(product.get('stok_karung', 0))
                old_stok_kg = safe_float(product.get('stok_kg', 0))
                
                self.load_stock()
                
                # Ambil data produk setelah update
                new_product = next((p for p in self.products if p.get('id_barang') == product_id), None)
                if new_product:
                    new_stok_karung = safe_float(new_product.get('stok_karung', 0))
                    new_stok_kg = safe_float(new_product.get('stok_kg', 0))
                    
                    # Tentukan jenis transaksi
                    if new_stok_karung > old_stok_karung:
                        jenis = "MASUK"
                        jumlah = new_stok_karung - old_stok_karung
                        keterangan = "Penambahan stok via edit produk"
                    elif new_stok_karung < old_stok_karung:
                        jenis = "KELUAR"
                        jumlah = old_stok_karung - new_stok_karung
                        keterangan = "Pengurangan stok via edit produk"
                    else:
                        return
                    
                    # Tambahkan log stok
                    DatabaseHelper.add_stock_log(
                        id_barang=product_id,
                        kode_barang=product.get('kode_barang', '-'),
                        brand=product.get('brand', '-'),
                        jenis_transaksi=jenis,
                        jumlah_karung=jumlah,
                        jumlah_kg=jumlah * product.get('berat_per_karung', 50),
                        stok_sebelum_karung=old_stok_karung,
                        stok_sebelum_kg=old_stok_kg,
                        stok_sesudah_karung=new_stok_karung,
                        stok_sesudah_kg=new_stok_kg,
                        keterangan=keterangan,
                        user="Admin"
                    )

                msg_box = QMessageBox()
                msg_box.setWindowTitle("Pemberitahuan!")
                msg_box.setText(f"Produk berhasil diubah!")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()
    
    def delete_product(self, product_id, product_name):
        """Delete product with confirmation and error handling"""
        # Konfirmasi dengan detail
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"Apakah Anda yakin ingin menghapus produk '{product_name}'?")
        msg_box.setInformativeText(
            "⚠️ PERINGATAN:\n"
            "- Data yang dihapus tidak dapat dikembalikan\n"
            "- Jika produk ini memiliki riwayat transaksi, penghapusan akan gagal"
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Tampilkan loading
                QApplication.setOverrideCursor(Qt.WaitCursor)
                
                # Panggil API delete
                result = DatabaseHelper.delete_product(product_id)
                
                # Kembalikan cursor
                QApplication.restoreOverrideCursor()
                
                if result.get('status') == 'success':
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Pemberitahuan!")
                    msg_box.setText(f"Produk berhasil dihapus!")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.load_stock()  # Refresh tabel
                else:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Peringatan!")
                    msg_box.setText(f"❌ Gagal menghapus: karena barang ini memiliki riwayat transaksi")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.exec()
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Terjadi kesalahan: {str(e)}"
                )

    def add_stock(self, product_id):
        """Tambah stok baru untuk produk yang sama dengan harga berbeda"""
        product = next((p for p in self.products if p.get('id_barang') == product_id), None)
        if product:
            dialog = AddStockDialog(product, self)
            if dialog.exec():
                self.load_stock()
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Pemberitahuan!")
                msg_box.setText(f"Produk berhasil diubah!")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()