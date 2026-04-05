# windows/transaction_detail_window.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from printer import QuickReceiptPrinter, PrintDialog
from utils import safe_float, format_rupiah, format_tanggal
from styles import STYLE_REFRESH_BUTTON, STYLE_DANGER_BUTTON
from database_helper import DatabaseHelper

class TransactionDetailWindow(QDialog):
    """Window untuk menampilkan detail transaksi"""
    
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.setWindowTitle(f"Detail Transaksi - {transaction.get('no_invoice', '-')}")
        self.setFixedSize(700, 650)
        self.setModal(True)

        self._is_closing = False

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                color: #3b82f6;
                left: 12px;
                padding: 0 8px;
            }
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3b82f6;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                font-weight: 600;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                border: none;
            }
            QPushButton#printBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#printBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#closeBtn {
                background-color: #f1f5f9;
                color: #475569;
            }
            QPushButton#closeBtn:hover {
                background-color: #e2e8f0;
            }
            QFrame#headerFrame {
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 5px;
            }
            QFrame#customerFrame {
                background-color: #fef9e3;
                border: 1px solid #fde047;
                border-radius: 10px;
                padding: 12px;
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
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        
        invoice_title = QLabel("INVOICE")
        invoice_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #3b82f6;")
        invoice_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(invoice_title)
        
        no_invoice = QLabel(self.transaction.get('no_invoice', '-'))
        no_invoice.setStyleSheet("font-size: 14px; font-weight: 500;")
        no_invoice.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(no_invoice)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Informasi Pelanggan (jika ada)
        customer_data = self.get_customer_data()
        if customer_data:
            customer_frame = QFrame()
            customer_frame.setObjectName("customerFrame")
            customer_layout = QHBoxLayout()
            customer_layout.setSpacing(15)
            
            # Icon
            icon_label = QLabel("👤")
            icon_label.setStyleSheet("font-size: 28px;")
            customer_layout.addWidget(icon_label)
            
            # Info pelanggan
            info_layout = QVBoxLayout()
            info_layout.setSpacing(4)
            
            name_label = QLabel(f"<b>{customer_data.get('nama', '-')}</b>")
            name_label.setStyleSheet("font-size: 14px;")
            info_layout.addWidget(name_label)
            
            code_label = QLabel(f"Kode: {customer_data.get('kode_pelanggan', '-')}")
            code_label.setStyleSheet("color: #64748b; font-size: 11px;")
            info_layout.addWidget(code_label)
            
            contact_text = ""
            if customer_data.get('no_telp'):
                contact_text += f"📞 {customer_data.get('no_telp')}"
            if customer_data.get('email'):
                if contact_text:
                    contact_text += " | ✉️ "
                else:
                    contact_text += "✉️ "
                contact_text += customer_data.get('email')
            
            if contact_text:
                contact_label = QLabel(contact_text)
                contact_label.setStyleSheet("color: #64748b; font-size: 11px;")
                info_layout.addWidget(contact_label)
            
            # poin_label = QLabel(f"⭐ Poin: {safe_float(customer_data.get('poin', 0)):,.0f}")
            # poin_label.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: 500;")
            # info_layout.addWidget(poin_label)
            
            customer_layout.addLayout(info_layout)
            customer_layout.addStretch()
            
            customer_frame.setLayout(customer_layout)
            layout.addWidget(customer_frame)
        
        # Informasi Transaksi
        info_group = QGroupBox("Informasi Transaksi")
        info_layout = QGridLayout()
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        # Data transaksi
        no_invoice = self.transaction.get('no_invoice', '-')
        tanggal = self.transaction.get('tanggal_transaksi', '-')
        if len(tanggal) > 19:
            tanggal = tanggal[:19]
        kasir = self.transaction.get('kasir', '-')
        
        info_layout.addWidget(QLabel("No. Invoice:"), 0, 0)
        info_layout.addWidget(QLabel(f"<b>{no_invoice}</b>"), 0, 1)
        
        info_layout.addWidget(QLabel("Tanggal:"), 1, 0)
        info_layout.addWidget(QLabel(tanggal), 1, 1)
        
        info_layout.addWidget(QLabel("Kasir:"), 2, 0)
        info_layout.addWidget(QLabel(kasir), 2, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Tabel Item Belanja - Fixed height
        items_group = QGroupBox("Item Belanja")
        items_group.setFixedHeight(250)
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Brand", "Jumlah (Karung)", "KG", "Harga/Karung", "Subtotal"])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.items_table.setColumnWidth(0, 150)
        self.items_table.setColumnWidth(1, 100)
        self.items_table.setColumnWidth(2, 80)
        self.items_table.setColumnWidth(3, 120)
        self.items_table.setColumnWidth(4, 120)
        
        self.items_table.verticalHeader().setVisible(False)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Ringkasan Total - Fixed height
        summary_group = QGroupBox("Ringkasan")
        summary_group.setFixedHeight(220)
        summary_layout = QGridLayout()
        summary_layout.setSpacing(10)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        
        total_karung = safe_float(self.transaction.get('total_karung', 0))
        total_kg = safe_float(self.transaction.get('total_kg', 0))
        total_bayar = safe_float(self.transaction.get('total_bayar', 0))
        uang_bayar = safe_float(self.transaction.get('uang_bayar', 0))
        uang_kembali = safe_float(self.transaction.get('uang_kembali', 0))
        
        summary_layout.addWidget(QLabel("Total Karung:"), 0, 0)
        summary_layout.addWidget(QLabel(f"<b>{total_karung:.1f} karung</b>"), 0, 1)
        
        summary_layout.addWidget(QLabel("Total KG:"), 1, 0)
        summary_layout.addWidget(QLabel(f"<b>{total_kg:.0f} KG</b>"), 1, 1)
        
        summary_layout.addWidget(QLabel("Total Bayar:"), 2, 0)
        summary_layout.addWidget(QLabel(f"<b style='color:#10b981'>Rp {total_bayar:,.0f}</b>"), 2, 1)
        
        summary_layout.addWidget(QLabel("Uang Bayar:"), 3, 0)
        summary_layout.addWidget(QLabel(f"Rp {uang_bayar:,.0f}"), 3, 1)
        
        summary_layout.addWidget(QLabel("Kembalian:"), 4, 0)
        summary_layout.addWidget(QLabel(f"Rp {uang_kembali:,.0f}"), 4, 1)
        
        # Tambahkan informasi poin didapat jika ada pelanggan
        # if customer_data:
        #     poin_didapat = int(total_bayar / 10000)
        #     summary_layout.addWidget(QLabel("Poin Didapat:"), 5, 0)
        #     summary_layout.addWidget(QLabel(f"<b style='color:#f59e0b'>+{poin_didapat} poin</b>"), 5, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Tombol Aksi
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        print_btn = QPushButton("Cetak Nota")
        # print_btn.setObjectName("printBtn")
        print_btn.setStyleSheet(STYLE_REFRESH_BUTTON)
        print_btn.setFixedSize(120, 40)
        print_btn.clicked.connect(self.print_receipt)
        btn_layout.addWidget(print_btn)
        
        close_btn = QPushButton("Tutup")
        # close_btn.setObjectName("closeBtn")
        close_btn.setStyleSheet(STYLE_DANGER_BUTTON)
        close_btn.setFixedSize(100, 40)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Load items
        self.load_items()
    
    def get_customer_data(self):
        """Get customer data from transaction"""
        # Cek langsung dari transaksi
        if 'pelanggan' in self.transaction:
            return self.transaction.get('pelanggan')
        
        # Cek apakah ada data pelanggan langsung
        if self.transaction.get('customer_name'):
            return {
                'nama': self.transaction.get('customer_name'),
                'kode_pelanggan': self.transaction.get('customer_code', '-'),
                'no_telp': self.transaction.get('customer_phone', '-'),
                'email': self.transaction.get('customer_email', '-')
            }
        
        # Cek apakah ada id_pelanggan
        customer_id = self.transaction.get('id_pelanggan')
        if customer_id:
            customer = DatabaseHelper.get_customer_by_id(customer_id)
            if customer:
                return customer
        
        # Cek dari items atau details
        items = self.transaction.get('items', [])
        if items and len(items) > 0:
            # Cek apakah ada data pelanggan di item pertama
            if 'customer' in items[0]:
                return items[0].get('customer')
        
        return None
    
    def load_items(self):
        """Load items to table"""
        items = self.transaction.get('items', [])
        
        if not items:
            items = self.transaction.get('details', [])
        
        self.items_table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            brand = item.get('brand', '-')
            qty = safe_float(item.get('jumlah_karung', item.get('qty', 0)))
            kg = safe_float(item.get('jumlah_kg', item.get('kg', qty * 50)))
            harga = safe_float(item.get('harga_per_karung', item.get('harga', 0)))
            subtotal = safe_float(item.get('subtotal', 0))
            
            self.items_table.setItem(i, 0, QTableWidgetItem(brand))
            self.items_table.setItem(i, 1, QTableWidgetItem(f"{qty:.1f}"))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"{kg:.0f}"))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"Rp {harga:,.0f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"Rp {subtotal:,.0f}"))
        
        self.items_table.resizeColumnsToContents()
    
    def print_receipt(self):
        """Print receipt for this transaction"""
        
        # Prepare data for printing
        transaction_data = {
            'no_invoice': self.transaction.get('no_invoice', '-'),
            'tanggal_transaksi': self.transaction.get('tanggal_transaksi', '-'),
            'total_bayar': self.transaction.get('total_bayar', 0),
            'uang_bayar': self.transaction.get('uang_bayar', 0),
            'uang_kembali': self.transaction.get('uang_kembali', 0),
            'kasir': self.transaction.get('kasir', 'Admin')
        }
        
        # Tambahkan info pelanggan
        customer = self.get_customer_data()
        if customer:
            transaction_data['pelanggan'] = customer.get('nama')
            transaction_data['pelanggan_kode'] = customer.get('kode_pelanggan')
            transaction_data['pelanggan_telp'] = customer.get('no_telp')
        
        details = []
        items = self.transaction.get('items', [])
        if not items:
            items = self.transaction.get('details', [])
        
        for item in items:
            details.append({
                'brand': item.get('brand', '-'),
                'jumlah_karung': safe_float(item.get('jumlah_karung', item.get('qty', 0))),
                'jumlah_kg': safe_float(item.get('jumlah_kg', item.get('kg', 0))),
                'subtotal': safe_float(item.get('subtotal', 0))
            })
        
        # Cetak dengan 3 rangkap
        # ReceiptPrinterWithCopies.print_receipt(transaction_data, details, 1)

        dialog = PrintDialog(transaction_data, details, self)
        dialog.exec_()