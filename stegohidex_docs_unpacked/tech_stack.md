# 💻 StegoHideX — Tech Stack & Dependencies

## Primary Languages
- Python 3.11+ or C# (depending on implementation)
- GUI: 
  - Python: Tkinter or PyQt6
  - C#: WPF (.NET 6)

## Steganography Libraries
- Python:
  - `stegano` (LSB-based)
  - `cryptography` (for payload encryption)
- C#:
  - Custom byte array encoding via `System.Drawing`
  - Optional: `ImageSharp` for more control

## Packaging
- `PyInstaller` (Python)
- `MSIX` or `InnoSetup` (C#)

## Optional Enhancements
- OpenCV for image validation
- Pillow for image manipulation (Python)
- AES-based encryption for payloads

## Target OS
- Windows 10 and above (x64)
