# utils.py
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

def safe_float(value, default=0.0):
    """Safe conversion to float"""
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(',', '').replace('Rp', '').replace(' ', '').strip()
            if value == '':
                return default
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        return default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safe conversion to int"""
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(',', '').replace('Rp', '').replace(' ', '').strip()
            if value == '':
                return default
            return int(float(value))
        if isinstance(value, (int, float)):
            return int(value)
        return default
    except (ValueError, TypeError):
        return default

def format_rupiah(value):
    """Format angka ke Rupiah"""
    try:
        val = safe_float(value)
        return f"Rp {val:,.0f}"
    except:
        return "Rp 0"

def format_tanggal(tanggal_str=None):
    """Format tanggal ke string yang rapi"""
    if tanggal_str and tanggal_str != '-':
        try:
            if isinstance(tanggal_str, str):
                # Handle berbagai format tanggal
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]:
                    try:
                        tanggal = datetime.strptime(tanggal_str, fmt)
                        return tanggal.strftime("%d/%m/%Y %H:%M:%S")
                    except:
                        continue
        except:
            pass
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_tanggal_sekarang():
    """Get current date and time as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class EventSystem:
    """Simple event system untuk komunikasi antar halaman"""
    _instance = None
    _listeners = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}
        return cls._instance
    
    def subscribe(self, event_name, callback):
        """Subscribe to an event"""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name, callback):
        """Unsubscribe from an event"""
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)
    
    def emit(self, event_name, data=None):
        """Emit an event"""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(data)

# Buat instance global
events = EventSystem()

# utils.py - Tambahkan fungsi helper

def show_question(parent, title, message):
    """Show question dialog with Yes/No buttons"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.No)
    msg.setIcon(QMessageBox.Icon.Question)
    return msg.exec()

def show_warning(parent, title, message):
    """Show warning dialog"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    # msg.setIcon(QMessageBox.Icon.Warning)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
            border-radius: 12px;
        }
        QMessageBox QLabel {
            color: #1e293b;
            font-size: 13px;
            min-width: 300px;
            padding: 10px;
        }
        QPushButton {
            background-color: #10b981;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 24px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #059669;
        }
    """)
    return msg.exec()

def show_info(parent, title, message):
    """Show information dialog"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    # msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
            border-radius: 12px;
        }
        QMessageBox QLabel {
            color: #1e293b;
            font-size: 13px;
            min-width: 300px;
            padding: 10px;
        }
        QPushButton {
            background-color: #10b981;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 24px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #059669;
        }
    """)
    return msg.exec()