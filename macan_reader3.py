import sys
import os
import pypdfium2 as pdfium
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSplitter, QFileDialog, QStatusBar, QSlider, QMessageBox,
    QToolBar, QPushButton, QLineEdit, QCheckBox, 
    #QActionGroup # DITAMBAHKAN: Untuk grup aksi tema
)
from PySide6.QtGui import (
    QPixmap, QImage, QIcon, QAction, QPainter, QScreen, QColor,
    QActionGroup # DUPLIKAT, tapi tidak masalah
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
    # DITAMBAHKAN: Ikon untuk reset zoom (menggunakan 'target')
    "zoom-reset": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>""",
    "prev-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>""",
    "next-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>""",
    "save": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",
    "hand": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"></path><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"></path><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"></path><path d="M18 8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h2"></path></svg>"""
}

# DITAMBAHKAN: Kamus untuk warna ikon tema
THEME_ICON_COLORS = {
    "light": "black",
    "dark": "#E0E0E0",
    "dark-blue": "#E0E0E0",
    "neon-blue": "#E0E0E0",
    "soft-pink": "#333333"
}

# DITAMBAHKAN: Kamus untuk QSS Tema
THEME_STYLESHEETS = {
    "light": """
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
        }
        QMainWindow, QToolBar, QStatusBar, QMenu, QMenuBar {
            background-color: #F0F0F0;
            color: #000000;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #0078D4;
            color: #FFFFFF;
        }
        QScrollArea {
            background-color: #E0E0E0;
            border: 1px solid #C0C0C0;
        }
        QPushButton {
            background-color: #E1E1E1;
            border: 1px solid #C0C0C0;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #E5E5E5;
        }
        QPushButton:pressed {
            background-color: #D0D0D0;
        }
        QLineEdit {
            background-color: #FFFFFF;
            border: 1px solid #C0C0C0;
        }
        QSlider::groove:horizontal {
            background: #C0C0C0;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #0078D4;
            width: 18px;
        }
        QSplitter::handle {
            background-color: #C0C0C0;
        }
        QWidget#searchWidget {
            background-color: #F0F0F0;
        }
        QWidget#thumbnailContainer {
            background-color: #E0E0E0;
        }
        ThumbnailLabel {
            border: 1px solid lightgray;
            padding: 2px;
            margin: 5px;
        }
        ThumbnailLabel:hover {
            border: 1px solid dodgerblue;
        }
    """,
    "dark": """
        QWidget {
            background-color: #3C3C3C;
            color: #E0E0E0;
        }
        QMainWindow, QToolBar, QStatusBar, QMenu, QMenuBar {
            background-color: #2D2D2D;
            color: #E0E0E0;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #0078D4;
            color: #FFFFFF;
        }
        QScrollArea {
            background-color: #333333;
            border: 1px solid #4A4A4A;
        }
        QPushButton {
            background-color: #4A4A4A;
            border: 1px solid #5A5A5A;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #5A5A5A;
        }
        QPushButton:pressed {
            background-color: #444444;
        }
        QLineEdit {
            background-color: #333333;
            border: 1px solid #5A5A5A;
        }
        QSlider::groove:horizontal {
            background: #4A4A4A;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #0078D4;
            width: 18px;
        }
        QSplitter::handle {
            background-color: #4A4A4A;
        }
        QWidget#searchWidget {
            background-color: #2D2D2D;
        }
        QWidget#thumbnailContainer {
            background-color: #333333;
        }
        ThumbnailLabel {
            border: 1px solid #5A5A5A;
            padding: 2px;
            margin: 5px;
        }
        ThumbnailLabel:hover {
            border: 1px solid #0078D4;
        }
    """,
    "dark-blue": """
        QWidget {
            background-color: #2D3A4F;
            color: #E0E0E0;
        }
        QMainWindow, QToolBar, QStatusBar, QMenu, QMenuBar {
            background-color: #222B3A;
            color: #E0E0E0;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #4A90E2;
            color: #FFFFFF;
        }
        QScrollArea {
            background-color: #283344;
            border: 1px solid #3A4A63;
        }
        QPushButton {
            background-color: #3A4A63;
            border: 1px solid #4A5B79;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #4A5B79;
        }
        QPushButton:pressed {
            background-color: #33425A;
        }
        QLineEdit {
            background-color: #283344;
            border: 1px solid #4A5B79;
        }
        QSlider::groove:horizontal {
            background: #3A4A63;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #4A90E2;
            width: 18px;
        }
        QSplitter::handle {
            background-color: #3A4A63;
        }
        QWidget#searchWidget {
            background-color: #222B3A;
        }
        QWidget#thumbnailContainer {
            background-color: #283344;
        }
        ThumbnailLabel {
            border: 1px solid #3A4A63;
            padding: 2px;
            margin: 5px;
        }
        ThumbnailLabel:hover {
            border: 1px solid #4A90E2;
        }
    """,
    "neon-blue": """
        QWidget {
            background-color: #0A0A1A;
            color: #00FFD1;
        }
        QMainWindow, QToolBar, QStatusBar, QMenu, QMenuBar {
            background-color: #0F0F2A;
            color: #00FFD1;
            border: 1px solid #00FFD1;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #00FFD1;
            color: #000000;
        }
        QScrollArea {
            background-color: #050510;
            border: 1px solid #00FFD1;
        }
        QPushButton {
            background-color: #1A1A3A;
            border: 1px solid #00FFD1;
            color: #00FFD1;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #2A2A4A;
        }
        QPushButton:pressed {
            background-color: #11112A;
        }
        QLineEdit {
            background-color: #050510;
            border: 1px solid #00FFD1;
            color: #00FFD1;
        }
        QSlider::groove:horizontal {
            background: #1A1A3A;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #00FFD1;
            width: 18px;
        }
        QSplitter::handle {
            background-color: #1A1A3A;
            border: 1px solid #00FFD1;
        }
        QWidget#searchWidget {
            background-color: #0F0F2A;
        }
        QWidget#thumbnailContainer {
            background-color: #050510;
        }
        ThumbnailLabel {
            border: 1px solid #00FFD1;
            padding: 2px;
            margin: 5px;
        }
        ThumbnailLabel:hover {
            border: 2px solid #00FFD1;
        }
    """,
    "soft-pink": """
        QWidget {
            background-color: #FFF0F5;
            color: #5D4037;
        }
        QMainWindow, QToolBar, QStatusBar, QMenu, QMenuBar {
            background-color: #FFDDEE;
            color: #5D4037;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #FF80AB;
            color: #FFFFFF;
        }
        QScrollArea {
            background-color: #FFF5F9;
            border: 1px solid #FFC0CB;
        }
        QPushButton {
            background-color: #FFC0CB;
            border: 1px solid #FF80AB;
            color: #5D4037;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #FFB0C1;
        }
        QPushButton:pressed {
            background-color: #FFA0B1;
        }
        QLineEdit {
            background-color: #FFF5F9;
            border: 1px solid #FFC0CB;
            color: #5D4037;
        }
        QSlider::groove:horizontal {
            background: #FFC0CB;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #FF80AB;
            width: 18px;
        }
        QSplitter::handle {
            background-color: #FFC0CB;
        }
        QWidget#searchWidget {
            background-color: #FFDDEE;
        }
        QWidget#thumbnailContainer {
            background-color: #FFF5F9;
        }
        ThumbnailLabel {
            border: 1px solid #FFC0CB;
            padding: 2px;
            margin: 5px;
        }
        ThumbnailLabel:hover {
            border: 1px solid #FF80AB;
        }
    """
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
        # DIUBAH: Stylesheet dihapus dari sini dan dipindahkan ke QSS tema
        # self.setStyleSheet("""...""")

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
        
        self.search_results = []
        self.current_search_index = -1
        
        self.settings = QSettings("MacanAngkasa", "MacanReader")

        # DITAMBAHKAN: Grup aksi untuk tema
        self.themes_action_group = QActionGroup(self)
        self.themes_action_group.setExclusive(True)

        self.init_ui()
        self.update_recent_files_menu()
        
        # DITAMBAHKAN: Muat pengaturan (termasuk tema) saat startup
        self.load_settings()

        if file_to_open:
            self.open_pdf(file_to_open)

    def init_ui(self):
        self.setWindowTitle("Macan Reader")
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        screen_size = QApplication.primaryScreen().geometry()
        self.resize(int(screen_size.width() * 0.7), int(screen_size.height() * 0.8))

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.search_widget = self.create_search_widget()
        main_layout.addWidget(self.search_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        self.setCentralWidget(main_widget)
        
        self.thumb_scroll_area = QScrollArea()
        self.thumb_scroll_area.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_container.setObjectName("thumbnailContainer") # DITAMBAHKAN: Object name untuk styling
        self.thumb_layout = QVBoxLayout(self.thumb_container)
        self.thumb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.thumb_scroll_area.setWidget(self.thumb_container)
        self.thumb_scroll_area.setMinimumWidth(150)
        self.splitter.addWidget(self.thumb_scroll_area)
        
        self.pdf_view_scroll_area = QScrollArea()
        self.pdf_view_scroll_area.setWidgetResizable(True)
        
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

    def create_search_widget(self):
        widget = QWidget()
        widget.setObjectName("searchWidget") # DITAMBAHKAN: Object name untuk styling
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(QLabel("Find:"))
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.find_next)
        self.search_input.textChanged.connect(self.clear_search)
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
        
        self.close_search_btn = QPushButton("") # DIUBAH: Ikon akan di-set di update_icons
        self.close_search_btn.setFlat(True)
        self.close_search_btn.setFixedSize(24, 24)
        self.close_search_btn.setToolTip("Close Search Bar")
        self.close_search_btn.clicked.connect(self.toggle_search_bar)
        layout.addWidget(self.close_search_btn)
        
        widget.setVisible(False)
        # DIUBAH: Stylesheet dihapus dari sini
        return widget

    def create_actions(self):
        # DIUBAH: Ikon di-set dengan warna default 'black', akan di-update oleh set_theme
        default_icon_color = THEME_ICON_COLORS["light"]
        
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"], default_icon_color), "&Open...", self)
        self.open_action.triggered.connect(self.open_file_dialog)
        self.open_action.setShortcut("Ctrl+O")

        self.save_as_action = QAction(create_svg_icon(SVG_ICONS["save"], default_icon_color), "&Save As...", self)
        self.save_as_action.triggered.connect(self.save_as_file)

        self.print_action = QAction(create_svg_icon(SVG_ICONS["print"], default_icon_color), "&Print...", self)
        self.print_action.triggered.connect(self.print_file)
        self.print_action.setShortcut("Ctrl+P")

        self.close_action = QAction("&Close", self)
        self.close_action.triggered.connect(self.close_pdf)
        self.close_action.setShortcut("Ctrl+W")
        
        self.clear_recent_action = QAction("Clear Recent Files", self)
        self.clear_recent_action.triggered.connect(self.clear_recent_files)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut("Ctrl+Q")
        
        self.find_action = QAction(create_svg_icon(SVG_ICONS["search"], default_icon_color), "&Find...", self)
        self.find_action.triggered.connect(self.toggle_search_bar)
        self.find_action.setShortcut("Ctrl+F")

        self.toggle_thumbnails_action = QAction("Show &Thumbnail Pane", self)
        self.toggle_thumbnails_action.setCheckable(True)
        self.toggle_thumbnails_action.setChecked(True)
        self.toggle_thumbnails_action.triggered.connect(self.toggle_thumbnail_pane)

        self.about_action = QAction("&About Macan Reader", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        
        # DITAMBAHKAN: Aksi Toolbar (yang perlu di-update warnanya)
        self.prev_page_action = QAction(create_svg_icon(SVG_ICONS["prev-page"], default_icon_color), "Previous Page", self)
        self.prev_page_action.triggered.connect(lambda: self.go_to_page(self.current_page - 1))
        self.prev_page_action.setShortcut("Left")

        self.next_page_action = QAction(create_svg_icon(SVG_ICONS["next-page"], default_icon_color), "Next Page", self)
        self.next_page_action.triggered.connect(lambda: self.go_to_page(self.current_page + 1))
        self.next_page_action.setShortcut("Right")

        self.zoom_out_action = QAction(create_svg_icon(SVG_ICONS["zoom-out"], default_icon_color), "Zoom Out", self)
        self.zoom_out_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() - 10))
        self.zoom_out_action.setShortcut("Ctrl+-")

        self.zoom_in_action = QAction(create_svg_icon(SVG_ICONS["zoom-in"], default_icon_color), "Zoom In", self)
        self.zoom_in_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_slider.value() + 10))
        self.zoom_in_action.setShortcut("Ctrl+=")
        
        # DITAMBAHKAN: Aksi Reset Zoom
        self.zoom_reset_action = QAction(create_svg_icon(SVG_ICONS["zoom-reset"], default_icon_color), "Reset Zoom (100%)", self)
        self.zoom_reset_action.triggered.connect(self.reset_zoom)
        self.zoom_reset_action.setShortcut("Ctrl+0")

        self.pan_action = QAction(create_svg_icon(SVG_ICONS["hand"], default_icon_color), "Pan Tool (Drag to move page)", self)
        self.pan_action.setCheckable(True)
        self.pan_action.triggered.connect(self.toggle_pan_mode)
        
        # DITAMBAHKAN: Aksi Tema
        self.light_theme_action = QAction("Light", self, checkable=True, triggered=lambda: self.set_theme("light"))
        self.dark_theme_action = QAction("Dark", self, checkable=True, triggered=lambda: self.set_theme("dark"))
        self.dark_blue_theme_action = QAction("Dark Blue", self, checkable=True, triggered=lambda: self.set_theme("dark-blue"))
        self.neon_blue_theme_action = QAction("Neon Blue", self, checkable=True, triggered=lambda: self.set_theme("neon-blue"))
        self.soft_pink_theme_action = QAction("Soft Pink", self, checkable=True, triggered=lambda: self.set_theme("soft-pink"))
        
        self.themes_action_group.addAction(self.light_theme_action)
        self.themes_action_group.addAction(self.dark_theme_action)
        self.themes_action_group.addAction(self.dark_blue_theme_action)
        self.themes_action_group.addAction(self.neon_blue_theme_action)
        self.themes_action_group.addAction(self.soft_pink_theme_action)


    def create_menus(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        
        file_menu.addAction(self.close_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.find_action)
        
        window_menu = menu_bar.addMenu("&Window")
        window_menu.addAction(self.toggle_thumbnails_action)
        
        # DITAMBAHKAN: Menu Tema
        themes_menu = menu_bar.addMenu("&Themes")
        themes_menu.addAction(self.light_theme_action)
        themes_menu.addAction(self.dark_theme_action)
        themes_menu.addAction(self.dark_blue_theme_action)
        themes_menu.addAction(self.neon_blue_theme_action)
        themes_menu.addAction(self.soft_pink_theme_action)
        
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.print_action)
        toolbar.addAction(self.save_as_action)
        toolbar.addSeparator()

        # DIUBAH: Aksi sudah dibuat di create_actions
        toolbar.addAction(self.prev_page_action)
        toolbar.addAction(self.next_page_action)
        
        toolbar.addSeparator()

        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_reset_action) # DITAMBAHKAN: Aksi Reset Zoom
        
        toolbar.addSeparator()
        
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

    # DITAMBAHKAN: Slot untuk reset zoom
    def reset_zoom(self):
        self.zoom_slider.setValue(100)

    # DITAMBAHKAN: Metode untuk memuat pengaturan
    def load_settings(self):
        saved_theme = self.settings.value("theme", "light")
        
        # Setel aksi yang dicentang
        if saved_theme == "dark":
            self.dark_theme_action.setChecked(True)
        elif saved_theme == "dark-blue":
            self.dark_blue_theme_action.setChecked(True)
        elif saved_theme == "neon-blue":
            self.neon_blue_theme_action.setChecked(True)
        elif saved_theme == "soft-pink":
            self.soft_pink_theme_action.setChecked(True)
        else:
            self.light_theme_action.setChecked(True)
            
        # Terapkan tema
        self.set_theme(saved_theme)

    # DITAMBAHKAN: Metode untuk menerapkan tema
    def set_theme(self, theme_name):
        style = THEME_STYLESHEETS.get(theme_name, "")
        QApplication.instance().setStyleSheet(style)
        self.settings.setValue("theme", theme_name)
        
        # Perbarui warna ikon
        icon_color = THEME_ICON_COLORS.get(theme_name, "black")
        self.update_icons_for_theme(icon_color)
        
    # DITAMBAHKAN: Metode untuk memperbarui semua ikon
    def update_icons_for_theme(self, icon_color):
        self.open_action.setIcon(create_svg_icon(SVG_ICONS["open"], icon_color))
        self.print_action.setIcon(create_svg_icon(SVG_ICONS["print"], icon_color))
        self.save_as_action.setIcon(create_svg_icon(SVG_ICONS["save"], icon_color))
        self.find_action.setIcon(create_svg_icon(SVG_ICONS["search"], icon_color))
        
        self.prev_page_action.setIcon(create_svg_icon(SVG_ICONS["prev-page"], icon_color))
        self.next_page_action.setIcon(create_svg_icon(SVG_ICONS["next-page"], icon_color))
        self.zoom_in_action.setIcon(create_svg_icon(SVG_ICONS["zoom-in"], icon_color))
        self.zoom_out_action.setIcon(create_svg_icon(SVG_ICONS["zoom-out"], icon_color))
        self.zoom_reset_action.setIcon(create_svg_icon(SVG_ICONS["zoom-reset"], icon_color))
        self.pan_action.setIcon(create_svg_icon(SVG_ICONS["hand"], icon_color))
        
        # Ikon tombol tutup di search bar (ukuran lebih kecil)
        close_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>"""
        self.close_search_btn.setIcon(create_svg_icon(close_icon_svg, icon_color))

    def toggle_pan_mode(self, checked):
        self.pdf_view_label.setPanMode(checked)

    def toggle_thumbnail_pane(self, checked):
        self.thumb_scroll_area.setVisible(checked)

    def toggle_search_bar(self):
        is_visible = self.search_widget.isVisible()
        self.search_widget.setVisible(not is_visible)
        if not is_visible:
            self.search_input.setFocus()
        else:
            self.clear_search()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.open_pdf(file_path)
            
    def open_pdf(self, file_path):
        try:
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

    def close_pdf(self):
        if not self.pdf:
            return
            
        self.pdf.close()
        self.pdf = None
        self.current_file_path = None
        self.current_page = 0
        
        self.setWindowTitle("Macan Reader")
        self.pdf_view_label.clear()
        self.clear_search()
        self.populate_thumbnails()
        self.update_ui_state()
        self.update_status_bar()

    def populate_thumbnails(self):
        while self.thumb_layout.count():
            child = self.thumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.pdf:
            return

        for i in range(len(self.pdf)):
            page = self.pdf[i]
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
        
        if self.search_results:
            self.draw_search_highlights(page, pixmap)
        
        self.pdf_view_label.setPixmap(pixmap)
        
        self.update_status_bar()
        self.update_ui_state()

    def go_to_page(self, page_num):
        if self.pdf and 0 <= page_num < len(self.pdf):
            self.display_page(page_num)
            
            for i in range(self.thumb_layout.count()):
                widget = self.thumb_layout.itemAt(i).widget()
                if isinstance(widget, ThumbnailLabel):
                    # DIUBAH: Gunakan setStyleSheet("") untuk reset ke tema
                    if widget.page_num == page_num:
                        # Warna highlight biru standar, menonjol di semua tema
                        widget.setStyleSheet("border: 2px solid #0078d4; padding: 2px; margin: 5px;")
                    else:
                        widget.setStyleSheet("") # Reset ke gaya tema default

    def set_zoom(self, value):
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f" {value}% ")
        self.display_page(self.current_page)

    # --- Bagian Logika Pencarian ---

    def clear_search(self):
        self.search_results = []
        self.current_search_index = -1
        if self.pdf:
            self.display_page(self.current_page)
        self.status_bar.clearMessage()

    def run_search(self):
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
                self.search_results.append((i, rect))
                
        self.status_bar.showMessage(f"Found {len(self.search_results)} result(s).")
        
    def find_next(self):
        text = self.search_input.text()
        if not text: return
        
        if not self.search_results:
            self.run_search()
            
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.highlight_search_result()

    def find_prev(self):
        text = self.search_input.text()
        if not text: return

        if not self.search_results:
            self.run_search()

        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1 + len(self.search_results)) % len(self.search_results)
        self.highlight_search_result()

    def highlight_search_result(self):
        if not self.search_results:
            return
            
        page_num, rect = self.search_results[self.current_search_index]
        
        if page_num != self.current_page:
            self.go_to_page(page_num)
        else:
            self.display_page(page_num)
            
        # TODO: Scroll ke area highlight jika di luar pandangan

    def convert_pdf_rect_to_pixmap(self, page, rect):
        l, b, r, t = rect
        page_width, page_height = page.get_size()
        
        pixmap_x = l * self.zoom_factor
        pixmap_y = (page_height - t) * self.zoom_factor
        pixmap_w = (r - l) * self.zoom_factor
        pixmap_h = (t - b) * self.zoom_factor
        
        return QRectF(pixmap_x, pixmap_y, pixmap_w, pixmap_h)

    def draw_search_highlights(self, page, pixmap):
        painter = QPainter(pixmap)
        
        highlight_color = QColor(255, 255, 0, 100)
        active_highlight_color = QColor(255, 165, 0, 150)
        
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

            if page_range == QPrinter.PageRange.PageRange:
                pages_to_print = list(range(from_page - 1, min(to_page, len(self.pdf))))
            elif page_range == QPrinter.PageRange.CurrentPage:
                pages_to_print = [self.current_page]

            for i, page_idx in enumerate(pages_to_print):
                if page_idx >= len(self.pdf):
                    continue
                    
                page = self.pdf[page_idx]
                
                scale = printer.resolution() / 72.0
                img = page.render(scale=scale).to_pil()
                
                q_img = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                
                page_rect = printer.pageRect(QPrinter.Unit.Pixel)
                img_pixmap = QPixmap.fromImage(q_img)
                
                scaled_pixmap = img_pixmap.scaled(page_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
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
        <p>v2.0.0</p>
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
            self.recent_files_menu.addSeparator()
            self.recent_files_menu.addAction(self.clear_recent_action)
        else:
            no_recent_action = QAction("No Recent Files", self)
            no_recent_action.setEnabled(False)
            self.recent_files_menu.addAction(no_recent_action)

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
        
        self.save_as_action.setEnabled(is_pdf_loaded)
        self.print_action.setEnabled(is_pdf_loaded)
        self.close_action.setEnabled(is_pdf_loaded)
        
        self.find_action.setEnabled(is_pdf_loaded)
        self.pan_action.setEnabled(is_pdf_loaded)
        if not is_pdf_loaded and self.pan_action.isChecked():
            self.pan_action.setChecked(False)
            self.toggle_pan_mode(False)
        
        self.zoom_in_action.setEnabled(is_pdf_loaded)
        self.zoom_out_action.setEnabled(is_pdf_loaded)
        self.zoom_reset_action.setEnabled(is_pdf_loaded) # DITAMBAHKAN
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