# styles.py
STYLE = """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "Segoe UI", Arial;
    color: #1f2937;
}

QPushButton {
    background-color: #10b981;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #059669;
}

QPushButton#danger {
    background-color: #ef4444;
}

QPushButton#danger:hover {
    background-color: #dc2626;
}

QPushButton#secondary {
    background-color: #3b82f6;
}

QPushButton#secondary:hover {
    background-color: #2563eb;
}

QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #10b981;
}

QTableWidget {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: #e5e7eb;
    alternate-background-color: #f9fafb;
}
QHeaderView::section {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 12px 8px;
    border: none;
    border-bottom: 2px solid #10b981;
    font-weight: 600;
    font-size: 13px;
}
QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #f1f5f9;
}
QTableWidget::item:selected {
    background-color: #10b981;
    color: white;
}
QTableWidget::item:hover {
    background-color: #f1f5f9;
}

QLabel {
    color: #1f2937;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #10b981;
}

QStatusBar {
    background-color: #f1f5f9;
    color: #64748b;
}

QListWidget {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: white;
}

QListWidget::item {
    padding: 8px;
}

QListWidget::item:selected {
    background-color: #10b981;
    color: white;
}

QComboBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px 10px;
    background-color: white;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

QTabBar::tab {
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #10b981;
    color: white;
}

# QTableWidget {
#     background-color: #ffffff;
#     border: 1px solid #e5e7eb;
#     border-radius: 16px;
#     gridline-color: #f3f4f6;
#     selection-background-color: #10b981;
#     selection-color: #ffffff;
#     font-size: 13px;
# }

# QHeaderView::section {
#     background-color: #f9fafb;
#     color: #111827;
#     padding: 14px 12px;
#     border: none;
#     border-bottom: 2px solid #10b981;
#     font-weight: 600;
#     font-size: 13px;
# }

# QTableWidget::item {
#     padding: 12px 8px;
#     border-bottom: 1px solid #f3f4f6;
# }

# QTableWidget::item:hover {
#     background-color: #f9fafb;
# }

# QTableWidget::item:selected {
#     background-color: #10b981;
#     color: #ffffff;
# }

QTableWidget::item:selected:hover {
    background-color: #059669;
}

QScrollBar:vertical {
    background-color: #f3f4f6;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #d1d5db;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9ca3af;
}

QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #e2e8f0;
}

QProgressBar::chunk {
    border-radius: 4px;
    background-color: #10b981;
}

QMessageBox {
    background-color: #ffffff;
    border-radius: 12px;
}

QMessageBox QLabel {
    color: #1e293b;
    font-size: 13px;
    margin: 10px;
}

QMessageBox QPushButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #e2e8f0;
}

QMessageBox QPushButton[text="OK"] {
    background-color: #10b981;
    color: white;
}

QMessageBox QPushButton[text="OK"]:hover {
    background-color: #059669;
}

QMessageBox QPushButton[text="Yes"] {
    background-color: #10b981;
    color: white;
}

QMessageBox QPushButton[text="Yes"]:hover {
    background-color: #059669;
}

QMessageBox QPushButton[text="No"] {
    background-color: #ef4444;
    color: white;
}

QMessageBox QPushButton[text="No"]:hover {
    background-color: #dc2626;
}

QMessageBox QPushButton[text="Cancel"] {
    background-color: #f1f5f9;
    color: #475569;
}

QMessageBox QPushButton[text="Cancel"]:hover {
    background-color: #e2e8f0;
}

/* Style untuk QDialogButtonBox */
QDialogButtonBox {
    button-layout: 0;
}

QDialogButtonBox QPushButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-width: 80px;
}

QDialogButtonBox QPushButton:hover {
    background-color: #e2e8f0;
}

QDialogButtonBox QPushButton[text="OK"] {
    background-color: #10b981;
    color: white;
}

QDialogButtonBox QPushButton[text="Cancel"] {
    background-color: #f1f5f9;
    color: #475569;
}

/* Style untuk QInputDialog */
QInputDialog {
    background-color: #ffffff;
    border-radius: 12px;
}

QInputDialog QLabel {
    color: #1e293b;
}

QInputDialog QLineEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: white;
}

QInputDialog QPushButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border-radius: 6px;
    padding: 6px 16px;
}

QInputDialog QPushButton[text="OK"] {
    background-color: #10b981;
    color: white;
}

QInputDialog QPushButton[text="Cancel"] {
    background-color: #f1f5f9;
    color: #475569;
}
"""

STYLE_REFRESH_BUTTON = """
QPushButton {
    background-color: #008bfc;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #041578;
}
QPushButton:pressed {
    background-color: #a5a7b0;
}
"""

STYLE_ADD_BUTTON = """
QPushButton {
    background-color: #2ff761;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #09820b;
}
QPushButton:pressed {
    background-color: #a5a7b0;
}
"""

STYLE_DANGER_BUTTON = """
QPushButton {
    background-color: #FF4848;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #FF0000;
}
QPushButton:pressed {
    background-color: #a5a7b0;
}
"""

STYLE_WARNING_BUTTON = """
QPushButton {
    background-color: #FFFA6D;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #FFF700;
}
QPushButton:pressed {
    background-color: #a5a7b0;
}
"""