# printer.py
from datetime import datetime
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog, QPrinterInfo
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFileDialog, QMessageBox, QScrollArea, QWidget, QInputDialog
from PySide6.QtGui import QPainter, QFont, QPageSize, QPageLayout, QPen, QPixmap, QPainter as QPainterWidget
from PySide6.QtCore import Qt, QMarginsF, QRectF
from config import COMPANY_DATA
from utils import safe_float
import traceback
class QuickReceiptPrinter:    
    @staticmethod
    def print_receipt(transaction_data, details):
        try:
            printer = QPrinter()

            # ✅ Set ukuran A4 (Qt6 style)
            printer.setPageSize(QPageSize(QPageSize.A4))

            # ✅ Set orientasi (Qt6)
            printer.setPageOrientation(QPageLayout.Portrait)

            painter = QPainter()

            if not painter.begin(printer):
                raise Exception("Printer tidak bisa digunakan")

            # ✅ Pakai viewport (PALING AMAN)
            page_rect = painter.viewport()

            x = 20
            y = 20
            w = page_rect.width() - 40
            line_height = 20

            left_width = w * 0.5
            right_width = w * 0.5

            left_x = x
            right_x = x + left_width

            # Font
            font_title = QFont("Arial", 14, QFont.Bold)
            font_header = QFont("Arial", 11, QFont.Bold)
            font_normal = QFont("Arial", 10)
            font_small = QFont("Arial", 9)

            # ================= HEADER =================
            # HEADER BOX
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(x, y, w, 60)

            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(QRectF(x, y + 5, w, 20), Qt.AlignCenter, COMPANY_DATA['nama'])

            painter.setFont(QFont("Arial", 10))
            painter.drawText(QRectF(x, y + 25, w, 15), Qt.AlignCenter, COMPANY_DATA['jenis_usaha'])
            painter.drawText(QRectF(x, y + 40, w, 15), Qt.AlignCenter, f"Telp: {COMPANY_DATA['telp']}")
            painter.drawText(QRectF(x, y + 55, w, 15), Qt.AlignCenter, f"{COMPANY_DATA['alamat']}")

            y += 70

            # =======SECTION INVOICE
            section_height = 80

            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(x, y, w, section_height)

            # garis tengah
            painter.drawLine(x + w/2, y, x + w/2, y + section_height)

            painter.setFont(font_header)

            painter.drawText(QRectF(left_x + 5, y + 5, left_width, 20), Qt.AlignLeft, "INVOICE")
            painter.drawText(QRectF(right_x + 5, y + 5, right_width, 20), Qt.AlignLeft, "PELANGGAN")

            painter.setFont(font_normal)

            # kiri
            painter.drawText(QRectF(left_x + 5, y + 25, left_width, 15), Qt.AlignLeft,
                            f"No      : {transaction_data.get('no_invoice', '-')}")
            painter.drawText(QRectF(left_x + 5, y + 40, left_width, 15), Qt.AlignLeft,
                            f"Tanggal : {transaction_data.get('tanggal_transaksi', '-')[:19]}")
            painter.drawText(QRectF(left_x + 5, y + 55, left_width, 15), Qt.AlignLeft,
                            f"Kasir   : {transaction_data.get('kasir', 'Admin')}")

            # kanan
            painter.drawText(QRectF(right_x + 5, y + 25, right_width, 15), Qt.AlignLeft,
                            f"Nama : {transaction_data.get('pelanggan', '-')}")
            painter.drawText(QRectF(right_x + 5, y + 40, right_width, 15), Qt.AlignLeft,
                            f"Kode : {transaction_data.get('pelanggan_kode', '-')}")
            painter.drawText(QRectF(right_x + 5, y + 55, right_width, 15), Qt.AlignLeft,
                            f"Telp : {transaction_data.get('pelanggan_telp', '-')}")
            
            # ============== Section Item

            y += section_height + 10

            row_height = 25

            # HEADER TABEL
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(x, y, w, row_height)

            col_brand = x
            col_qty = x + w * 0.30
            col_kg = x + w * 0.40
            col_harga_kg = x + w * 0.55
            col_harga_karung = x + w * 0.70
            col_sub = x + w * 0.85

            # Border header
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(x, y, w, row_height)

            # Garis vertikal
            for col in [col_qty, col_kg, col_harga_kg, col_harga_karung, col_sub]:
                painter.drawLine(col, y, col, y + row_height)

            painter.setFont(font_header)

            painter.drawText(QRectF(col_brand + 5, y, 100, row_height), Qt.AlignVCenter, "Item")
            painter.drawText(QRectF(col_qty, y, 60, row_height), Qt.AlignCenter, "Qty/Krg")
            painter.drawText(QRectF(col_kg, y, 60, row_height), Qt.AlignCenter, "Kg")
            painter.drawText(QRectF(col_harga_kg, y, 90, row_height), Qt.AlignCenter, "Harga/Kg")
            painter.drawText(QRectF(col_harga_karung, y, 100, row_height), Qt.AlignCenter, "Harga/Krg")
            painter.drawText(QRectF(col_sub, y, 100, row_height), Qt.AlignCenter, "Subtotal")

            y += row_height

            painter.setFont(font_normal)
            painter.setPen(QPen(Qt.black, 1))

            for item in details:
                qty = safe_float(item.get('jumlah_karung', 0))
                kg = safe_float(item.get('jumlah_kg', 0))
                subtotal = safe_float(item.get('subtotal', 0))

                harga_per_kg = subtotal / kg if kg else 0
                harga_per_karung = subtotal / qty if qty else 0

                painter.drawRect(x, y, w, row_height)

                for col in [col_qty, col_kg, col_harga_kg, col_harga_karung, col_sub]:
                    painter.drawLine(col, y, col, y + row_height)

                painter.drawText(QRectF(col_brand + 5, y, 140, row_height),
                                Qt.AlignVCenter, item.get('brand', '-'))

                painter.drawText(QRectF(col_qty, y, 60, row_height),
                                Qt.AlignCenter, f"{qty:.1f}")

                painter.drawText(QRectF(col_kg, y, 60, row_height),
                                Qt.AlignCenter, f"{kg:.0f}")

                painter.drawText(QRectF(col_harga_kg, y, 90, row_height),
                                Qt.AlignRight, f"{harga_per_kg:,.0f}")

                painter.drawText(QRectF(col_harga_karung, y, 100, row_height),
                                Qt.AlignRight, f"{harga_per_karung:,.0f}")

                painter.drawText(QRectF(col_sub, y, 100, row_height),
                                Qt.AlignRight, f"{subtotal:,.0f}")

                y += row_height
            
            # ================= SUMMARY =================

            y += 5

            left_x = x
            right_x = x + w * 0.55

            left_width = w * 0.45
            right_width = w * 0.45

            # ===========SUM KANAN
            painter.setFont(font_normal)

            total_karung = sum(safe_float(i.get('jumlah_karung', 0)) for i in details)
            total_kg = total_karung * 50

            total = safe_float(transaction_data.get('total_bayar', 0))
            bayar = safe_float(transaction_data.get('uang_bayar', 0))
            kembali = safe_float(transaction_data.get('uang_kembali', 0))

            line_h = 20

            summary_lines = [
                ("Total Karung", f"{total_karung:.1f} karung"),
                ("Total KG", f"{total_kg:.0f} KG"),
                ("Total Bayar", f"Rp {total:,.0f}"),
                ("Bayar", f"Rp {bayar:,.0f}"),
                ("Kembali", f"Rp {kembali:,.0f}")
            ]

            for label, value in summary_lines:
                painter.drawText(QRectF(right_x, y, right_width/2, line_h),
                                Qt.AlignLeft | Qt.AlignVCenter, label)

                # bold untuk total bayar
                if label == "Total Bayar":
                    painter.setFont(font_header)
                else:
                    painter.setFont(font_normal)

                painter.drawText(QRectF(right_x + right_width/2, y, right_width/2, line_h),
                                Qt.AlignRight | Qt.AlignVCenter, value)

                # ===== TAMBAHKAN GARIS DI BAWAH TOTAL BAYAR =====
                if label == "Total Bayar":
                    line_y = y + line_h

                    painter.setPen(QPen(Qt.black, 2))  # garis tebal
                    painter.drawLine(
                        right_x,
                        line_y,
                        right_x + right_width,
                        line_y
                    )

                    painter.setPen(QPen(Qt.black, 1))  # balikin normal

                y += line_h
            
            ttd_y = y + 30

            left_x = x
            right_x = x + w * 0.55

            ttd_width = w * 0.35

            painter.setFont(font_normal)

            # ====== HITUNG CENTER ======
            left_center = left_x + (ttd_width / 2)
            right_center = right_x + (ttd_width / 2)

            # ====== LABEL ======
            painter.drawText(QRectF(left_x, ttd_y, ttd_width, 20),
                            Qt.AlignCenter, "Admin")

            painter.drawText(QRectF(right_x, ttd_y, ttd_width, 20),
                            Qt.AlignCenter, "Penerima")

            # ====== GARIS ======
            line_y = ttd_y + 60
            line_width = 120  # panjang garis tanda tangan

            # kiri (admin)
            painter.drawLine(
                left_center - line_width / 2,
                line_y,
                left_center + line_width / 2,
                line_y
            )

            # kanan (penerima)
            painter.drawLine(
                right_center - line_width / 2,
                line_y,
                right_center + line_width / 2,
                line_y
            )

            # ====== NAMA (TITIK-TITIK) ======
            painter.drawText(QRectF(left_center - 80, line_y + 5, 160, 20),
                            Qt.AlignCenter, "(.........................)")

            painter.drawText(QRectF(right_center - 80, line_y + 5, 160, 20),
                            Qt.AlignCenter, "(.........................)")

            #=============== Foooooterrrr
            
            footer_y = line_y + 40

            painter.setFont(font_small)

            # Garis atas footer
            painter.setPen(QPen(Qt.black, 1))
            painter.drawLine(x, footer_y, x + w, footer_y)

            footer_y += 10

            # Text tengah
            painter.drawText(QRectF(x, footer_y, w, 20),
                            Qt.AlignCenter,
                            "Terima kasih atas kepercayaan Anda")

            footer_y += 15

            painter.drawText(QRectF(x, footer_y, w, 20),
                            Qt.AlignCenter,
                            "Barang yang sudah dibeli tidak dapat dikembalikan")

            footer_y += 15

            # Waktu cetak
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            painter.drawText(QRectF(x, footer_y, w, 20),
                            Qt.AlignCenter,
                            f"Dicetak: {now}")

            painter.end()

        except Exception as e:
            print(f"Error printing: {e}")
            traceback.print_exc()


