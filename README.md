# StegoHideX

A Windows desktop application to hide and extract any file type inside image files (PNG, JPEG) using steganography. Features a modern GUI, drag-and-drop support, password protection, and robust security measures.

## Features
- Hide any file inside an image (PNG, JPEG)
- Extract files from images
- Optional password protection (AES encryption)
- Drag-and-drop interface
- Dark mode
- Native Windows look (PyQt6)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Development
- Python 3.11+
- PyQt6 for GUI
- Pillow for image handling
- stegano for steganography
- cryptography for encryption

## License
MIT
