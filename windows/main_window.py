# windows/main_window.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime
from styles import STYLE
from config import COMPANY_DATA
from database_helper import DatabaseHelper
from pages.dashboard_page import DashboardPage
from pages.transaction_page import TransactionPage
from pages.customer_page import CustomerPage
from pages.stock_page import StockPage
from pages.report_page import ReportPage
from windows.dialogs import ChangePasswordDialog
from windows.profile_dialog import ProfileDialog

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"{COMPANY_DATA['nama']}")
        
        # Set window state
        self.setWindowState(Qt.WindowMaximized)
        
        self.setStyleSheet(STYLE)
        
        # Set font default
        default_font = QFont("Segoe UI", 10)
        QApplication.setFont(default_font)
        
        self.is_closing = False
        self.db_status = DatabaseHelper.check_connection()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== SIDEBAR ====================
        sidebar = QFrame()
        sidebar.setFixedWidth(200)  # Lebar sidebar lebih kecil
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(8)
        
        # Logo
        logo_label = QLabel("APP")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 28px;
            color: #10b981;
            padding: 8px;
        """)
        sidebar_layout.addWidget(logo_label)
        
        logo_text = QLabel(f"{COMPANY_DATA['nama']}")
        logo_text.setAlignment(Qt.AlignCenter)
        logo_text.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            padding-bottom: 20px;
        """)
        sidebar_layout.addWidget(logo_text)
        
        sidebar_layout.addSpacing(8)
        
        # Menu items
        menus = [
            ("🏠", "Tampilan Awal", 'dashboard'),
            ("💰", "Transaksi", 'transaksi'),
            ("👥", "Pelanggan", 'pelanggan'),
            ("📦", "Stok", 'stok'),
            ("📊", "Laporan", 'laporan'),
        ]
        
        self.menu_buttons = {}
        
        for icon, text, page in menus:
            btn = QPushButton(f" {icon}  {text}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(44)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    border-radius: 10px;
                    padding: 10px 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1e293b;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, p=page: self.show_page(p))
            sidebar_layout.addWidget(btn)
            self.menu_buttons[page] = btn
        
        sidebar_layout.addStretch()
        
        # Database status
        # status_color = "#10b981" if self.db_status else "#ef4444"
        # status_text = "● Online" if self.db_status else "● Offline"
        # self.db_status_label = QLabel(status_text)
        # self.db_status_label.setAlignment(Qt.AlignCenter)
        # self.db_status_label.setStyleSheet(f"""
        #     color: {status_color};
        #     font-size: 11px;
        #     padding: 12px;
        # """)
        # sidebar_layout.addWidget(self.db_status_label)
        
        # Logout button
        # logout_btn = QPushButton("🚪  Keluar")
        # logout_btn.setCursor(Qt.PointingHandCursor)
        # logout_btn.setMinimumHeight(44)
        # logout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # logout_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: transparent;
        #         color: #f43f5e;
        #         border-radius: 10px;
        #         padding: 10px 12px;
        #         text-align: left;
        #         font-size: 13px;
        #         font-weight: 500;
        #     }
        #     QPushButton:hover {
        #         background-color: #1e293b;
        #     }
        # """)
        # logout_btn.clicked.connect(self.logout)
        # sidebar_layout.addWidget(logout_btn)
        
        sidebar.setLayout(sidebar_layout)
        
        # ==================== MAIN CONTENT ====================
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #f8fafc;")
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        topbar = QWidget()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        topbar_layout = QHBoxLayout()
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Page title
        self.page_title = QLabel("Tampilan Awal")
        self.page_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #0f172a;
        """)
        topbar_layout.addWidget(self.page_title)
        
        topbar_layout.addStretch()
        
        # Clock
        self.clock = QLabel()
        self.clock.setStyleSheet("""
            color: #475569;
            font-size: 13px;
            background-color: #f1f5f9;
            padding: 6px 14px;
            border-radius: 20px;
        """)
        self.update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        topbar_layout.addWidget(self.clock)
        
        topbar_layout.addSpacing(12)
        
        # User button
        self.user_btn = QPushButton(f"👤 {self.user['nama']}")
        self.user_btn.setCursor(Qt.PointingHandCursor)
        self.user_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #1e293b;
                border: none;
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        
        user_menu = QMenu(self)
        user_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #10b981;
                color: white;
            }
        """)
        
        profile_action = QAction("👤 Profil", self)
        profile_action.triggered.connect(self.show_profile_dialog)
        user_menu.addAction(profile_action)
        
        # change_pass_action = QAction("🔑 Ganti Password", self)
        # change_pass_action.triggered.connect(self.change_password)
        # user_menu.addAction(change_pass_action)
        
        user_menu.addSeparator()
        
        logout_action = QAction("🚪 Keluar", self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        
        self.user_btn.setMenu(user_menu)
        topbar_layout.addWidget(self.user_btn)
        
        topbar.setLayout(topbar_layout)
        content_layout.addWidget(topbar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f8fafc;")
        
        # Initialize pages
        self.pages = {
            'dashboard': DashboardPage(),
            'transaksi': TransactionPage(),
            'pelanggan': CustomerPage(),
            'stok': StockPage(),
            'laporan': ReportPage(),
        }
        
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        content_layout.addWidget(self.stacked_widget, 1)
        
        content_container.setLayout(content_layout)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_container, 1)
        
        central.setLayout(main_layout)
        
        # Status bar
        status_text = "Database Terhubung" if self.db_status else "Database Tidak Terhubung"
        self.statusBar().showMessage(f"{user['nama']} | {status_text}")
        
        # Set default page
        self.current_page = 'dashboard'
        self.show_page('dashboard')
    
    def update_clock(self):
        now = datetime.now()
        self.clock.setText(now.strftime("%H:%M:%S"))
    
    def show_page(self, page_name):
        """Menampilkan halaman yang dipilih"""
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            self.current_page = page_name
            
            # Update page title
            page_titles = {
                'dashboard': "Tampilan Awal",
                'transaksi': "Transaksi",
                'pelanggan': "Pelanggan",
                'stok': "Stok Barang",
                'laporan': "Laporan"
            }
            self.page_title.setText(page_titles.get(page_name, page_name.title()))
            
            # Update active menu style
            active_style = """
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border-radius: 10px;
                    padding: 10px 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #10b981;
                }
            """
            normal_style = """
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    border-radius: 10px;
                    padding: 10px 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1e293b;
                    color: white;
                }
            """
            
            for p, btn in self.menu_buttons.items():
                if p == page_name:
                    btn.setStyleSheet(active_style)
                else:
                    btn.setStyleSheet(normal_style)
            
            # Refresh data for pages that need it
            try:
                if page_name == 'dashboard':
                    if hasattr(self.pages['dashboard'], 'load_data'):
                        self.pages['dashboard'].load_data()
                elif page_name == 'transaksi':
                    if hasattr(self.pages['transaksi'], 'load_products'):
                        self.pages['transaksi'].load_products()
                    if hasattr(self.pages['transaksi'], 'load_customers'):
                        self.pages['transaksi'].load_customers()
                elif page_name == 'pelanggan':
                    if hasattr(self.pages['pelanggan'], 'load_customers'):
                        self.pages['pelanggan'].load_customers()
                elif page_name == 'stok':
                    if hasattr(self.pages['stok'], 'load_stock'):
                        self.pages['stok'].load_stock()
                elif page_name == 'laporan':
                    if hasattr(self.pages['laporan'], 'load_report'):
                        self.pages['laporan'].load_report()
            except Exception as e:
                print(f"Error refreshing page {page_name}: {e}")
    
    def show_profile_dialog(self):
        dialog = ProfileDialog(self.user, self)
        dialog.exec()
    
    def change_password(self):
        dialog = ChangePasswordDialog(self.user['username'], self)
        if dialog.exec():
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Pemberitahuan!")
            msg_box.setText("Password berhasil diubah!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            self.logout()
    
    def logout(self):
        if self.is_closing:
            return
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Konfirmasi")
        msg_box.setText("Apakah Anda yakin ingin keluar?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            self.is_closing = True
            self.close()
            from windows.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
    
    def closeEvent(self, event):
        if self.is_closing:
            event.accept()
            return
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Konfirmasi")
        msg_box.setText("Apakah Anda yakin ingin keluar?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            self.is_closing = True
            event.accept()
        else:
            event.ignore()