# windows/customer_history_dialog.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah

class CustomerHistoryDialog(QDialog):
    """Dialog untuk menampilkan history transaksi lengkap pelanggan"""
    
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.transactions = []
        self.transaction_count = 0
        self.setWindowTitle(f"History Transaksi - {customer.get('nama', '')}")
        self.setFixedSize(1100, 750)  # Diperbesar
        self.setModal(True)
        # self.setStyleSheet("""
        #     QDialog {
        #         background-color: #f8fafc;
        #         border-radius: 20px;
        #     }
        #     QGroupBox {
        #         font-weight: bold;
        #         border: 1px solid #e2e8f0;
        #         border-radius: 12px;
        #         margin-top: 12px;
        #         padding-top: 12px;
        #         background-color: white;
        #     }
        #     QGroupBox::title {
        #         color: #10b981;
        #         left: 12px;
        #         padding: 0 8px;
        #     }
        #     QTableWidget {
        #         border: 1px solid #e2e8f0;
        #         border-radius: 10px;
        #         background-color: white;
        #         gridline-color: #f1f5f9;
        #     }
        #     QTableWidget::item {
        #         padding: 8px;
        #     }
        #     QTableWidget::item:selected {
        #         background-color: #10b981;
        #         color: white;
        #     }
        #     QHeaderView::section {
        #         background-color: #f8fafc;
        #         padding: 12px 8px;
        #         font-weight: 600;
        #         border: none;
        #         border-bottom: 2px solid #10b981;
        #         font-size: 12px;
        #     }
        #     QPushButton {
        #         border-radius: 10px;
        #         padding: 10px 24px;
        #         font-weight: 600;
        #         border: none;
        #         font-size: 13px;
        #     }
        #     QPushButton#closeBtn {
        #         background-color: #f1f5f9;
        #         color: #475569;
        #     }
        #     QPushButton#closeBtn:hover {
        #         background-color: #e2e8f0;
        #     }
        #     QPushButton#printBtn {
        #         background-color: #10b981;
        #         color: white;
        #     }
        #     QPushButton#printBtn:hover {
        #         background-color: #059669;
        #     }
        #     QFrame#headerFrame {
        #         background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        #             stop:0 #10b981, stop:1 #059669);
        #         border-radius: 16px;
        #         padding: 20px;
        #         margin-bottom: 10px;
        #     }
        #     QLabel#headerTitle {
        #         color: white;
        #         font-size: 20px;
        #         font-weight: bold;
        #     }
        #     QLabel#headerSubtitle {
        #         color: rgba(255,255,255,0.9);
        #         font-size: 12px;
        #     }
        #     QFrame#summaryFrame {
        #         background-color: white;
        #         border-radius: 12px;
        #         padding: 15px;
        #         border: 1px solid #e2e8f0;
        #     }
        #     QScrollArea {
        #         border: none;
        #         background-color: transparent;
        #     }
        #     QScrollBar:vertical {
        #         border: none;
        #         background-color: #f1f5f9;
        #         width: 10px;
        #         border-radius: 5px;
        #     }
        #     QScrollBar::handle:vertical {
        #         background-color: #cbd5e1;
        #         border-radius: 5px;
        #         min-height: 40px;
        #     }
        #     QScrollBar::handle:vertical:hover {
        #         background-color: #94a3b8;
        #     }
        #     QScrollBar:horizontal {
        #         border: none;
        #         background-color: #f1f5f9;
        #         height: 10px;
        #         border-radius: 5px;
        #     }
        #     QScrollBar::handle:horizontal {
        #         background-color: #cbd5e1;
        #         border-radius: 5px;
        #         min-width: 40px;
        #     }
        # """)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area utama
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        container = QWidget()
        container.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # ==================== HEADER GRADIENT ====================
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        # Icon dan judul
        icon_layout = QHBoxLayout()
        icon_label = QLabel("👤")
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch()
        header_layout.addLayout(icon_layout)
        
        title_label = QLabel(self.customer.get('nama', '-'))
        title_label.setObjectName("headerTitle")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        kode_label = QLabel(f"Kode Pelanggan: {self.customer.get('kode_pelanggan', '-')}")
        kode_label.setObjectName("headerSubtitle")
        kode_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(kode_label)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # ==================== RINGKASAN ====================
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_belanja = safe_float(self.customer.get('total_belanja', 0))
        poin = safe_float(self.customer.get('poin', 0))
        
        summary_items = [
            ("💰 Total Belanja", f"Rp {total_belanja:,.0f}", "#10b981"),
            ("🔄 Total Transaksi", str(self.transaction_count), "#3b82f6"),
            ("⭐ Poin", f"{poin:,.0f}", "#f59e0b"),
            ("📞 Telepon", self.customer.get('no_telp', '-'), "#64748b"),
            ("✉️ Email", self.customer.get('email', '-'), "#64748b")
        ]
        
        for title, value, color in summary_items:
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #64748b; font-size: 11px;")
            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {color};")
            value_label.setWordWrap(True)
            item_layout.addWidget(title_label)
            item_layout.addWidget(value_label)
            item_widget.setLayout(item_layout)
            summary_layout.addWidget(item_widget)
        
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        # ==================== TABEL RIWAYAT TRANSAKSI ====================
        trans_group = QGroupBox("📋 Riwayat Transaksi")
        trans_layout = QVBoxLayout()
        
        # Scroll area untuk tabel transaksi
        trans_scroll = QScrollArea()
        trans_scroll.setWidgetResizable(True)
        trans_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        trans_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        trans_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        trans_container = QWidget()
        trans_container_layout = QVBoxLayout()
        trans_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(5)
        self.trans_table.setHorizontalHeaderLabels(["No Invoice", "Tanggal", "Karung", "KG", "Total"])
        self.trans_table.setAlternatingRowColors(True)
        self.trans_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Set column widths
        self.trans_table.setColumnWidth(0, 180)
        self.trans_table.setColumnWidth(1, 180)
        self.trans_table.setColumnWidth(2, 100)
        self.trans_table.setColumnWidth(3, 100)
        self.trans_table.setColumnWidth(4, 150)
        
        self.trans_table.verticalHeader().setDefaultSectionSize(45)
        self.trans_table.verticalHeader().setVisible(False)
        
        # Double click untuk detail
        self.trans_table.itemDoubleClicked.connect(self.on_transaction_double_click)
        
        trans_container_layout.addWidget(self.trans_table)
        trans_container.setLayout(trans_container_layout)
        trans_scroll.setWidget(trans_container)
        trans_scroll.setMinimumHeight(250)
        
        trans_layout.addWidget(trans_scroll)
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)
        
        # ==================== TABEL DETAIL ITEM ====================
        detail_group = QGroupBox("📦 Detail Item Pembelian")
        detail_layout = QVBoxLayout()
        
        # Scroll area untuk tabel detail
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        detail_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        detail_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        detail_container = QWidget()
        detail_container_layout = QVBoxLayout()
        detail_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels(["Tanggal", "Brand", "Jumlah (Karung)", "Subtotal"])
        self.detail_table.setAlternatingRowColors(True)
        
        self.detail_table.setColumnWidth(0, 150)
        self.detail_table.setColumnWidth(1, 250)
        self.detail_table.setColumnWidth(2, 120)
        self.detail_table.setColumnWidth(3, 180)
        
        self.detail_table.verticalHeader().setDefaultSectionSize(45)
        self.detail_table.verticalHeader().setVisible(False)
        
        detail_container_layout.addWidget(self.detail_table)
        detail_container.setLayout(detail_container_layout)
        detail_scroll.setWidget(detail_container)
        detail_scroll.setMinimumHeight(200)
        
        detail_layout.addWidget(detail_scroll)
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        # ==================== TOMBOL ====================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Tombol cetak
        print_btn = QPushButton("🖨️ Cetak History")
        print_btn.setObjectName("printBtn")
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self.print_history)
        btn_layout.addWidget(print_btn)
        
        # Tombol tutup
        close_btn = QPushButton("✕ Tutup")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Load data
        self.load_history()
    
    def load_history(self):
        """Load transaction history for customer"""
        try:
            # Ambil semua transaksi pelanggan
            customer_id = self.customer.get('id_pelanggan')
            all_transactions = DatabaseHelper.get_transactions_with_details()
            
            self.transactions = [t for t in all_transactions if t.get('id_pelanggan') == customer_id]
            self.transaction_count = len(self.transactions)
            
            # Tampilkan di tabel transaksi
            self.display_transactions()
            
            # Tampilkan semua detail item
            self.display_all_details()
            
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def display_transactions(self):
        """Display transactions in table"""
        if not self.transactions:
            self.trans_table.setRowCount(1)
            self.trans_table.setItem(0, 0, QTableWidgetItem("Belum ada transaksi"))
            return
        
        # Sort by date (most recent first)
        sorted_trans = sorted(self.transactions, key=lambda x: x.get('tanggal_transaksi', ''), reverse=True)
        
        self.trans_table.setRowCount(len(sorted_trans))
        
        for i, t in enumerate(sorted_trans):
            self.trans_table.setItem(i, 0, QTableWidgetItem(t.get('no_invoice', '-')))
            self.trans_table.setItem(i, 1, QTableWidgetItem(t.get('tanggal_transaksi', '-')[:19]))
            self.trans_table.setItem(i, 2, QTableWidgetItem(f"{safe_float(t.get('total_karung', 0)):.1f}"))
            self.trans_table.setItem(i, 3, QTableWidgetItem(f"{safe_float(t.get('total_kg', 0)):.0f}"))
            self.trans_table.setItem(i, 4, QTableWidgetItem(format_rupiah(t.get('total_bayar', 0))))
        
        # Alternating row colors
        for i in range(self.trans_table.rowCount()):
            for j in range(self.trans_table.columnCount()):
                item = self.trans_table.item(i, j)
                if item and i % 2 == 0:
                    item.setBackground(QColor(248, 250, 252))
        
        # Resize rows to contents
        self.trans_table.resizeRowsToContents()
    
    def display_all_details(self):
        """Display all item details from all transactions"""
        all_details = []
        
        for t in self.transactions:
            items = t.get('items', [])
            if not items:
                items = t.get('details', [])
            
            for item in items:
                all_details.append({
                    'tanggal': t.get('tanggal_transaksi', '-')[:16],
                    'brand': item.get('brand', '-'),
                    'jumlah_karung': safe_float(item.get('jumlah_karung', 0)),
                    'subtotal': safe_float(item.get('subtotal', 0))
                })
        
        if not all_details:
            self.detail_table.setRowCount(1)
            self.detail_table.setItem(0, 0, QTableWidgetItem("Belum ada detail"))
            self.detail_table.setItem(0, 1, QTableWidgetItem(""))
            self.detail_table.setItem(0, 2, QTableWidgetItem(""))
            self.detail_table.setItem(0, 3, QTableWidgetItem(""))
            return
        
        # Sort by date (most recent first)
        all_details.sort(key=lambda x: x.get('tanggal', ''), reverse=True)
        
        self.detail_table.setRowCount(len(all_details))
        
        for i, d in enumerate(all_details):
            self.detail_table.setItem(i, 0, QTableWidgetItem(d.get('tanggal', '-')))
            self.detail_table.setItem(i, 1, QTableWidgetItem(d.get('brand', '-')))
            self.detail_table.setItem(i, 2, QTableWidgetItem(f"{d.get('jumlah_karung', 0):.1f}"))
            self.detail_table.setItem(i, 3, QTableWidgetItem(format_rupiah(d.get('subtotal', 0))))
        
        # Alternating row colors
        for i in range(self.detail_table.rowCount()):
            for j in range(self.detail_table.columnCount()):
                item = self.detail_table.item(i, j)
                if item and i % 2 == 0:
                    item.setBackground(QColor(248, 250, 252))
        
        # Resize rows to contents
        self.detail_table.resizeRowsToContents()
    
    def on_transaction_double_click(self, item):
        """Show detail for selected transaction"""
        row = item.row()
        if row < len(self.transactions):
            transaction = self.transactions[row]
            from windows.transaction_detail_window import TransactionDetailWindow
            detail_dialog = TransactionDetailWindow(transaction, self)
            detail_dialog.exec()
    
    def print_history(self):
        """Print customer history"""
        QMessageBox.information(self, "Info", "Fitur cetak history akan segera hadir!")