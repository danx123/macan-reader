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
<img width="958" height="644" alt="Screenshot 2025-10-22 175550" src="https://github.com/user-attachments/assets/900c33a8-0f10-4c39-9a8b-d4d20e396317" />




---

## 📝 Changelog v3.3.0

- Added logic for handling password-protected PDFs
- Added numbering to the Thumbnail Pane
- Added a Jump Page function
(to jump to the desired page)
by entering the page number

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
