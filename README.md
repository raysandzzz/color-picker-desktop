# Color Picker

A modular desktop application built with Python and Tkinter designed for precise color extraction, real-time pixel inspection, and image-based palette management.

## Screenshots

<div align="center">
  <p><strong>Main Workspace & Pixel Inspector</strong></p>
  <img src="https://github.com/user-attachments/assets/083c5c2e-1cbb-41bc-af79-4be40647748c" alt="Color Picker Workspace" width="750">
</div>

<br>

---

## Features

- **Pixel-Level Precision:** Interactive canvas with responsive scaling and image rendering via Pillow.
- **Magnifying Loupe:** Real-time magnified inspection window displaying exact HEX and RGB color values.
- **Palette & Project Management:** Organize, save, and persist custom palettes locally via `projects.json`.
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
├── views/
│   ├── sidebar_view.py       # Sidebar controls and palette management
│   └── workspace_view.py     # Canvas, image rendering, and loupe inspector
├── color_engine.py           # Color calculations and pixel sampling
├── project_manager.py        # Project state and JSON persistence
├── config.py                 # Application constants, theme colors, and layout dimensions
├── color_picker_main.pyw     # Application entry point and window orchestration
├── icon.ico                  # Application icon (multi-resolution)
└── requirements.txt          # Python dependencies
```

---

## Download & Run (Windows)

*No Python installation required.*

1. Go to the [Releases](https://github.com/raysandzzz/color-picker-desktop/releases/latest) section.
2. Download `ColorPicker-v1.0.0-windows.zip`.
3. Extract the contents and double-click `ColorPicker.exe`.
4. (Optional) You can add a desktop shortcut for added convenience :)

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
pyinstaller --noconfirm --onedir --windowed --icon="icon.ico" --add-data "icon.ico;." --name="ColorPicker" color_picker_main.pyw
```

The output will be generated inside the `dist/ColorPicker/` directory.

---

## Tech Stack

* **GUI Framework:** Python 3 / Tkinter
* **Image Processing:** [Pillow (PIL)](https://python-pillow.org/)
* **Data Storage:** JSON (`projects.json`)
* **Packaging:** [PyInstaller](https://pyinstaller.org/)
