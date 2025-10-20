import sys
import os
import pypdfium2 as pdfium
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSplitter, QFileDialog, QStatusBar, QSlider, QMessageBox,
    QToolBar, QPushButton
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction, QPainter, QScreen
from PySide6.QtCore import Qt, QSize, QSettings, QUrl, QByteArray
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# --- Helper untuk menangani path saat di-bundle dengan PyInstaller ---
def resource_path(relative_path):
    """ Dapatkan path absolut ke resource, berfungsi untuk dev dan PyInstaller """
    try:
        # PyInstaller membuat folder temp dan menyimpan path di _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Icon SVG dalam format XML (Embedded) ---
# Menggunakan icon dari Feather Icons (https://feathericons.com/) - MIT License
SVG_ICONS = {
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>""",
    "print": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>""",
    "zoom-in": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
    "zoom-out": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
    "prev-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>""",
    "next-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>""",
    "save": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>"""
}

def create_svg_icon(svg_xml, color="black"):
    """Membuat QIcon dari string XML SVG."""
    # Ganti warna stroke default
    svg_xml = svg_xml.replace('stroke="currentColor"', f'stroke="{color}"')
    
    # Render SVG ke QPixmap
    renderer = QSvgRenderer(QByteArray(svg_xml.encode('utf-8')))
    pixmap = QPixmap(QSize(24, 24))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)

class ThumbnailLabel(QLabel):
    """Label kustom untuk thumbnail yang bisa diklik."""
    def __init__(self, page_num, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.setToolTip(f"Go to page {self.page_num + 1}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            ThumbnailLabel {
                border: 1px solid lightgray;
                padding: 2px;
                margin: 5px;
            }
            ThumbnailLabel:hover {
                border: 1px solid dodgerblue;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent().parent().parent().parent().parent().parent().go_to_page(self.page_num)

class MacanReader(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        
        self.pdf = None
        self.current_page = 0
        self.zoom_factor = 1.0  # 100%
        self.current_file_path = None
        
        self.settings = QSettings("MacanAngkasa", "MacanReader")

        self.init_ui()
        self.update_recent_files_menu()

        if file_to_open:
            self.open_pdf(file_to_open)

    def init_ui(self):
        self.setWindowTitle("Macan Reader")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        
        # Atur ukuran awal berdasarkan ukuran layar
        screen_size = QApplication.primaryScreen().geometry()
        self.resize(int(screen_size.width() * 0.7), int(screen_size.height() * 0.8))

        # --- Layout Utama dengan Splitter ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)
        
        # --- Panel Kiri: Thumbnails ---
        self.thumb_scroll_area = QScrollArea()
        self.thumb_scroll_area.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_layout = QVBoxLayout(self.thumb_container)
        self.thumb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.thumb_scroll_area.setWidget(self.thumb_container)
        self.thumb_scroll_area.setMinimumWidth(150)
        self.splitter.addWidget(self.thumb_scroll_area)
        
        # --- Panel Kanan: PDF View ---
        self.pdf_view_scroll_area = QScrollArea()
        self.pdf_view_scroll_area.setWidgetResizable(True)
        self.pdf_view_label = QLabel()
        self.pdf_view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_view_scroll_area.setWidget(self.pdf_view_label)
        self.splitter.addWidget(self.pdf_view_scroll_area)
        
        self.splitter.setSizes([150, 800]) # Atur ukuran awal splitter

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()
        self.update_ui_state()
        
        # Aktifkan Drag and Drop
        self.setAcceptDrops(True)

    def create_actions(self):
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"]), "&Open...", self)
        self.open_action.triggered.connect(self.open_file_dialog)
        self.open_action.setShortcut("Ctrl+O")

        self.save_as_action = QAction(create_svg_icon(SVG_ICONS["save"]), "&Save As...", self)
        self.save_as_action.triggered.connect(self.save_as_file)

        self.print_action = QAction(create_svg_icon(SVG_ICONS["print"]), "&Print...", self)
        self.print_action.triggered.connect(self.print_file)
        self.print_action.setShortcut("Ctrl+P")

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut("Ctrl+Q")
        
        self.about_action = QAction("&About Macan Reader", self)
        self.about_action.triggered.connect(self.show_about_dialog)

    def create_menus(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.print_action)
        toolbar.addAction(self.save_as_action)
        toolbar.addSeparator()

        self.prev_page_action = QAction(create_svg_icon(SVG_ICONS["prev-page"]), "Previous Page", self)
        self.prev_page_action.triggered.connect(lambda: self.go_to_page(self.current_page - 1))
        self.prev_page_action.setShortcut("Left")
        toolbar.addAction(self.prev_page_action)

        self.next_page_action = QAction(create_svg_icon(SVG_ICONS["next-page"]), "Next Page", self)
        self.next_page_action.triggered.connect(lambda: self.go_to_page(self.current_page + 1))
        self.next_page_action.setShortcut("Right")
        toolbar.addAction(self.next_page_action)
        
        toolbar.addSeparator()

        self.zoom_out_action = QAction(create_svg_icon(SVG_ICONS["zoom-out"]), "Zoom Out", self)
        self.zoom_out_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() - 10))
        self.zoom_out_action.setShortcut("Ctrl+-")
        toolbar.addAction(self.zoom_out_action)

        self.zoom_in_action = QAction(create_svg_icon(SVG_ICONS["zoom-in"]), "Zoom In", self)
        self.zoom_in_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() + 10))
        self.zoom_in_action.setShortcut("Ctrl+=")
        toolbar.addAction(self.zoom_in_action)


    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.file_info_label = QLabel("No file opened")
        self.status_bar.addWidget(self.file_info_label, 1) # Stretch factor 1

        self.page_info_label = QLabel()
        self.status_bar.addPermanentWidget(self.page_info_label)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 500) # 25% to 500%
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.valueChanged.connect(self.set_zoom)
        self.status_bar.addPermanentWidget(self.zoom_slider)

        self.zoom_label = QLabel(" 100% ")
        self.status_bar.addPermanentWidget(self.zoom_label)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.open_pdf(file_path)
            
    def open_pdf(self, file_path):
        try:
            self.pdf = pdfium.PdfDocument(file_path)
            self.current_file_path = file_path
            self.current_page = 0
            self.setWindowTitle(f"Macan Reader - {os.path.basename(file_path)}")
            self.populate_thumbnails()
            self.display_page(self.current_page)
            self.update_ui_state()
            self.add_to_recent_files(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF file: {e}")
            self.pdf = None
            self.update_ui_state()

    def populate_thumbnails(self):
        # Hapus thumbnail lama
        while self.thumb_layout.count():
            child = self.thumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.pdf:
            return

        for i in range(len(self.pdf)):
            page = self.pdf[i]
            # Render thumbnail dengan lebar tetap untuk konsistensi
            thumbnail = page.render(scale=0.15).to_pil()
            
            image = QImage(thumbnail.tobytes(), thumbnail.width, thumbnail.height, thumbnail.width * 3, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(image)
            
            thumb_label = ThumbnailLabel(i, self.thumb_container)
            thumb_label.setPixmap(pixmap)
            self.thumb_layout.addWidget(thumb_label)
            
    def display_page(self, page_num):
        if not self.pdf or not (0 <= page_num < len(self.pdf)):
            return

        self.current_page = page_num
        page = self.pdf[page_num]
        
        # Render dengan zoom factor
        pil_image = page.render(scale=self.zoom_factor).to_pil()
        
        image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(image)
        self.pdf_view_label.setPixmap(pixmap)
        
        self.update_status_bar()

    def go_to_page(self, page_num):
        if self.pdf and 0 <= page_num < len(self.pdf):
            self.display_page(page_num)
            
            # Highlight thumbnail yang aktif
            for i in range(self.thumb_layout.count()):
                widget = self.thumb_layout.itemAt(i).widget()
                if isinstance(widget, ThumbnailLabel):
                    if widget.page_num == page_num:
                        widget.setStyleSheet("border: 2px solid #0078d4; padding: 2px; margin: 5px;")
                    else:
                        widget.setStyleSheet("border: 1px solid lightgray; padding: 2px; margin: 5px;")

    def set_zoom(self, value):
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f" {value}% ")
        self.display_page(self.current_page)

    def save_as_file(self):
        if not self.pdf:
            return
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if save_path:
            try:
                # pypdfium2 mendukung penyimpanan ke path baru
                self.pdf.save(save_path)
                QMessageBox.information(self, "Success", f"File saved successfully to {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def print_file(self):
        if not self.pdf:
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter()
            painter.begin(printer)
            
            for i in range(len(self.pdf)):
                page = self.pdf[i]
                # Render dengan resolusi printer
                img = page.render(scale=printer.resolution()/72.0).to_pil() # 72 DPI is standard
                q_img = QImage(img.tobytes(), img.width, img.height, QImage.Format.Format_RGB888).rgbSwapped()
                
                # Gambar pixmap ke halaman printer
                painter.drawPixmap(0, 0, QPixmap.fromImage(q_img))
                
                # Pindah ke halaman baru jika bukan halaman terakhir
                if i < len(self.pdf) - 1:
                    printer.newPage()
                    
            painter.end()

    def show_about_dialog(self):
        about_text = """
        <h2>Macan Reader</h2>
        <p>A professional PDF reader built with PySide6 and PyPDFium2.</p>
        <p>Fast, efficient, and reliable.</p>
        <br>
        <p>© 2025 - Danx Exodus - Macan Angkasa</p>
        """
        QMessageBox.about(self, "About Macan Reader", about_text)

    def add_to_recent_files(self, file_path):
        recent_files = self.settings.value("recentFiles", [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        # Batasi jumlah recent files
        del recent_files[10:]
        self.settings.setValue("recentFiles", recent_files)
        self.update_recent_files_menu()
        
    def update_recent_files_menu(self):
        self.recent_files_menu.clear()
        recent_files = self.settings.value("recentFiles", [])
        
        for file_path in recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_recent_file(self):
        action = self.sender()
        if action:
            file_path = action.data()
            if os.path.exists(file_path):
                self.open_pdf(file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"The file '{file_path}' could not be found.")
                # Hapus dari recent list
                recent_files = self.settings.value("recentFiles", [])
                if file_path in recent_files:
                    recent_files.remove(file_path)
                    self.settings.setValue("recentFiles", recent_files)
                    self.update_recent_files_menu()

    def update_ui_state(self):
        is_pdf_loaded = self.pdf is not None
        self.save_as_action.setEnabled(is_pdf_loaded)
        self.print_action.setEnabled(is_pdf_loaded)
        self.zoom_in_action.setEnabled(is_pdf_loaded)
        self.zoom_out_action.setEnabled(is_pdf_loaded)
        self.zoom_slider.setEnabled(is_pdf_loaded)
        
        if is_pdf_loaded:
            self.prev_page_action.setEnabled(self.current_page > 0)
            self.next_page_action.setEnabled(self.current_page < len(self.pdf) - 1)
        else:
            self.prev_page_action.setEnabled(False)
            self.next_page_action.setEnabled(False)

    def update_status_bar(self):
        if self.pdf:
            self.file_info_label.setText(os.path.basename(self.current_file_path))
            self.page_info_label.setText(f" Page: {self.current_page + 1} of {len(self.pdf)} ")
        else:
            self.file_info_label.setText("No file opened")
            self.page_info_label.setText("")

    # --- Event Handlers untuk Drag and Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Cek apakah file adalah PDF
            url = event.mimeData().urls()[0]
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        file_path = url.toLocalFile()
        self.open_pdf(file_path)

    def closeEvent(self, event):
        # Opsi untuk menyimpan setting saat keluar
        self.settings.sync()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_to_open = None
    # Cek jika ada argumen file dari command line
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path) and path.lower().endswith('.pdf'):
            file_to_open = path
            
    window = MacanReader(file_to_open)
    window.show()
    sys.exit(app.exec())