# main.py
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtGui import QFont, QIcon
from windows.login_window import LoginWindow
from styles import STYLE
from config_manager import ConfigManager
from database_helper import DatabaseHelper
from windows.config_dialog import ConfigDialog
from config import get_db_config

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_database_connection():
    """Cek koneksi database"""
    config_manager = ConfigManager()
    
    # Test database
    db_ok, db_msg = config_manager.test_connection()
    
    if not db_ok:
        return False, db_msg
    
    # Test API
    api_ok, api_msg = config_manager.test_api_connection()
    
    if not api_ok:
        return False, api_msg
    
    return True, "Koneksi berhasil"

def main():
    app = QApplication(sys.argv)
    # Set icon
    icon_path = resource_path("favicon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(16)

    app.setFont(font)
    app.setStyle(STYLE)
    
    # Cek koneksi database
    connected, message = check_database_connection()
    
    if not connected:
        # Tampilkan dialog konfigurasi
        dialog = ConfigDialog()
        
        # Cek jika user menekan cancel
        if dialog.exec() != QDialog.Accepted:
            # Jika user cancel, tanya apakah ingin keluar
            reply = QMessageBox.question(
                None,
                "Konfirmasi",
                "Aplikasi membutuhkan konfigurasi database untuk berjalan.\n\nApakah Anda ingin keluar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                sys.exit(0)
            else:
                # Ulangi dialog
                ConfigDialog().exec()
        
        # Setelah konfigurasi, cek ulang
        connected, message = check_database_connection()
        if not connected:
            QMessageBox.critical(
                None,
                "Error",
                f"❌ Tidak dapat terhubung ke database!\n\n{message}\n\nAplikasi akan ditutup."
            )
            sys.exit(1)
    
    # Koneksi berhasil, lanjut ke login
    db_config = get_db_config()
    DatabaseHelper.API_URL = db_config['api_url']
    
    login = LoginWindow()
    login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()