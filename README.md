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
<img width="959" height="644" alt="Screenshot 2025-11-12 055907" src="https://github.com/user-attachments/assets/eb6376f6-691a-4a35-a843-465ba6b3b034" />
<img width="956" height="646" alt="Screenshot 2025-11-12 055724" src="https://github.com/user-attachments/assets/42650cb0-5336-46f3-9d88-0f4a3e502f92" />


---

## 📝 Changelog v4.5.0

✨ New Features
Continuous View Mode: Users can now toggle between the default "Single Page" view and a new "Continuous" view (Ctrl+7). This mode renders all pages in a single vertical column, allowing for smooth scrolling through the entire document without clicking "Next" or "Previous."
Toolbar Toggle: A new "Continuous View" icon has been added to the main toolbar to easily switch between view modes.
🚀 Improvements & Fixes
Virtual Page Rendering (Lazy Loading): To ensure high performance in Continuous View, only the pages currently visible (plus a small buffer) are rendered. Pages that scroll out of view are cleared from memory, keeping memory usage low even for large documents.
FIXED: Lazy Loading Render Bug: Resolved a critical bug where the lazy loading mechanism would fail to render pages beyond the initial view (often stopping after 1-2 pages). All pages now correctly load as the user scrolls.
Enhanced Tool Compatibility:
Zoom: Zooming (Ctrl++/Ctrl+-, slider) now works perfectly in Continuous View, resizing all pages and recalculating the scroll layout on the fly.
Pan Tool: The Pan tool (Hand icon) is fully functional across all pages in Continuous View.
Search: Highlighting a search result (Ctrl+F) now correctly navigates to the corresponding page and scrolls it into view in both Single and Continuous modes.
Go to Page: Jumping to a page (via Ctrl+G, thumbnails, or bookmarks) now instantly scrolls to the correct page's position in Continuous View.
UI Smarts: The "Fit to Page" (Ctrl+9) action is now intelligently disabled in Continuous View, as it is only applicable to Single Page mode. "Fit to Width" (Ctrl+8) remains functional in both modes.

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
