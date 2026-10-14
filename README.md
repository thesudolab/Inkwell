<p align="center">
  <img src="Inkwell PDF Editor Logo (1).png" alt="Inkwell PDF Viewer & Editor Logo" width="220"/>
</p>

<h1 align="center">Inkwell PDF Viewer, Editor & Encryptor</h1>

<p align="center">
  <b>A lightweight, secure, and feature-rich desktop PDF editor, viewer, and encryption utility built with Python, HTML5 Canvas, and modern web libraries.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platforms">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

---

## 🚀 Overview

**Inkwell** is an all-in-one desktop application designed for fast, privacy-focused PDF manipulation. Running locally through a secure embedded web window via a lightweight background server, your files never touch an external cloud or server—everything stays strictly on your machine.

This repository contains the single `builder.py` script, which handles embedding the frontend application, running a local server, launching the desktop window, and compiling a standalone binary package.

---

## ✨ Features

- **📖 Comprehensive Viewing & Navigation:** Smoothly render, zoom, pan, and jump across multi-page PDF documents.
- **✍️ Annotations & Edits:** Insert custom text, freehand drawings, highlights, images, and electronic signatures (Type, Draw, or Upload).
- **🔒 Redaction & Blurring:** Securely cover, erase, or apply gaussian blur to confidential info.
- **📑 Page Management:** Reorder or delete specific pages from your document.
- **🔐 Password Encryption:** Securely lock any PDF with custom user/owner passwords and permissions directly from the interface.
- **📦 Standalone Binary Builder:** Package the entire project into an independent executable with a single command.

---

## 📂 Repository Structure

```text
Inkwell/
│
├── builder.py                  # All-in-one application runner, server, and PyInstaller builder script
├── Inkwell PDF Editor Logo (1).png  # Project logo
└── README.md                   # Project documentation

```

*(Note: Compiled binaries and build folders are ignored via `.gitignore` and generated locally when building).*

---

## 📋 Prerequisites

Before running or building the script, make sure you have the following installed on your system:

### 1. Python (Version 3.11 or newer)

Ensure Python is installed and added to your system's PATH. You can check your version by running:

```bash
python --version

```

### 2. Required Python Dependencies

Inkwell relies on standard third-party libraries for window rendering, server communication, and binary packaging. Run the following command in your terminal to install them:

```bash
pip install pywebview pyinstaller bottle clr_loader proxy_tools pythonnet

```

---

## ⚙️ How to Run the Script

Follow these steps to run or compile the script on your machine:

### Step 1: Save the Files

Ensure you have saved the script as **`builder.py`** and placed your logo file (**`Inkwell PDF Editor Logo (1).png`**) in the same repository folder.

### Step 2: Open Terminal / Command Prompt

Navigate to the folder where your `builder.py` file is located:

```bash
cd path/to/your/folder

```

### Step 3: Run the Application (Desktop Mode)

To launch the app directly in a native desktop window via the local Python server, execute:

```bash
python builder.py

```

### Step 4: Build a Standalone Executable

If you want to package the script into a standalone `.exe` / application binary that doesn't require Python to run on target machines:

```bash
python builder.py --build

```

* **Output:** This command will automatically compile the script and generate a clean folder named **`inkwell`** right next to your script containing your standalone application binary.

---

## 💡 How to Use Inkwell

1. **Open a PDF:** Click **Open PDF** or drag and drop any PDF file directly into the application window.
2. **Edit & Annotate:** Choose your desired tool from the toolbar (Text, Draw, Highlight, Cover, Blur, Sign, etc.).
3. **Modify Elements:** Switch to the **View** tool and select any placed element to reposition, resize, or delete it using the properties bar.
4. **Save or Lock:**
* Click **Save PDF** to export your modified document.
* Click **Lock PDF** to password-protect and encrypt the file.



---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```
