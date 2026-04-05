# pages/dashboard_page.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime, timedelta
from database_helper import DatabaseHelper
from utils import safe_float, format_rupiah
import calendar

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.transactions = []
        self.products = []
        self.init_ui()
        self.load_data()
        
        # Auto refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)
    
    def init_ui(self):
        # Main layout dengan scroll area
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8fafc;
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
        
        # Container untuk konten dashboard
        container = QWidget()
        container.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📊 Tampilan Awal")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1f2937;")
        header.addWidget(title)
        header.addStretch()
        
        # Date selector
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedWidth(120)
        self.date_edit.setMinimumHeight(32)
        self.date_edit.dateChanged.connect(self.on_date_changed)
        header.addWidget(QLabel("Tanggal:"))
        header.addWidget(self.date_edit)
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # ==================== RINGKASAN HARI INI ====================
        ringkasan_group = QGroupBox("📊 Ringkasan Hari Ini")
        ringkasan_group.setStyleSheet("""
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
        ringkasan_layout = QVBoxLayout()
        ringkasan_layout.setSpacing(12)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        
        self.card_penjualan = self.create_stat_card("💰 Penjualan", "Rp 0", "#10b981")
        self.card_transaksi = self.create_stat_card("🔄 Transaksi", "0", "#3b82f6")
        self.card_karung = self.create_stat_card("📦 Karung", "0", "#f59e0b")
        self.card_kg = self.create_stat_card("⚖️ KG", "0", "#8b5cf6")
        
        cards_layout.addWidget(self.card_penjualan)
        cards_layout.addWidget(self.card_transaksi)
        cards_layout.addWidget(self.card_karung)
        cards_layout.addWidget(self.card_kg)
        
        ringkasan_layout.addLayout(cards_layout)
        ringkasan_group.setLayout(ringkasan_layout)
        layout.addWidget(ringkasan_group)
        
        # ==================== RINGKASAN STOK ====================
        stok_group = QGroupBox("📦 Ringkasan Stok")
        stok_group.setStyleSheet("""
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
        stok_layout = QVBoxLayout()
        stok_layout.setSpacing(12)
        
        stok_cards = QHBoxLayout()
        stok_cards.setSpacing(12)
        
        self.card_total_stok = self.create_stat_card("📦 Total Stok", "0 Karung", "#10b981")
        self.card_total_kg_stok = self.create_stat_card("⚖️ Total KG", "0 KG", "#3b82f6")
        self.card_stok_menipis = self.create_stat_card("⚠️ Stok Menipis", "0 Brand", "#ef4444")
        self.card_jenis_barang = self.create_stat_card("🏷️ Jenis Barang", "0 Brand", "#8b5cf6")
        
        stok_cards.addWidget(self.card_total_stok)
        stok_cards.addWidget(self.card_total_kg_stok)
        stok_cards.addWidget(self.card_stok_menipis)
        stok_cards.addWidget(self.card_jenis_barang)
        
        stok_layout.addLayout(stok_cards)
        stok_group.setLayout(stok_layout)
        layout.addWidget(stok_group)
        
        # ==================== RINGKASAN BULAN INI ====================
        bulanan_group = QGroupBox("📆 Ringkasan Bulan Ini")
        bulanan_group.setStyleSheet("""
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
        bulanan_layout = QVBoxLayout()
        bulanan_layout.setSpacing(12)
        
        bulanan_cards = QHBoxLayout()
        bulanan_cards.setSpacing(12)
        
        self.card_bulan_penjualan = self.create_stat_card("💰 Penjualan", "Rp 0", "#10b981")
        self.card_bulan_transaksi = self.create_stat_card("🔄 Transaksi", "0", "#3b82f6")
        self.card_bulan_karung = self.create_stat_card("📦 Karung", "0", "#f59e0b")
        self.card_bulan_kg = self.create_stat_card("⚖️ KG", "0", "#8b5cf6")
        self.card_rata_rata = self.create_stat_card("📊 Rata-rata", "Rp 0", "#ec489a")
        
        bulanan_cards.addWidget(self.card_bulan_penjualan)
        bulanan_cards.addWidget(self.card_bulan_transaksi)
        bulanan_cards.addWidget(self.card_bulan_karung)
        bulanan_cards.addWidget(self.card_bulan_kg)
        bulanan_cards.addWidget(self.card_rata_rata)
        
        bulanan_layout.addLayout(bulanan_cards)
        bulanan_group.setLayout(bulanan_layout)
        layout.addWidget(bulanan_group)
        
        # ==================== TRANSAKSI TERBARU ====================
        recent_group = QGroupBox("🕐 Transaksi Terbaru")
        recent_group.setStyleSheet("""
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
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["No Invoice", "Tanggal", "Kasir", "Karung", "Total"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setMinimumHeight(280)
        
        # Set column widths
        self.recent_table.setColumnWidth(0, 140)
        self.recent_table.setColumnWidth(1, 140)
        self.recent_table.setColumnWidth(2, 90)
        self.recent_table.setColumnWidth(3, 70)
        self.recent_table.setColumnWidth(4, 110)
        
        self.recent_table.verticalHeader().setDefaultSectionSize(36)
        self.recent_table.verticalHeader().setVisible(False)
        
        recent_layout.addWidget(self.recent_table)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_stat_card(self, title, value, color):
        """Create statistic card with fixed size"""
        card = QFrame()
        card.setFixedHeight(150)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
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
        value_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        return card
    
    def on_date_changed(self, date):
        """Handle date change"""
        self.load_data()
    
    def load_data(self):
        """Load all dashboard data"""
        try:
            selected_date = self.date_edit.date().toString("yyyy-MM-dd")
            current_month = datetime.now().strftime("%Y-%m")
            current_year = datetime.now().strftime("%Y")
            
            # 1. Get products data
            self.products = DatabaseHelper.get_products()
            
            # 2. Get today's transactions
            today_transactions = DatabaseHelper.get_transactions(start_date=selected_date)
            
            # 3. Get this month's transactions
            month_start = f"{current_month}-01"
            last_day = calendar.monthrange(int(current_year), int(current_month.split('-')[1]))[1]
            month_end = f"{current_month}-{last_day}"
            month_transactions = DatabaseHelper.get_transactions(start_date=month_start, end_date=month_end)
            
            # 4. Update all stats
            self.update_stats_cards(self.products, today_transactions, month_transactions)
            
            # 5. Update recent transactions
            self.update_recent_transactions(today_transactions)
            
        except Exception as e:
            print(f"Error loading dashboard: {e}")
    
    def update_stats_cards(self, products, today_transactions, month_transactions):
        """Update all statistics cards"""
        try:
            # === Ringkasan Hari Ini ===
            total_penjualan = sum(safe_float(t.get('total_bayar', 0)) for t in today_transactions)
            total_karung = sum(safe_float(t.get('total_karung', 0)) for t in today_transactions)
            total_kg = sum(safe_float(t.get('total_kg', 0)) for t in today_transactions)
            jumlah_transaksi = len(today_transactions)
            
            self.card_penjualan.value_label.setText(format_rupiah(total_penjualan))
            self.card_transaksi.value_label.setText(str(jumlah_transaksi))
            self.card_karung.value_label.setText(f"{total_karung:.1f}")
            self.card_kg.value_label.setText(f"{total_kg:.0f}")
            
            # === Ringkasan Stok ===
            total_stok = sum(safe_float(p.get('stok_karung', 0)) for p in products)
            total_kg_stok = sum(safe_float(p.get('stok_kg', 0)) for p in products)
            stok_menipis = sum(1 for p in products if safe_float(p.get('stok_karung', 0)) <= safe_float(p.get('stok_minimum_karung', 2)))
            jenis_barang = len(products)
            
            self.card_total_stok.value_label.setText(f"{total_stok:.1f} Karung")
            self.card_total_kg_stok.value_label.setText(f"{total_kg_stok:.0f} KG")
            self.card_stok_menipis.value_label.setText(f"{stok_menipis} Brand")
            self.card_jenis_barang.value_label.setText(f"{jenis_barang} Brand")
            
            # === Ringkasan Bulan Ini ===
            total_penjualan_bulan = sum(safe_float(t.get('total_bayar', 0)) for t in month_transactions)
            total_karung_bulan = sum(safe_float(t.get('total_karung', 0)) for t in month_transactions)
            total_kg_bulan = sum(safe_float(t.get('total_kg', 0)) for t in month_transactions)
            jumlah_transaksi_bulan = len(month_transactions)
            rata_rata = total_penjualan_bulan / jumlah_transaksi_bulan if jumlah_transaksi_bulan > 0 else 0
            
            self.card_bulan_penjualan.value_label.setText(format_rupiah(total_penjualan_bulan))
            self.card_bulan_transaksi.value_label.setText(str(jumlah_transaksi_bulan))
            self.card_bulan_karung.value_label.setText(f"{total_karung_bulan:.1f}")
            self.card_bulan_kg.value_label.setText(f"{total_kg_bulan:.0f}")
            self.card_rata_rata.value_label.setText(format_rupiah(rata_rata))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def update_recent_transactions(self, transactions):
        """Update recent transactions table"""
        try:
            if not transactions:
                self.recent_table.setRowCount(1)
                self.recent_table.setItem(0, 0, QTableWidgetItem("Belum ada transaksi"))
                return
            
            # Sort by date, most recent first
            sorted_trans = sorted(transactions, key=lambda x: x.get('tanggal_transaksi', ''), reverse=True)[:10]
            
            self.recent_table.setRowCount(len(sorted_trans))
            
            for i, trans in enumerate(sorted_trans):
                self.recent_table.setItem(i, 0, QTableWidgetItem(trans.get('no_invoice', '-')))
                self.recent_table.setItem(i, 1, QTableWidgetItem(trans.get('tanggal_transaksi', '-')[:19]))
                self.recent_table.setItem(i, 2, QTableWidgetItem(trans.get('kasir', '-')))
                self.recent_table.setItem(i, 3, QTableWidgetItem(f"{safe_float(trans.get('total_karung', 0)):.1f}"))
                self.recent_table.setItem(i, 4, QTableWidgetItem(format_rupiah(trans.get('total_bayar', 0))))
            
            # Alternating row colors
            for i in range(self.recent_table.rowCount()):
                for j in range(self.recent_table.columnCount()):
                    item = self.recent_table.item(i, j)
                    if item and i % 2 == 0:
                        item.setBackground(QColor(248, 250, 252))
                        
        except Exception as e:
            print(f"Error updating recent transactions: {e}")