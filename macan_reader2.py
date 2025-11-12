import sys
import os
import pypdfium2 as pdfium
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSplitter, QFileDialog, QStatusBar, QSlider, QMessageBox,
    QToolBar, QPushButton, QLineEdit, QCheckBox
)
# DITAMBAHKAN: Import tambahan untuk search, pan, dll.
from PySide6.QtGui import (
    QPixmap, QImage, QIcon, QAction, QPainter, QScreen, QColor
)
from PySide6.QtCore import (
    Qt, QSize, QSettings, QUrl, QByteArray, Signal, QRectF
)
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
SVG_ICONS = {
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>""",
    "print": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>""",
    "zoom-in": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
    "zoom-out": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
    "prev-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>""",
    "next-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>""",
    "save": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>""",
    # DITAMBAHKAN: Ikon untuk search dan pan
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",
    "hand": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"></path><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"></path><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"></path><path d="M18 8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h2"></path></svg>"""
}

def create_svg_icon(svg_xml, color="black"):
    """Membuat QIcon dari string XML SVG."""
    svg_xml = svg_xml.replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(QByteArray(svg_xml.encode('utf-8')))
    pixmap = QPixmap(QSize(24, 24))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

class ThumbnailLabel(QLabel):
    """Label kustom untuk thumbnail yang bisa diklik."""
    page_clicked = Signal(int)

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
            self.page_clicked.emit(self.page_num)

