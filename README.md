# 🖋️ Inkwell PDF Viewer, Editor & Encryptor
<img width="1254" height="1254" alt="Inkwell PDF Editor Logo (1)" src="https://github.com/user-attachments/assets/8198cae6-06ac-46eb-808a-a0dad5eb7992" />

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

This repository contains the all-in-one `builder.py` script, which automatically handles embedding the frontend application, running a local server, launching the desktop window, and compiling a standalone binary package.

---

## ✨ Features

* **📖 Comprehensive Viewing & Navigation:** Smoothly render, zoom, pan, and jump across multi-page PDF documents.
* **✍️ Annotations & Edits:** Insert custom text, freehand drawings, highlights, images, and electronic signatures (Type, Draw, or Upload).
* **🔒 Redaction & Blurring:** Securely cover, erase, or apply gaussian blur to confidential info.
* **📑 Page Management:** Reorder or delete specific pages from your document.
* **🔐 Password Encryption:** Securely lock any PDF with custom user/owner passwords and permissions directly from the interface.
* **📦 Standalone Binary Builder:** Package the entire project into an independent executable with a single command.

---

## 📂 Repository Structure

```text
Inkwell/
│
├── builder.py       # All-in-one application runner, server, and PyInstaller builder script
└── README.md        # Project documentation
