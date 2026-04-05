# windows/__init__.py
from windows.login_window import LoginWindow
from windows.main_window import MainWindow
from windows.transaction_detail_window import TransactionDetailWindow
from windows.profile_dialog import ProfileDialog
from windows.dialogs import ChangePasswordDialog, AddProductDialog, CustomerDialog

__all__ = [
    'LoginWindow', 
    'MainWindow', 
    'TransactionDetailWindow', 
    'ProfileDialog',
    'ChangePasswordDialog', 
    'AddProductDialog',
    'CustomerDialog'
]