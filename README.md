# Color Picker

A modular desktop application built with Python and Tkinter designed for precise color extraction, real-time pixel inspection, and image-based palette management.

## Screenshots

<div align="center">
  <p><strong>Main Workspace</strong></p>
  <p><em>Running in Dark Mode with custom Pixel Font</em></p>
  <img src="https://github.com/user-attachments/assets/e9510f27-c626-4b9c-9769-4f096f3cb687" width="750">
</div>

<br>

---


## Features

- **Pixel-Level Precision:** Interactive canvas with responsive scaling and image rendering via Pillow.
- **Drag-and-Drop Workflow:** Seamless image loading by dragging image files directly into the application workspace.
- **Magnifying Loupe:** Real-time magnified inspection window displaying exact HEX and RGB color values.
- **Theme & Typography Customization:** Toggle between Light and Dark modes with support for dynamic font switching (including custom pixel font and Panton) loaded in-memory via GDI.
- **Palette Management:** Organize, save, and persist custom palettes locally via `save.json`.
- **Decoupled Architecture:** Clean separation of concerns between UI components (`workspace_view`, `sidebar_view`), business logic (`color_engine`), and storage (`project_manager`).
- **Native Windows Integration:** Dedicated taskbar grouping via `AppUserModelID` and standalone executable support.

---

## Detailed Views

| Pixel Inspector | Palette Management |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/758ab103-c1e1-47f2-92c3-49adf41ebc24" alt="Loupe Preview" width="400"> | <img src="https://github.com/user-attachments/assets/f5e7d897-cf57-4402-8a26-49056ee36532" alt="Palette Preview" width="400"> |
| *Precise coordinate picking with live HEX preview* | *Automatically generates dominant tones and manages color swatches* |

---

## Architecture
```text
color-picker-desktop/
├── assets/
│   ├── fonts/               # Custom TTF typography (Panton, Pixel)
│   ├── icon.ico             # Windows executable icon (multi-resolution)
│   └── icon.png             # Application logo and window icon
├── core/
│   ├── color_engine.py      # Color calculations and pixel sampling
│   ├── config.py            # Application constants and layout dimensions
│   ├── project_manager.py   # State management and JSON persistence orchestration
│   └── theme_manager.py     # Light/Dark mode themes and dynamic font handling
├── views/
│   ├── sidebar_view.py      # Sidebar controls, theme toggles, and palette management
│   └── workspace_view.py    # Canvas, image rendering, drag-and-drop, and loupe inspector
├── color_picker_main.pyw    # Application entry point and window orchestration
├── requirements.txt         # Python dependencies
└── save.json                # Local persistence store for custom palettes and settings
```
---

## Download & Run (Windows)

*No Python installation required.*

1. Go to the [Releases](https://github.com/raysandzzz/color-picker-desktop/releases/latest) section.
2. Download `ColorPicker-v1.1.0-windows.zip`.
3. Extract the contents and double-click `ColorPicker.exe`.
4. (Optional) You can add a desktop shortcut for added convenience :)

> **Note on Windows SmartScreen / Defender:**  
> Since this standalone binary is packaged with PyInstaller and is not digitally signed with a commercial certificate, Windows Defender or SmartScreen may flag it as an unrecognized file.  
> You can safely proceed by clicking **"More info" → "Run anyway"**. The application runs completely offline and the full source code is inspectable in this repository.

---

## Development Setup

If you want to run or modify the source code locally:

### Prerequisites
- Python 3.10+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/raysandzzz/color-picker-desktop.git
   cd color-picker-desktop
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```powershell
   python color_picker_main.pyw
   ```

---

## Build Standalone Executable

To compile into a standalone Windows binary using PyInstaller:

```powershell
pyinstaller --clean --noconfirm --onedir --windowed --icon="assets/icon.ico" --add-data "assets;assets" --name="ColorPicker" color_picker_main.pyw
```

The output will be generated inside the `dist/ColorPicker/` directory.

---

## Tech Stack

* **GUI Framework:** Python 3 / Tkinter
* **Drag-and-Drop:** [TkinterDnD2](https://github.com/pmgagne/tkinterdnd2)
* **Image Processing:** [Pillow (PIL)](https://python-pillow.org/)
* **Data Storage:** JSON (`save.json`)
* **Packaging:** [PyInstaller](https://pyinstaller.org/)