class ReceiptPrinterWithCopies:
    """Cetak nota dengan pilihan jumlah rangkap"""
    
    @staticmethod
    def print_receipt(transaction_data, details, copies=1):
        """Cetak nota dengan jumlah rangkap yang ditentukan"""
        try:
            copies, ok = QInputDialog.getInt(
                None, 
                "Cetak Nota", 
                "Jumlah rangkap yang ingin dicetak:", 
                copies, 1, 5, 1
            )
            
            if not ok:
                return
            
            for copy_num in range(copies):
                QuickReceiptPrinter.print_receipt(transaction_data, details)
                
        except Exception as e:
            print(f"Error printing: {e}")
            QMessageBox.warning(None, "Error", f"Gagal mencetak nota: {e}")

class PrintDialog(QDialog):
    """Dialog cetak lengkap dengan preview menggunakan QuickReceiptPrinter"""
    
    def __init__(self, transaction_data, details, parent=None):
        super().__init__(parent)
        self.transaction_data = transaction_data
        self.details = details
        self.setWindowTitle("Cetak Nota")
        self.setFixedSize(900, 750)
        self.setModal(True)
        
        # Printer yang dipilih
        self.printer = QPrinter()
        self.printer.setPageSize(QPageSize(QPageSize.A4))
        self.printer.setPageOrientation(QPageLayout.Portrait)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # ========== TOOLBAR ATAS ==========
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        # Pilih Printer
        printer_label = QLabel("Printer:")
        printer_label.setStyleSheet("font-weight: 500;")
        toolbar.addWidget(printer_label)
        
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumWidth(250)
        self.printer_combo.currentIndexChanged.connect(self.on_printer_changed)
        toolbar.addWidget(self.printer_combo)
        
        toolbar.addStretch()
        
        # Tombol Cetak
        print_btn = QPushButton("🖨️ Cetak")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        print_btn.clicked.connect(self.print_document)
        toolbar.addWidget(print_btn)
        
        # Tombol Export PDF
        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        pdf_btn.clicked.connect(self.export_pdf)
        toolbar.addWidget(pdf_btn)
        
        # Tombol Tutup
        close_btn = QPushButton("✕ Tutup")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        close_btn.clicked.connect(self.close)
        toolbar.addWidget(close_btn)
        
        layout.addLayout(toolbar)
        
        # ========== PREVIEW AREA ==========
        preview_label = QLabel("📄 Preview Nota")
        preview_label.setStyleSheet("font-weight: 600; font-size: 14px; margin-top: 10px;")
        layout.addWidget(preview_label)
        
        # Scroll area untuk preview
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
            }
        """)
        
        # Widget untuk preview (akan digambar menggunakan painter)
        self.preview_widget = QWidget()
        self.preview_widget.setMinimumSize(600, 800)
        self.preview_widget.setStyleSheet("background-color: white;")
        
        self.preview_scroll.setWidget(self.preview_widget)
        layout.addWidget(self.preview_scroll, 1)
        
        self.setLayout(layout)
        
        # Load daftar printer
        self.load_printers()
        
        # Update preview
        self.update_preview()
    
    def load_printers(self):
        """Load daftar printer yang tersedia menggunakan QPrinterInfo"""
        self.printer_combo.clear()
        
        # Dapatkan daftar printer menggunakan QPrinterInfo
        printers = QPrinterInfo.availablePrinters()
        
        # Tambahkan opsi "Default Printer"
        default_printer = QPrinterInfo.defaultPrinter()
        if default_printer:
            self.printer_combo.addItem(f"📄 Default Printer ({default_printer.printerName()})", default_printer)
        else:
            self.printer_combo.addItem("📄 Default Printer", None)
        
        # Tambahkan daftar printer lainnya
        for printer in printers:
            # Hindari duplikasi dengan default printer
            if default_printer and printer.printerName() == default_printer.printerName():
                continue
            self.printer_combo.addItem(f"🖨️ {printer.printerName()}", printer)
        
        # Jika tidak ada printer, tambahkan opsi "Tidak ada printer"
        if self.printer_combo.count() == 0:
            self.printer_combo.addItem("⚠️ Tidak ada printer terdeteksi", None)
        
        # Pilih printer default
        if self.printer_combo.count() > 0:
            self.printer_combo.setCurrentIndex(0)
    
    def on_printer_changed(self, index):
        """Saat printer dipilih"""
        printer_info = self.printer_combo.currentData()
        if printer_info:
            self.printer = QPrinter(printer_info)
        else:
            self.printer = QPrinter()
        
        # Set ukuran kertas
        self.printer.setPageSize(QPageSize(QPageSize.A4))
        self.printer.setPageOrientation(QPageLayout.Portrait)
        
        # Update preview
        self.update_preview()
    
    def update_preview(self):
        """Update preview nota dengan menggunakan QuickReceiptPrinter"""
        try:
            # Buat painter untuk preview widget
            painter = QPainter()
            
            # Set printer untuk preview (menggunakan QPrinter yang sudah diset)
            # Tapi kita akan menggambar langsung ke widget untuk preview
            # Buat printer sementara dengan format PDF untuk preview
            preview_printer = QPrinter()
            preview_printer.setOutputFormat(QPrinter.PdfFormat)
            preview_printer.setPageSize(QPageSize(QPageSize.A4))
            preview_printer.setPageOrientation(QPageLayout.Portrait)
            
            # Gunakan QuickReceiptPrinter untuk menggambar ke printer
            # Tapi kita perlu menangkap output ke widget
            # Untuk preview, kita akan menggunakan metode yang sama dengan QuickReceiptPrinter
            # tetapi menggambar ke widget
            
            # Buat pixmap untuk preview
            pixmap = QPixmap(self.preview_widget.size())
            pixmap.fill(Qt.white)
            
            widget_painter = QPainterWidget(pixmap)
            
            # Salin metode _draw_receipt dari QuickReceiptPrinter
            self._draw_preview(widget_painter, self.transaction_data, self.details)
            widget_painter.end()
            
            # Tampilkan pixmap di preview widget
            # Hapus widget lama
            for child in self.preview_widget.findChildren(QLabel):
                child.deleteLater()
            
            preview_label = QLabel(self.preview_widget)
            preview_label.setPixmap(pixmap)
            preview_label.resize(pixmap.size())
            preview_label.show()
            
        except Exception as e:
            print(f"Error update preview: {e}")
    
    def _draw_preview(self, painter, transaction_data, details):
        """Draw receipt untuk preview (salinan dari QuickReceiptPrinter)"""
        # Ambil ukuran widget
        x = 10
        y = 10
        w = self.preview_widget.width() - 20
        line_height = 20

        left_width = w * 0.5
        right_width = w * 0.5

        left_x = x
        right_x = x + left_width

        # Font
        font_title = QFont("Arial", 14, QFont.Bold)
        font_header = QFont("Arial", 11, QFont.Bold)
        font_normal = QFont("Arial", 10)
        font_small = QFont("Arial", 9)

        # ================= HEADER =================
        # HEADER BOX
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(x, y, w, 80)

        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRectF(x, y + 5, w, 20), Qt.AlignCenter, COMPANY_DATA['nama'])

        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRectF(x, y + 25, w, 15), Qt.AlignCenter, COMPANY_DATA['jenis_usaha'])
        painter.drawText(QRectF(x, y + 40, w, 15), Qt.AlignCenter, f"Telp: {COMPANY_DATA['telp']}")
        painter.drawText(QRectF(x, y + 55, w, 15), Qt.AlignCenter, f"{COMPANY_DATA['alamat']}")

        y += 85

        # =======SECTION INVOICE
        section_height = 80

        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(x, y, w, section_height)

        # garis tengah
        painter.drawLine(x + w/2, y, x + w/2, y + section_height)

        painter.setFont(font_header)

        painter.drawText(QRectF(left_x + 5, y + 5, left_width, 20), Qt.AlignLeft, "INVOICE")
        painter.drawText(QRectF(right_x + 5, y + 5, right_width, 20), Qt.AlignLeft, "PELANGGAN")

        painter.setFont(font_normal)

        # kiri
        label_w = 80  # lebar label
        value_w = left_width - label_w - 10

        # NO
        painter.drawText(QRectF(left_x + 5, y + 25, label_w, 15),
                        Qt.AlignLeft, "No")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 25, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 25, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('no_invoice', '-'))


        # TANGGAL
        painter.drawText(QRectF(left_x + 5, y + 40, label_w, 15),
                        Qt.AlignLeft, "Tanggal")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 40, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 40, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('tanggal_transaksi', '-')[:19])


        # KASIR
        painter.drawText(QRectF(left_x + 5, y + 55, label_w, 15),
                        Qt.AlignLeft, "Kasir")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 55, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 55, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('kasir', 'Admin'))

        # kanan
        label_w = 70
        value_w = right_width - label_w - 10

        # NAMA
        painter.drawText(QRectF(right_x + 5, y + 25, label_w, 15),
                        Qt.AlignLeft, "Nama")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 25, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 25, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan', '-'))


        # KODE
        painter.drawText(QRectF(right_x + 5, y + 40, label_w, 15),
                        Qt.AlignLeft, "Kode")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 40, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 40, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan_kode', '-'))


        # TELP
        painter.drawText(QRectF(right_x + 5, y + 55, label_w, 15),
                        Qt.AlignLeft, "Telp")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 55, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 55, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan_telp', '-'))
        
        # ============== Section Item

        y += section_height + 10

        row_height = 25

        col_ratios = [0.30, 0.10, 0.10, 0.15, 0.15, 0.20]

        # Hitung posisi kolom
        col_positions = [x]
        for ratio in col_ratios:
            col_positions.append(col_positions[-1] + w * ratio)

        # ================= HEADER =================
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(x, y, w, row_height)

        # Garis vertikal header
        for col in col_positions[1:-1]:
            painter.drawLine(col, y, col, y + row_height)

        headers = ["Item", "Qty/Krg", "Kg", "Harga/Kg", "Harga/Krg", "Subtotal"]

        painter.setFont(font_header)

        for i, text in enumerate(headers):
            col_x = col_positions[i]
            col_w = col_positions[i+1] - col_positions[i]

            painter.drawText(QRectF(col_x, y, col_w, row_height),
                            Qt.AlignCenter, text)

        y += row_height

        # ================= ISI =================
        painter.setFont(font_normal)
        painter.setPen(QPen(Qt.black, 1))

        total_karung = 0
        total_kg = 0

        for item in details:
            qty = safe_float(item.get('jumlah_karung', 0))
            kg = safe_float(item.get('jumlah_kg', 0))
            subtotal = safe_float(item.get('subtotal', 0))

            harga_per_kg = subtotal / kg if kg else 0
            harga_per_karung = subtotal / qty if qty else 0

            total_karung += qty
            total_kg += kg

            # Border row
            painter.drawRect(x, y, w, row_height)

            # Garis vertikal
            for col in col_positions[1:-1]:
                painter.drawLine(col, y, col, y + row_height)

            values = [
                item.get('brand', '-'),
                f"{qty:.1f}",
                f"{kg:.0f}",
                f"{harga_per_kg:,.0f}",
                f"{harga_per_karung:,.0f}",
                f"{subtotal:,.0f}"
            ]

            aligns = [
                Qt.AlignLeft,
                Qt.AlignCenter,
                Qt.AlignCenter,
                Qt.AlignRight,
                Qt.AlignRight,
                Qt.AlignRight
            ]

            for i, val in enumerate(values):
                col_x = col_positions[i]
                col_w = col_positions[i+1] - col_positions[i]

                # padding kiri kanan biar rapi
                painter.drawText(QRectF(col_x + 5, y, col_w - 10, row_height),
                                aligns[i] | Qt.AlignVCenter, val)

            y += row_height
        
        # ================= SUMMARY + TTD + FOOTER =================

        # ===== GRID 2 KOLOM =====
        col_split = 0.5

        left_x = x
        right_x = x + w * col_split

        left_width = w * col_split
        right_width = w * (1 - col_split)

        y += int(w * 0.03)

        # ================= SUMMARY (KANAN) =================
        painter.setFont(font_normal)

        total_karung = sum(safe_float(i.get('jumlah_karung', 0)) for i in details)
        total_kg = sum(safe_float(i.get('jumlah_kg', 0)) for i in details)

        total = safe_float(transaction_data.get('total_bayar', 0))
        bayar = safe_float(transaction_data.get('uang_bayar', 0))
        kembali = safe_float(transaction_data.get('uang_kembali', 0))

        summary_lines = [
            ("Total Karung", f"{total_karung:.1f} karung"),
            ("Total KG", f"{total_kg:.0f} KG"),
            ("Total Bayar", f"Rp {total:,.0f}"),
            ("Bayar", f"Rp {bayar:,.0f}"),
            ("Kembali", f"Rp {kembali:,.0f}")
        ]

        line_h = int(w * 0.04)

        label_w = right_width * 0.5
        value_w = right_width * 0.5

        start_y = y  # simpan untuk sejajarin TTD

        for label, value in summary_lines:
            painter.setFont(font_normal)

            painter.drawText(QRectF(right_x, y, label_w, line_h),
                            Qt.AlignLeft | Qt.AlignVCenter, label)

            if label == "Total Bayar":
                painter.setFont(font_header)

            painter.drawText(QRectF(right_x + label_w, y, value_w, line_h),
                            Qt.AlignRight | Qt.AlignVCenter, value)

            # ===== GARIS FULL WIDTH =====
            if label == "Total Bayar":
                line_y = y + line_h

                painter.setPen(QPen(Qt.black, 2))
                painter.drawLine(
                    int(right_x),
                    int(line_y),
                    int(right_x + right_width),
                    int(line_y)
                )
                painter.setPen(QPen(Qt.black, 1))

            y += line_h

        # ================= TTD (KIRI & KANAN) =================

        ttd_y = y + int(w * 0.05)  # sejajarin dengan summary atas

        ttd_width = left_width
        line_width = ttd_width * 0.6

        left_center = left_x + (ttd_width / 2)
        right_center = right_x + (ttd_width / 2)

        painter.setFont(font_normal)

        # Label
        painter.drawText(QRectF(left_x, ttd_y, ttd_width, 20),
                        Qt.AlignCenter, "Admin")

        painter.drawText(QRectF(right_x, ttd_y, ttd_width, 20),
                        Qt.AlignCenter, "Penerima")

        # Garis tanda tangan
        line_y = ttd_y + int(w * 0.08)

        painter.drawLine(
            left_center - line_width / 2,
            line_y,
            left_center + line_width / 2,
            line_y
        )

        painter.drawLine(
            right_center - line_width / 2,
            line_y,
            right_center + line_width / 2,
            line_y
        )

        # Nama (titik-titik)
        text_w = line_width

        painter.drawText(QRectF(left_center - text_w/2, line_y + 5, text_w, 20),
                        Qt.AlignCenter, "(.........................)")

        painter.drawText(QRectF(right_center - text_w/2, line_y + 5, text_w, 20),
                        Qt.AlignCenter, "(.........................)")

        # ================= FOOTER =================

        footer_y = line_y + int(w * 0.08)

        painter.setFont(font_small)

        # garis atas footer
        painter.drawLine(x, footer_y, x + w, footer_y)

        footer_y += int(w * 0.02)

        # text
        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        "Terima kasih atas kepercayaan Anda")

        footer_y += int(w * 0.03)

        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        "Barang yang sudah dibeli tidak dapat dikembalikan")

        footer_y += int(w * 0.03)

        # waktu cetak
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        f"Dicetak: {now}")
    
    def print_document(self):
        """Cetak dengan dialog printer (pakai printer yang dipilih)"""
        try:
            dialog = QPrintDialog(self.printer, self)

            if dialog.exec() == QDialog.Accepted:
                painter = QPainter()

                if painter.begin(self.printer):
                    self._draw_to_printer(painter, self.transaction_data, self.details)
                    painter.end()

                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Pemberitahuan!")
                    msg_box.setText(f"Nota berhasil dicetak!")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.close()
                else:
                    raise Exception("Gagal mengakses printer")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mencetak: {e}")
    
    def export_pdf(self):
        """Export ke PDF menggunakan QuickReceiptPrinter"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan PDF",
                f"nota_{self.transaction_data.get('no_invoice', 'invoice')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Buat printer dengan output PDF
                pdf_printer = QPrinter()
                pdf_printer.setOutputFormat(QPrinter.PdfFormat)
                pdf_printer.setOutputFileName(filename)
                pdf_printer.setPageSize(QPageSize(QPageSize.A4))
                pdf_printer.setPageOrientation(QPageLayout.Portrait)
                
                painter = QPainter()
                if painter.begin(pdf_printer):
                    # Salin metode dari QuickReceiptPrinter
                    # Untuk PDF, kita gunakan pendekatan yang sama
                    self._draw_to_printer(painter, self.transaction_data, self.details)
                    painter.end()
                    
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Pemberitahuan!")
                    msg_box.setText(f"PDF berhasil dicetak {filename}!")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.close()
                else:
                    raise Exception("Gagal membuat PDF")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal export PDF: {e}")
    
    def _draw_to_printer(self, painter, transaction_data, details):
        page_rect = painter.device().pageRect(QPrinter.DevicePixel)

        BASE_WIDTH = 800
        BASE_HEIGHT = int(800 * 1.414)

        scale_x = page_rect.width() / BASE_WIDTH
        scale_y = page_rect.height() / BASE_HEIGHT

        painter.scale(scale_x, scale_y)

        # sekarang gambar pakai base size
        x = 20
        y = 20
        w = BASE_WIDTH - 40
        # line_height = 20

        def i(v): return int(v)

        left_width = w * 0.5
        right_width = w * 0.5

        left_x = x
        right_x = x + left_width

        # Font
        font_title = QFont("Arial", 14, QFont.Bold)
        font_header = QFont("Arial", 11, QFont.Bold)
        font_normal = QFont("Arial", 10)
        font_small = QFont("Arial", 9)

        # ================= HEADER =================
        # HEADER BOX
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(x, y, w, 80)

        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRectF(x, y + 5, w, 20), Qt.AlignCenter, COMPANY_DATA['nama'])

        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRectF(x, y + 25, w, 15), Qt.AlignCenter, COMPANY_DATA['jenis_usaha'])
        painter.drawText(QRectF(x, y + 40, w, 15), Qt.AlignCenter, f"Telp: {COMPANY_DATA['telp']}")
        painter.drawText(QRectF(x, y + 55, w, 15), Qt.AlignCenter, f"{COMPANY_DATA['alamat']}")

        y += 85

        # =======SECTION INVOICE
        section_height = 80

        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(x, y, w, section_height)

        # garis tengah
        painter.drawLine(x + w/2, y, x + w/2, y + section_height)

        painter.setFont(font_header)

        painter.drawText(QRectF(left_x + 5, y + 5, left_width, 20), Qt.AlignLeft, "INVOICE")
        painter.drawText(QRectF(right_x + 5, y + 5, right_width, 20), Qt.AlignLeft, "PELANGGAN")

        painter.setFont(font_normal)

        # kiri
        label_w = 80  # lebar label
        value_w = left_width - label_w - 10

        # NO
        painter.drawText(QRectF(left_x + 5, y + 25, label_w, 15),
                        Qt.AlignLeft, "No")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 25, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 25, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('no_invoice', '-'))


        # TANGGAL
        painter.drawText(QRectF(left_x + 5, y + 40, label_w, 15),
                        Qt.AlignLeft, "Tanggal")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 40, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 40, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('tanggal_transaksi', '-')[:19])


        # KASIR
        painter.drawText(QRectF(left_x + 5, y + 55, label_w, 15),
                        Qt.AlignLeft, "Kasir")

        painter.drawText(QRectF(left_x + 5 + label_w, y + 55, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(left_x + 5 + label_w + 10, y + 55, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('kasir', 'Admin'))

        # kanan
        label_w = 70
        value_w = right_width - label_w - 10

        # NAMA
        painter.drawText(QRectF(right_x + 5, y + 25, label_w, 15),
                        Qt.AlignLeft, "Nama")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 25, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 25, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan', '-'))


        # KODE
        painter.drawText(QRectF(right_x + 5, y + 40, label_w, 15),
                        Qt.AlignLeft, "Kode")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 40, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 40, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan_kode', '-'))


        # TELP
        painter.drawText(QRectF(right_x + 5, y + 55, label_w, 15),
                        Qt.AlignLeft, "Telp")

        painter.drawText(QRectF(right_x + 5 + label_w, y + 55, 10, 15),
                        Qt.AlignCenter, ":")

        painter.drawText(QRectF(right_x + 5 + label_w + 10, y + 55, value_w, 15),
                        Qt.AlignLeft, transaction_data.get('pelanggan_telp', '-'))
        
        # ============== Section Item

        y += section_height + 10

        row_height = 25

        # ================= KOLOM RATIO =================
        col_ratios = [0.30, 0.10, 0.10, 0.15, 0.15, 0.20]

        # Hitung posisi kolom
        col_positions = [x]
        for ratio in col_ratios:
            col_positions.append(col_positions[-1] + w * ratio)

        # ================= HEADER =================
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(x, y, w, row_height)

        # Garis vertikal header
        for col in col_positions[1:-1]:
            painter.drawLine(col, y, col, y + row_height)

        headers = ["Item", "Qty/Krg", "Kg", "Harga/Kg", "Harga/Krg", "Subtotal"]

        painter.setFont(font_header)

        for i, text in enumerate(headers):
            col_x = col_positions[i]
            col_w = col_positions[i+1] - col_positions[i]

            painter.drawText(QRectF(col_x, y, col_w, row_height),
                            Qt.AlignCenter, text)

        y += row_height

        # ================= ISI =================
        painter.setFont(font_normal)
        painter.setPen(QPen(Qt.black, 1))

        total_karung = 0
        total_kg = 0

        for item in details:
            qty = safe_float(item.get('jumlah_karung', 0))
            kg = safe_float(item.get('jumlah_kg', 0))
            subtotal = safe_float(item.get('subtotal', 0))

            harga_per_kg = subtotal / kg if kg else 0
            harga_per_karung = subtotal / qty if qty else 0

            total_karung += qty
            total_kg += kg

            # Border row
            painter.drawRect(x, y, w, row_height)

            # Garis vertikal
            for col in col_positions[1:-1]:
                painter.drawLine(col, y, col, y + row_height)

            values = [
                item.get('brand', '-'),
                f"{qty:.1f}",
                f"{kg:.0f}",
                f"{harga_per_kg:,.0f}",
                f"{harga_per_karung:,.0f}",
                f"{subtotal:,.0f}"
            ]

            aligns = [
                Qt.AlignLeft,
                Qt.AlignCenter,
                Qt.AlignCenter,
                Qt.AlignRight,
                Qt.AlignRight,
                Qt.AlignRight
            ]

            for i, val in enumerate(values):
                col_x = col_positions[i]
                col_w = col_positions[i+1] - col_positions[i]

                # padding kiri kanan biar rapi
                painter.drawText(QRectF(col_x + 5, y, col_w - 10, row_height),
                                aligns[i] | Qt.AlignVCenter, val)

            y += row_height
        
        MAX_CONTENT_Y = BASE_HEIGHT * 0.70
        
        # ================= SUMMARY + TTD + FOOTER =================
        # ===== GRID 2 KOLOM =====
        col_split = 0.5

        left_x = x
        right_x = x + w * col_split

        left_width = w * col_split
        right_width = w * (1 - col_split)

        y += int(BASE_HEIGHT * 0.01)

        if y > MAX_CONTENT_Y:
            y = MAX_CONTENT_Y

        # ================= SUMMARY (KANAN) =================
        painter.setFont(font_normal)

        total_karung = sum(safe_float(i.get('jumlah_karung', 0)) for i in details)
        total_kg = sum(safe_float(i.get('jumlah_kg', 0)) for i in details)

        total = safe_float(transaction_data.get('total_bayar', 0))
        bayar = safe_float(transaction_data.get('uang_bayar', 0))
        kembali = safe_float(transaction_data.get('uang_kembali', 0))

        summary_lines = [
            ("Total Karung", f"{total_karung:.1f} karung"),
            ("Total KG", f"{total_kg:.0f} KG"),
            ("Total Bayar", f"Rp {total:,.0f}"),
            ("Bayar", f"Rp {bayar:,.0f}"),
            ("Kembali", f"Rp {kembali:,.0f}")
        ]

        line_h = int(BASE_HEIGHT * 0.02)

        label_w = right_width * 0.5
        value_w = right_width * 0.5

        start_y = y  # simpan untuk sejajarin TTD

        for label, value in summary_lines:
            painter.setFont(font_normal)

            painter.drawText(QRectF(right_x, y, label_w, line_h),
                            Qt.AlignLeft | Qt.AlignVCenter, label)

            if label == "Total Bayar":
                painter.setFont(font_header)

            painter.drawText(QRectF(right_x + label_w, y, value_w, line_h),
                            Qt.AlignRight | Qt.AlignVCenter, value)

            # ===== GARIS FULL WIDTH =====
            if label == "Total Bayar":
                line_y = y + line_h

                painter.setPen(QPen(Qt.black, 2))
                painter.drawLine(
                    int(right_x),
                    int(line_y),
                    int(right_x + right_width),
                    int(line_y)
                )
                painter.setPen(QPen(Qt.black, 1))

            y += line_h

        # ================= TTD (KIRI & KANAN) =================

        ttd_y = y + int(BASE_HEIGHT * 0.02)  # sejajarin dengan summary atas

        ttd_width = left_width * 0.8
        line_width = ttd_width * 0.6

        left_center = left_x + left_width / 2
        right_center = right_x + right_width / 2

        painter.setFont(font_normal)

        # Label
        painter.drawText(QRectF(left_center - ttd_width/2, ttd_y, ttd_width, 20),
                        Qt.AlignCenter, "Admin")

        painter.drawText(QRectF(right_center - ttd_width/2, ttd_y, ttd_width, 20),
                        Qt.AlignCenter, "Penerima")

        # Garis tanda tangan
        line_y = ttd_y + int(BASE_HEIGHT * 0.06)

        painter.drawLine(
            int(left_center - line_width / 2),
            int(line_y),
            int(left_center + line_width / 2),
            int(line_y)
        )

        # kanan (penerima)
        painter.drawLine(
            int(right_center - line_width / 2),
            int(line_y),
            int(right_center + line_width / 2),
            int(line_y)
        )

        # Nama (titik-titik)
        text_w = line_width

        painter.drawText(QRectF(left_center - text_w/2, line_y + 5, text_w, 20),
                        Qt.AlignCenter, "(.........................)")

        painter.drawText(QRectF(right_center - text_w/2, line_y + 5, text_w, 20),
                        Qt.AlignCenter, "(.........................)")

        # ================= FOOTER =================

        footer_y = line_y + int(BASE_HEIGHT * 0.03)

        painter.setFont(font_small)

        # garis atas footer
        painter.drawLine(x, footer_y, x + w, footer_y)

        footer_y += int(BASE_HEIGHT * 0.015)

        # text
        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        "Terima kasih atas kepercayaan Anda")

        footer_y += int(BASE_HEIGHT * 0.015)

        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        "Barang yang sudah dibeli tidak dapat dikembalikan")

        footer_y += int(BASE_HEIGHT * 0.015)

        # waktu cetak
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        painter.drawText(QRectF(x, footer_y, w, 20),
                        Qt.AlignCenter,
                        f"Dicetak: {now}")