# pages/transaction_page.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah, events
from windows.dialogs import CustomerDialog
from styles import STYLE_ADD_BUTTON, STYLE_DANGER_BUTTON
from printer import PrintDialog

class TransactionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = []
        self.products = []
        self.customers = []
        self.selected_customer = None
        self.init_ui()
        self.load_data()

        events.subscribe('customer_changed', self.on_customer_changed)
    
    def init_ui(self):
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # ==================== LEFT PANEL ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # === Pelanggan Section ===
        customer_group = QGroupBox("👤 Pelanggan")
        customer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
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
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)
        
        # Pilih pelanggan
        customer_select_layout = QHBoxLayout()
        customer_select_layout.addWidget(QLabel("Pilih:"))
        
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(35)
        self.customer_combo.currentIndexChanged.connect(self.on_customer_selected)
        customer_select_layout.addWidget(self.customer_combo, 1)
        
        add_customer_btn = QPushButton("+ Baru")
        add_customer_btn.setFixedWidth(65)
        add_customer_btn.setMinimumHeight(35)
        add_customer_btn.clicked.connect(self.add_new_customer)
        add_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        customer_select_layout.addWidget(add_customer_btn)
        customer_layout.addLayout(customer_select_layout)
        
        # Info pelanggan
        self.customer_info = QFrame()
        self.customer_info.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        customer_info_layout = QVBoxLayout()
        customer_info_layout.setSpacing(2)
        
        self.customer_name_label = QLabel("Belum memilih pelanggan")
        self.customer_name_label.setStyleSheet("font-weight: bold; color: #ef4444;")
        customer_info_layout.addWidget(self.customer_name_label)
        
        self.customer_contact_label = QLabel("")
        self.customer_contact_label.setStyleSheet("color: #64748b; font-size: 11px;")
        customer_info_layout.addWidget(self.customer_contact_label)
        
        # self.customer_poin_label = QLabel("Poin: 0")
        # self.customer_poin_label.setStyleSheet("color: #f59e0b; font-size: 11px;")
        # customer_info_layout.addWidget(self.customer_poin_label)
        
        self.customer_info.setLayout(customer_info_layout)
        self.customer_info.setVisible(False)
        customer_layout.addWidget(self.customer_info)
        
        # Warning
        self.customer_warning = QLabel("⚠️ Pilih pelanggan terlebih dahulu")
        self.customer_warning.setStyleSheet("color: #ef4444; font-size: 11px; padding: 5px; background-color: #fef2f2; border-radius: 6px;")
        self.customer_warning.setVisible(True)
        customer_layout.addWidget(self.customer_warning)
        
        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)
        
        # === Produk Section dengan Scroll ===
        produk_group = QGroupBox("📦 Daftar Produk")
        produk_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
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
        produk_layout = QVBoxLayout()
        produk_layout.setSpacing(8)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari brand...")
        self.search_input.setMinimumHeight(35)
        search_layout.addWidget(self.search_input, 1)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(35, 35)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self.load_products)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        search_layout.addWidget(refresh_btn)
        produk_layout.addLayout(search_layout)
        
        # Scroll area untuk list produk
        produk_scroll = QScrollArea()
        produk_scroll.setWidgetResizable(True)
        produk_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        produk_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        produk_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
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
        
        self.product_list = QListWidget()
        self.product_list.setAlternatingRowColors(True)
        self.product_list.itemDoubleClicked.connect(self.add_to_cart)
        self.product_list.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)
        
        produk_scroll.setWidget(self.product_list)
        produk_layout.addWidget(produk_scroll, 1)
        
        produk_group.setLayout(produk_layout)
        left_layout.addWidget(produk_group, 1)
        
        left_panel.setLayout(left_layout)
        
        # ==================== RIGHT PANEL ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # === Keranjang Section dengan Scroll ===
        cart_group = QGroupBox("🛒 Keranjang Belanja")
        cart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
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
        cart_layout = QVBoxLayout()
        cart_layout.setSpacing(8)
        
        # Scroll area untuk tabel keranjang
        cart_scroll = QScrollArea()
        cart_scroll.setWidgetResizable(True)
        cart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        cart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        cart_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
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
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Brand", "Karung", "KG", "Harga", "Subtotal"])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.verticalHeader().setDefaultSectionSize(55)
        
        # Set column widths
        self.cart_table.setColumnWidth(0, 140)
        self.cart_table.setColumnWidth(1, 100)
        self.cart_table.setColumnWidth(2, 100)
        self.cart_table.setColumnWidth(3, 125)
        self.cart_table.setColumnWidth(4, 150)
        
        cart_scroll.setWidget(self.cart_table)
        cart_layout.addWidget(cart_scroll, 1)
        
        # Total
        total_widget = QWidget()
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel("TOTAL:")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(total_label)
        self.total_label = QLabel("Rp 0")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        total_layout.addWidget(self.total_label)
        total_widget.setLayout(total_layout)
        cart_layout.addWidget(total_widget)
        
        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group, 2)
        
        # === Pembayaran Section ===
        payment_group = QGroupBox("💵 Pembayaran")
        payment_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
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
        payment_layout = QGridLayout()
        payment_layout.setSpacing(8)
        payment_layout.setContentsMargins(15, 10, 15, 15)
        
        payment_layout.addWidget(QLabel("Uang Bayar:"), 0, 0)
        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("Masukkan jumlah uang")
        self.payment_input.setMinimumHeight(40)
        self.payment_input.textChanged.connect(self.calculate_change)
        payment_layout.addWidget(self.payment_input, 0, 1)
        
        payment_layout.addWidget(QLabel("Kembalian:"), 1, 0)
        self.change_label = QLabel("Rp 0")
        self.change_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")
        payment_layout.addWidget(self.change_label, 1, 1)
        
        # payment_layout.addWidget(QLabel("Poin Didapat:"), 2, 0)
        # self.poin_label = QLabel("0")
        # self.poin_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
        # payment_layout.addWidget(self.poin_label, 2, 1)
        
        payment_group.setLayout(payment_layout)
        right_layout.addWidget(payment_group)
        
        # === Tombol Aksi ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        clear_btn = QPushButton("🗑️ Bersihkan")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_cart)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_layout.addWidget(clear_btn)
        
        self.process_btn = QPushButton("✅ Proses Transaksi")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.clicked.connect(self.process_transaction)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_layout.addWidget(self.process_btn)
        
        right_layout.addLayout(btn_layout)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        self.setLayout(layout)
    
    def load_data(self):
        """Load products and customers"""
        self.load_products()
        self.load_customers()
    
    def load_products(self):
        """Load products from database"""
        try:
            self.products = DatabaseHelper.get_products()
            self.display_products(self.products)
        except Exception as e:
            print(f"Error loading products: {e}")

    def on_customer_changed(self, data):
        """Handle when customer data changes"""
        print(f"Customer changed: {data}")  # Debug
        self.load_customers()  # Refresh customer list
    
    def load_customers(self):
        """Load customers to combo box"""
        try:
            self.customers = DatabaseHelper.get_customers()
            current_customer_id = None
            
            # Save current selected customer id
            if self.selected_customer:
                current_customer_id = self.selected_customer.get('id_pelanggan')
            
            # Clear and reload combo
            self.customer_combo.clear()
            self.customer_combo.addItem("-- Pilih Pelanggan --", None)
            
            for c in self.customers:
                self.customer_combo.addItem(f"{c.get('nama')} ({c.get('kode_pelanggan')})", c)
            
            # Restore selection if customer still exists
            if current_customer_id:
                for i in range(self.customer_combo.count()):
                    customer = self.customer_combo.itemData(i)
                    if customer and customer.get('id_pelanggan') == current_customer_id:
                        self.customer_combo.setCurrentIndex(i)
                        self.selected_customer = customer
                        self.customer_info.setVisible(True)
                        self.customer_warning.setVisible(False)
                        self.update_customer_info()
                        break
                else:
                    # Customer no longer exists
                    self.selected_customer = None
                    self.customer_info.setVisible(False)
                    self.customer_warning.setVisible(True)
            else:
                self.selected_customer = None
                self.customer_info.setVisible(False)
                self.customer_warning.setVisible(True)
                
        except Exception as e:
            print(f"Error loading customers: {e}")

    def update_customer_info(self):
        """Update customer info display"""
        if self.selected_customer:
            self.customer_name_label.setText(f"👤 {self.selected_customer.get('nama')}")
            self.customer_contact_label.setText(f"📞 {self.selected_customer.get('no_telp', '-')} | ✉️ {self.selected_customer.get('email', '-')}")
            # self.customer_poin_label.setText(f"⭐ Poin: {self.selected_customer.get('poin', 0)}")
    
    def add_new_customer(self):
        """Add new customer dialog"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_customers()  # Refresh customer list
            # Auto select the new customer
            if self.customers:
                self.customer_combo.setCurrentIndex(self.customer_combo.count() - 1)
    
    def __del__(self):
        """Cleanup event subscription"""
        try:
            events.unsubscribe('customer_changed', self.on_customer_changed)
        except:
            pass
    
    def on_customer_selected(self, index):
        """Handle customer selection"""
        self.selected_customer = self.customer_combo.currentData()
        if self.selected_customer:
            self.customer_info.setVisible(True)
            self.customer_warning.setVisible(False)
            self.customer_name_label.setText(f"👤 {self.selected_customer.get('nama')}")
            self.customer_contact_label.setText(f"📞 {self.selected_customer.get('no_telp', '-')} | ✉️ {self.selected_customer.get('email', '-')}")
            # self.customer_poin_label.setText(f"⭐ Poin: {self.selected_customer.get('poin', 0)}")
        else:
            self.customer_info.setVisible(False)
            self.customer_warning.setVisible(True)
    
    def add_new_customer(self):
        """Add new customer dialog"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_customers()  # Refresh customer list
            # Auto select the new customer
            self.customer_combo.setCurrentIndex(self.customer_combo.count() - 1)
    
    def display_products(self, products):
        """Display products in list"""
        self.product_list.clear()
        for p in products:
            try:
                stok = safe_float(p.get('stok_karung', 0))
                if stok > 0:
                    harga_kg = safe_float(p.get('harga_jual_kg', 0))
                    berat = safe_float(p.get('berat_per_karung', 50))
                    harga_karung = harga_kg * berat
                    text = f"{p.get('brand')} | Stok: {stok:.1f} karung | Rp {harga_karung:,.0f}/karung"
                    self.product_list.addItem(text)
            except:
                continue
    
    def search_products(self, text):
        """Search products"""
        if not text:
            self.display_products(self.products)
        else:
            filtered = [p for p in self.products if text.lower() in p.get('brand', '').lower()]
            self.display_products(filtered)
    
    def add_to_cart(self, item):
        """Add product to cart"""
        brand = item.text().split(' | ')[0]
        product = next((p for p in self.products if p.get('brand') == brand), None)
        
        if product:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Tambah {product.get('brand')}")
            dialog.setFixedSize(400, 350)
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            # Info produk
            info_text = f"""
            <b>{product.get('brand')}</b><br>
            Harga: Rp {product.get('harga_jual_kg'):,.0f}/KG<br>
            Stok: {product.get('stok_karung'):.1f} karung
            """
            info = QLabel(info_text)
            info.setTextFormat(Qt.RichText)
            info.setStyleSheet("background-color: #f8fafc; padding: 12px; border-radius: 8px;")
            layout.addWidget(info)
            
            # Input jumlah
            layout.addWidget(QLabel("Jumlah (Karung):"))
            spin = QDoubleSpinBox()
            spin.setRange(1, product.get('stok_karung')) # set range penjualan DISINIIII
            spin.setSingleStep(1) # set range penjualan DISINIIII
            spin.setDecimals(1)
            spin.setSuffix(" karung")
            spin.setMinimumHeight(35)
            layout.addWidget(spin)
            
            # Preview
            preview = QLabel()
            preview.setStyleSheet("color: #10b981; font-weight: bold; margin-top: 5px;")
            layout.addWidget(preview)
            
            def update_preview():
                karung = spin.value()
                harga_karung = product.get('harga_jual_kg') * product.get('berat_per_karung')
                subtotal = karung * harga_karung
                kg = karung * product.get('berat_per_karung')
                preview.setText(f"Subtotal: Rp {subtotal:,.0f} | {kg:.0f} KG")
            
            spin.valueChanged.connect(lambda x: update_preview())
            update_preview()
            
            # Buttons
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("Tambah ke Keranjang")
            # ok_btn.setObjectName("primaryBtn")
            ok_btn.setStyleSheet(STYLE_ADD_BUTTON)
            ok_btn.clicked.connect(lambda: self.confirm_add(product, spin.value(), dialog))
            cancel_btn = QPushButton("Batal")
            cancel_btn.setStyleSheet(STYLE_DANGER_BUTTON)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
    
    def confirm_add(self, product, jumlah, dialog):
        """Add item to cart"""
        harga_karung = product.get('harga_jual_kg') * product.get('berat_per_karung')
        subtotal = jumlah * harga_karung
        
        item = {
            'id_barang': product.get('id_barang'),
            'brand': product.get('brand'),
            'jumlah': jumlah,
            'harga': harga_karung,
            'subtotal': subtotal,
            'kg': jumlah * product.get('berat_per_karung')
        }
        self.cart.append(item)
        self.update_cart()
        dialog.accept()
    
    def update_cart(self):
        """Update cart table"""
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['brand']))
            self.cart_table.setItem(i, 1, QTableWidgetItem(f"{item['jumlah']:.1f}"))
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"{item['kg']:.0f}"))
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"Rp {item['harga']:,.0f}"))
            self.cart_table.setItem(i, 4, QTableWidgetItem(f"Rp {item['subtotal']:,.0f}"))
            total += item['subtotal']
        
        self.total_label.setText(f"Rp {total:,.0f}")
        self.calculate_change()
        
        # Update poin (1 poin per Rp 10,000)
        # poin = int(total / 10000)
        # self.poin_label.setText(str(poin))
    
    def calculate_change(self):
        """Calculate change"""
        try:
            total = safe_float(self.total_label.text().replace("Rp ", "").replace(",", ""))
            bayar = safe_float(self.payment_input.text())
            self.change_label.setText(f"Rp {bayar - total:,.0f}")
        except:
            self.change_label.setText("Rp 0")
    
    def clear_cart(self):
        """Clear cart"""
        self.cart = []
        self.update_cart()
        self.payment_input.clear()
        self.change_label.setText("Rp 0")
        # self.poin_label.setText("0")

    def process_transaction(self):
        """Process transaction with stock log"""
        # VALIDASI: Cek apakah pelanggan sudah dipilih
        if not self.selected_customer:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText("Silahkan pilih pelanggan terlebih dahulu!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            return
        
        if not self.cart:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText("Silahkan tambahkan produk terlebih dahulu!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            return
        
        total = sum(item['subtotal'] for item in self.cart)
        bayar = safe_float(self.payment_input.text())
        
        if bayar < total:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText(f"Uang pembayaran tidak mencukupi. Total: Rp {total:,.0f} | Bayar: Rp {bayar:,.0f}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            return
        
        kembali = bayar - total
        
        try:
            # Simpan transaksi
            result = DatabaseHelper.save_transaction(
                self.cart, total, bayar, kembali, "Admin", 
                self.selected_customer.get('id_pelanggan')
            )
            
            if result.get('status') == 'success':
                # Update poin pelanggan
                # poin_tambah = int(total / 10000)
                # DatabaseHelper.update_customer_poin(
                #     self.selected_customer.get('id_pelanggan'),
                #     poin_tambah,
                #     total
                # )
                
                # Tambahkan log stok untuk setiap item di keranjang
                for item in self.cart:
                    # Ambil data produk sebelum transaksi
                    product = next((p for p in self.products if p.get('id_barang') == item['id_barang']), None)
                    if product:
                        stok_sebelum_karung = safe_float(product.get('stok_karung', 0))
                        stok_sebelum_kg = safe_float(product.get('stok_kg', 0))
                        stok_sesudah_karung = stok_sebelum_karung - item['jumlah']
                        stok_sesudah_kg = stok_sebelum_kg - (item['jumlah'] * 50)
                        
                        # Tambahkan log stok
                        DatabaseHelper.add_stock_log(
                            id_barang=item['id_barang'],
                            kode_barang=product.get('kode_barang', '-'),
                            brand=item['brand'],
                            jenis_transaksi='TRANSAKSI',
                            jumlah_karung=item['jumlah'],
                            jumlah_kg=item['jumlah'] * 50,
                            stok_sebelum_karung=stok_sebelum_karung,
                            stok_sebelum_kg=stok_sebelum_kg,
                            stok_sesudah_karung=stok_sesudah_karung,
                            stok_sesudah_kg=stok_sesudah_kg,
                            keterangan=f"Transaksi penjualan - Invoice: {result.get('no_invoice', '-')}",
                            no_referensi=result.get('no_invoice', '-'),
                            user="Admin"
                        )
                
                # Show success message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Transaksi Berhasil")
                msg.setText(f"""
                ✅ Transaksi Berhasil!
                
                Pelanggan: {self.selected_customer.get('nama')}
                No Invoice: {result.get('no_invoice', '-')}
                Total: Rp {total:,.0f}
                Bayar: Rp {bayar:,.0f}
                Kembali: Rp {kembali:,.0f}
                """)
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Yes)
                msg.button(QMessageBox.Ok).setText("OK")
                msg.button(QMessageBox.Yes).setText("Cetak Nota")
                
                reply = msg.exec()
                
                if reply == QMessageBox.Yes:
                    transaction_data_print = {
                        'no_invoice': result.get('no_invoice', '-'),
                        'tanggal_transaksi': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'total_bayar': total,
                        'uang_bayar': bayar,
                        'uang_kembali': kembali,
                        'kasir': "Admin",
                        'pelanggan': self.selected_customer.get('nama'),
                        'pelanggan_kode': self.selected_customer.get('kode_pelanggan'),
                        'pelanggan_telp': self.selected_customer.get('no_telp')
                    }
                    details = []
                    for item in self.cart:
                        details.append({
                            'brand': item['brand'],
                            'jumlah_karung': item['jumlah'],
                            'jumlah_kg': item['kg'],
                            'subtotal': item['subtotal']
                        })
                    # QuickReceiptPrinter.print_receipt(transaction_data_print, details)
                    PrintDialog(transaction_data_print, details).exec()
                
                self.clear_cart()
                self.load_products()
                self.load_customers()
                
            else:
                QMessageBox.critical(self, "Error", f"❌ Transaksi gagal: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Koneksi gagal: {e}")
            print(f"Transaction error: {e}")