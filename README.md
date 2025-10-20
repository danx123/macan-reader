## 📖 Macan Reader is a fast, efficient, and feature-rich PDF document reader built using Python, the modern GUI library PySide6, and powered by the PyPDFium2 PDF rendering engine. It is designed to provide a seamless PDF reading experience with a focus on performance and a customizable user interface.
---

## ✨ Key Features
Fast & Efficient Rendering: Uses PyPDFium2 (based on Google PDFium) for fast and reliable PDF rendering.
Theme Support (QSS): Five selectable visual themes (Light, Dark, Dark Blue, Neon Blue, Soft Pink) to customize the app's appearance, with dynamic icon color updates.
Pan Mode: A dedicated Pan tool that allows users to drag PDF pages with the mouse within the viewing area.
Page Thumbnails: A panel of thumbnails that can be hidden for quick page navigation.
Full Navigation: Page switching, dynamic zoom control via a slider, zoom in/out/reset buttons, and keyboard navigation.
Search Features: Find function with Match Case option and highlighting of active search results.
Recent Files: Maintains a list of recently opened files for quick access.
Drag-and-Drop Support: Easily open PDF files by dragging them into the application window.
Basic File Operations: Open, Close, Print (using QPrinter), and Save As (for copying/duplicating PDFs).
Export to: Png, Docx
---

## 📸 Screenshot
<img width="955" height="650" alt="Screenshot 2025-10-20 222726" src="https://github.com/user-attachments/assets/f2a0ea7a-70f8-458f-a4e9-b2c4f60c0229" />
<img width="955" height="647" alt="Screenshot 2025-10-20 222750" src="https://github.com/user-attachments/assets/8707ed66-d18f-4149-b8e2-599377930558" />
<img width="1080" height="1920" alt="macan_reader_v3" src="https://github.com/user-attachments/assets/309c3e73-9268-467e-ac48-54d242ba5d81" />


---

## 📝 Changelog v3.0.0

Print Preview Added: The "Print" menu (Ctrl+P) now opens the Print Preview dialog first, where you can preview how the page will print before sending it to the printer.

"Export As" Menu Added: Under the File menu, there is now an Export As submenu with two options:
Export as PNG...: Exports all PDF pages as separate image files (e.g., document_page_001.png, document_page_002.png, etc.).
Export as DOCX...: Exports all PDF pages as images embedded into a single .docx file. (Requires python-docx to be installed: pip install python-docx).
Close Thumbnail Pane Button: The thumbnail pane on the left now has a mini title bar with the heading "Thumbnails" and an 'X' button to quickly close it.

Thumbnail Context Menu: Right-clicking on any page thumbnail will now bring up a new context menu that allows you to export that specific page as:
- PDF (creates a new PDF containing only that single page)
- PNG
- DOCX (creates a new DOCX containing only an image of that single page)
Zoom Slider Icon Improved: The handles on the QSlider in the status bar now appear round in all themes, instead of flat squares.
Help Content Menu Added: Under the Help menu, there is now a Help Content option (Shortcut: F1) that opens a pop-up window with a guide on how to use the application's main features.

---


## 🪄 Technologies Used
Python 3.x
PySide6: Python binding library for Qt6, used for the graphical user interface.
PyPDFium2: Python wrapper for the PDFium rendering library, used for processing PDF documents.

---

## 🔨 Usage
After running the application:
Use the Open button (or Ctrl+O) from the Toolbar/File Menu to load a PDF file.
Navigate using the Previous Page and Next Page buttons on the Toolbar.
Adjust the display using the Zoom Slider in the Status Bar or the Zoom In/Out/Reset buttons.
Activate the Pan Tool mode to pan the page by dragging the mouse.
Access the search function with the Find button (or Ctrl+F).
Change the theme through the Themes menu for a different visual experience.

---

🎭 Contributions
Contributions are welcome! If you have an idea for a new feature, bug fix, or want to add a new theme, please:
Fork this repository.
Create a new branch (git checkout -b feature/AmazingFeature).
Make changes and commit them (git commit -m 'Add some AmazingFeature').
Push to the branch (git push origin feature/AmazingFeature).
Open a Pull Request.

---

📃 License
This project is licensed under the MIT License. See the LICENSE file for more details.