# DITAMBAHKAN: Kelas label kustom untuk panning
class PdfViewLabel(QLabel):
    """Label kustom untuk tampilan PDF yang mendukung panning."""
    def __init__(self, scroll_area, parent=None):
        super().__init__(parent)
        self.scroll_area = scroll_area
        self.pan_mode = False
        self.panning = False
        self.last_pan_pos = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def setPanMode(self, enabled):
        """Mengaktifkan atau menonaktifkan mode pan."""
        self.pan_mode = enabled
        self.setCursor(Qt.CursorShape.OpenHandCursor if enabled else Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        if self.pan_mode and event.button() == Qt.MouseButton.LeftButton:
            self.last_pan_pos = event.globalPosition().toPoint()
            self.panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning and self.last_pan_pos:
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self.last_pan_pos
            self.last_pan_pos = current_pos
            
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.panning and event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            self.last_pan_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            super().mouseReleaseEvent(event)

class MacanReader(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        
        self.pdf = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self.current_file_path = None
        
        # DITAMBAHKAN: Properti untuk pencarian
        self.search_results = []
        self.current_search_index = -1
        
        self.settings = QSettings("MacanAngkasa", "MacanReader")

        self.init_ui()
        self.update_recent_files_menu()

        if file_to_open:
            self.open_pdf(file_to_open)

    def init_ui(self):
        self.setWindowTitle("Macan Reader")
        
        screen_size = QApplication.primaryScreen().geometry()
        self.resize(int(screen_size.width() * 0.7), int(screen_size.height() * 0.8))

        # DITAMBAHKAN: Widget utama untuk menampung search bar dan splitter
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # DITAMBAHKAN: Buat dan tambahkan search widget (awalnya tersembunyi)
        self.search_widget = self.create_search_widget()
        main_layout.addWidget(self.search_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter) # Tambahkan splitter ke layout utama
        
        self.setCentralWidget(main_widget) # Set widget utama sebagai central widget
        
        self.thumb_scroll_area = QScrollArea()
        self.thumb_scroll_area.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_layout = QVBoxLayout(self.thumb_container)
        self.thumb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.thumb_scroll_area.setWidget(self.thumb_container)
        self.thumb_scroll_area.setMinimumWidth(150)
        self.splitter.addWidget(self.thumb_scroll_area)
        
        self.pdf_view_scroll_area = QScrollArea()
        self.pdf_view_scroll_area.setWidgetResizable(True)
        
        # DIUBAH: Gunakan PdfViewLabel kustom
        self.pdf_view_label = PdfViewLabel(self.pdf_view_scroll_area)
        self.pdf_view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_view_scroll_area.setWidget(self.pdf_view_label)
        self.splitter.addWidget(self.pdf_view_scroll_area)
        
        self.splitter.setSizes([150, 800])

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()
        self.update_ui_state()
        
        self.setAcceptDrops(True)

    # DITAMBAHKAN: Metode untuk membuat search widget
    def create_search_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(QLabel("Find:"))
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.find_next)
        self.search_input.textChanged.connect(self.clear_search) # Hapus hasil jika teks berubah
        layout.addWidget(self.search_input)
        
        find_next_btn = QPushButton("Next")
        find_next_btn.clicked.connect(self.find_next)
        layout.addWidget(find_next_btn)
        
        find_prev_btn = QPushButton("Previous")
        find_prev_btn.clicked.connect(self.find_prev)
        layout.addWidget(find_prev_btn)
        
        self.match_case_check = QCheckBox("Match Case")
        layout.addWidget(self.match_case_check)
        
        layout.addStretch()
        
        close_btn = QPushButton(create_svg_icon(
            """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>"""
        ), "")
        close_btn.setFlat(True)
        close_btn.setFixedSize(24, 24)
        close_btn.setToolTip("Close Search Bar")
        close_btn.clicked.connect(self.toggle_search_bar)
        layout.addWidget(close_btn)
        
        widget.setVisible(False) # Sembunyikan secara default
        widget.setStyleSheet("background-color: #f0f0f0;") # Beri sedikit warna latar
        return widget

    def create_actions(self):
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"]), "&Open...", self)
        self.open_action.triggered.connect(self.open_file_dialog)
        self.open_action.setShortcut("Ctrl+O")

        self.save_as_action = QAction(create_svg_icon(SVG_ICONS["save"]), "&Save As...", self)
        self.save_as_action.triggered.connect(self.save_as_file)

        self.print_action = QAction(create_svg_icon(SVG_ICONS["print"]), "&Print...", self)
        self.print_action.triggered.connect(self.print_file)
        self.print_action.setShortcut("Ctrl+P")

        # DITAMBAHKAN: Aksi Close
        self.close_action = QAction("&Close", self)
        self.close_action.triggered.connect(self.close_pdf)
        self.close_action.setShortcut("Ctrl+W")
        
        # DITAMBAHKAN: Aksi Clear Recent
        self.clear_recent_action = QAction("Clear Recent Files", self)
        self.clear_recent_action.triggered.connect(self.clear_recent_files)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut("Ctrl+Q")
        
        # DITAMBAHKAN: Aksi Find
        self.find_action = QAction(create_svg_icon(SVG_ICONS["search"]), "&Find...", self)
        self.find_action.triggered.connect(self.toggle_search_bar)
        self.find_action.setShortcut("Ctrl+F")

        # DITAMBAHKAN: Aksi Toggle Thumbnail
        self.toggle_thumbnails_action = QAction("Show &Thumbnail Pane", self)
        self.toggle_thumbnails_action.setCheckable(True)
        self.toggle_thumbnails_action.setChecked(True) # Tampil secara default
        self.toggle_thumbnails_action.triggered.connect(self.toggle_thumbnail_pane)

        self.about_action = QAction("&About Macan Reader", self)
        self.about_action.triggered.connect(self.show_about_dialog)

    def create_menus(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        
        # DITAMBAHKAN: Aksi Close
        file_menu.addAction(self.close_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # DITAMBAHKAN: Menu Edit
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.find_action)
        
        # DITAMBAHKAN: Menu Window
        window_menu = menu_bar.addMenu("&Window")
        window_menu.addAction(self.toggle_thumbnails_action)
        
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
        
        toolbar.addSeparator()
        
        # DITAMBAHKAN: Aksi Pan
        self.pan_action = QAction(create_svg_icon(SVG_ICONS["hand"]), "Pan Tool (Drag to move page)", self)
        self.pan_action.setCheckable(True)
        self.pan_action.triggered.connect(self.toggle_pan_mode)
        toolbar.addAction(self.pan_action)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.file_info_label = QLabel("No file opened")
        self.status_bar.addWidget(self.file_info_label, 1)

        self.page_info_label = QLabel()
        self.status_bar.addPermanentWidget(self.page_info_label)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.valueChanged.connect(self.set_zoom)
        self.status_bar.addPermanentWidget(self.zoom_slider)

        self.zoom_label = QLabel(" 100% ")
        self.status_bar.addPermanentWidget(self.zoom_label)

    # DITAMBAHKAN: Slot untuk aksi Pan
    def toggle_pan_mode(self, checked):
        self.pdf_view_label.setPanMode(checked)

    # DITAMBAHKAN: Slot untuk aksi Toggle Thumbnail
    def toggle_thumbnail_pane(self, checked):
        self.thumb_scroll_area.setVisible(checked)

    # DITAMBAHKAN: Slot untuk aksi Toggle Search Bar
    def toggle_search_bar(self):
        is_visible = self.search_widget.isVisible()
        self.search_widget.setVisible(not is_visible)
        if not is_visible:
            self.search_input.setFocus()
        else:
            self.clear_search() # Hapus pencarian saat menutup bar

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.open_pdf(file_path)
            
    def open_pdf(self, file_path):
        try:
            # Tutup file lama jika ada
            if self.pdf:
                self.close_pdf()
                
            self.pdf = pdfium.PdfDocument(file_path)
            self.current_file_path = file_path
            self.current_page = 0
            self.setWindowTitle(f"Macan Reader - {os.path.basename(file_path)}")
            self.populate_thumbnails()
            self.go_to_page(self.current_page)
            self.update_ui_state()
            self.add_to_recent_files(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF file: {e}")
            self.pdf = None
            self.update_ui_state()

    # DITAMBAHKAN: Metode untuk menutup file PDF
    def close_pdf(self):
        if not self.pdf:
            return
            
        self.pdf.close()
        self.pdf = None
        self.current_file_path = None
        self.current_page = 0
        
        self.setWindowTitle("Macan Reader")
        self.pdf_view_label.clear()
        self.clear_search() # Hapus hasil pencarian
        self.populate_thumbnails() # Kosongkan thumbnails
        self.update_ui_state()
        self.update_status_bar()

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
            # Render thumbnail dengan skala kecil
            thumbnail = page.render(scale=0.15).to_pil()
            
            image = QImage(thumbnail.tobytes(), thumbnail.width, thumbnail.height, thumbnail.width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            
            thumb_label = ThumbnailLabel(i, self.thumb_container)
            thumb_label.setPixmap(pixmap)
            
            thumb_label.page_clicked.connect(self.go_to_page)
            
            self.thumb_layout.addWidget(thumb_label)
            
    def display_page(self, page_num):
        if not self.pdf or not (0 <= page_num < len(self.pdf)):
            return

        self.current_page = page_num
        page = self.pdf[page_num]
        
        pil_image = page.render(scale=self.zoom_factor).to_pil()
        
        image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        
        # DITAMBAHKAN: Gambar highlight pencarian di atas pixmap
        if self.search_results:
            self.draw_search_highlights(page, pixmap)
        
        self.pdf_view_label.setPixmap(pixmap)
        
        self.update_status_bar()
        self.update_ui_state() # Panggil ini untuk update tombol prev/next

    def go_to_page(self, page_num):
        if self.pdf and 0 <= page_num < len(self.pdf):
            self.display_page(page_num)
            
            # Update highlight pada thumbnail
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

    # --- Bagian Logika Pencarian ---

    def clear_search(self):
        """Membersihkan hasil pencarian dan me-render ulang halaman."""
        self.search_results = []
        self.current_search_index = -1
        if self.pdf:
            # Panggil display_page untuk menggambar ulang tanpa highlight
            self.display_page(self.current_page)
        self.status_bar.clearMessage()

    def run_search(self):
        """Menjalankan pencarian baru di seluruh dokumen."""
        text = self.search_input.text()
        if not text or not self.pdf:
            self.clear_search()
            return
            
        self.search_results = []
        self.current_search_index = -1
        
        flags = pdfium.PdfTextSearch.MATCHCASE if self.match_case_check.isChecked() else 0
        
        for i in range(len(self.pdf)):
            page = self.pdf[i]
            searcher = page.search_text(text, flags=flags)
            rects = searcher.get_rects()
            for rect in rects:
                self.search_results.append((i, rect)) # Simpan (nomor halaman, rect)
                
        self.status_bar.showMessage(f"Found {len(self.search_results)} result(s).")
        
    def find_next(self):
        """Pergi ke hasil pencarian berikutnya."""
        text = self.search_input.text()
        if not text: return
        
        # Jalankan pencarian jika belum ada hasil
        if not self.search_results:
            self.run_search()
            
        if not self.search_results:
            return # Tidak ada hasil

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.highlight_search_result()

    def find_prev(self):
        """Pergi ke hasil pencarian sebelumnya."""
        text = self.search_input.text()
        if not text: return

        if not self.search_results:
            self.run_search()

        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1 + len(self.search_results)) % len(self.search_results)
        self.highlight_search_result()

    def highlight_search_result(self):
        """Pindah ke halaman dan gambar ulang dengan highlight aktif."""
        if not self.search_results:
            return
            
        page_num, rect = self.search_results[self.current_search_index]
        
        if page_num != self.current_page:
            self.go_to_page(page_num)
        else:
            # Jika sudah di halaman yang benar, panggil display_page lagi
            # untuk memperbarui highlight (mana yang aktif)
            self.display_page(page_num)
            
        # TODO: Scroll ke area highlight jika di luar pandangan

    def convert_pdf_rect_to_pixmap(self, page, rect):
        """Konversi koordinat rect PDF ke koordinat QPixmap."""
        l, b, r, t = rect # (left, bottom, right, top) - y-axis dari bawah
        page_width, page_height = page.get_size() # Ukuran dalam poin PDF
        
        # Koordinat pixmap (y-axis dari atas)
        pixmap_x = l * self.zoom_factor
        pixmap_y = (page_height - t) * self.zoom_factor
        pixmap_w = (r - l) * self.zoom_factor
        pixmap_h = (t - b) * self.zoom_factor
        
        return QRectF(pixmap_x, pixmap_y, pixmap_w, pixmap_h)

    def draw_search_highlights(self, page, pixmap):
        """Menggambar semua highlight untuk halaman saat ini di atas pixmap."""
        painter = QPainter(pixmap)
        
        highlight_color = QColor(255, 255, 0, 100) # Kuning transparan
        active_highlight_color = QColor(255, 165, 0, 150) # Oranye transparan
        
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i, (p_num, rect) in enumerate(self.search_results):
            if p_num == self.current_page:
                q_rect = self.convert_pdf_rect_to_pixmap(page, rect)
                
                if i == self.current_search_index:
                    painter.setBrush(active_highlight_color)
                else:
                    painter.setBrush(highlight_color)
                    
                painter.drawRect(q_rect)
        
        painter.end()

    # --- Akhir Bagian Logika Pencarian ---

    def save_as_file(self):
        if not self.pdf:
            return
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if save_path:
            try:
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
            
            page_range = printer.pageRange()
            from_page = printer.fromPage()
            to_page = printer.toPage()
            
            pages_to_print = list(range(len(self.pdf)))

            # Handle page range selection
            if page_range == QPrinter.PageRange.PageRange:
                pages_to_print = list(range(from_page - 1, min(to_page, len(self.pdf))))
            elif page_range == QPrinter.PageRange.CurrentPage:
                pages_to_print = [self.current_page]

            for i, page_idx in enumerate(pages_to_print):
                if page_idx >= len(self.pdf):
                    continue
                    
                page = self.pdf[page_idx]
                
                # Render dengan resolusi printer
                # (printer.resolution() / 72.0) adalah skala untuk DPI printer
                scale = printer.resolution() / 72.0
                img = page.render(scale=scale).to_pil()
                
                q_img = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                
                # Dapatkan ukuran halaman printer dan gambar
                page_rect = printer.pageRect(QPrinter.Unit.Pixel)
                img_pixmap = QPixmap.fromImage(q_img)
                
                # Skalakan gambar agar pas di halaman (aspect ratio tetap)
                scaled_pixmap = img_pixmap.scaled(page_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # Tengahkan gambar di halaman
                x = (page_rect.width() - scaled_pixmap.width()) / 2
                y = (page_rect.height() - scaled_pixmap.height()) / 2
                
                painter.drawPixmap(int(x), int(y), scaled_pixmap)
                
                if i < len(pages_to_print) - 1:
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
        del recent_files[10:]
        self.settings.setValue("recentFiles", recent_files)
        self.update_recent_files_menu()
        
    def update_recent_files_menu(self):
        self.recent_files_menu.clear()
        recent_files = self.settings.value("recentFiles", [])
        
        if recent_files:
            for file_path in recent_files:
                action = QAction(os.path.basename(file_path), self)
                action.setData(file_path)
                action.triggered.connect(self.open_recent_file)
                self.recent_files_menu.addAction(action)
            # DITAMBAHKAN: Pemisah dan aksi Clear
            self.recent_files_menu.addSeparator()
            self.recent_files_menu.addAction(self.clear_recent_action)
        else:
            # DITAMBAHKAN: Placeholder jika kosong
            no_recent_action = QAction("No Recent Files", self)
            no_recent_action.setEnabled(False)
            self.recent_files_menu.addAction(no_recent_action)

    # DITAMBAHKAN: Metode untuk membersihkan recent files
    def clear_recent_files(self):
        self.settings.setValue("recentFiles", [])
        self.update_recent_files_menu()

    def open_recent_file(self):
        action = self.sender()
        if action:
            file_path = action.data()
            if os.path.exists(file_path):
                self.open_pdf(file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"The file '{file_path}' could not be found.")
                recent_files = self.settings.value("recentFiles", [])
                if file_path in recent_files:
                    recent_files.remove(file_path)
                    self.settings.setValue("recentFiles", recent_files)
                    self.update_recent_files_menu()

    def update_ui_state(self):
        is_pdf_loaded = self.pdf is not None
        
        # Aksi file
        self.save_as_action.setEnabled(is_pdf_loaded)
        self.print_action.setEnabled(is_pdf_loaded)
        self.close_action.setEnabled(is_pdf_loaded)
        
        # Aksi edit & tools
        self.find_action.setEnabled(is_pdf_loaded)
        self.pan_action.setEnabled(is_pdf_loaded)
        if not is_pdf_loaded and self.pan_action.isChecked():
            self.pan_action.setChecked(False)
            self.toggle_pan_mode(False)
        
        # Aksi zoom
        self.zoom_in_action.setEnabled(is_pdf_loaded)
        self.zoom_out_action.setEnabled(is_pdf_loaded)
        self.zoom_slider.setEnabled(is_pdf_loaded)
        
        # Aksi navigasi
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        file_path = url.toLocalFile()
        self.open_pdf(file_path)

    def closeEvent(self, event):
        # Pastikan file PDF ditutup dengan benar
        if self.pdf:
            self.close_pdf()
        self.settings.sync()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_to_open = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path) and path.lower().endswith('.pdf'):
            file_to_open = path
            
    window = MacanReader(file_to_open)
    window.show()
    sys.exit(app.exec())