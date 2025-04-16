# 🛠️ StegoHideX — Feature Specifications

## Core Features

### ✅ File Embedding
- Select a carrier image (PNG, JPEG)
- Select a file to embed (any type)
- Optional password protection
- Output a new image with embedded data

### ✅ File Extraction
- Load an image with embedded data
- Optional password prompt
- Extract hidden file to chosen location

### ✅ Drag-and-Drop UI
- Drag image/file directly into interface
- Realtime previews (non-destructive)

## Advanced Features (Phase 2)
- Batch encoding/decoding
- Output image fingerprint checker
- Compression of embedded data
- CLI version for power users

## Security Measures
- Warn if file is too large for the selected image
- Apply light encryption for protected payloads
- Use image checksum comparison to detect tampering

## UI
- Windows-native look (WinForms or WPF)
- Dark mode toggle
- Embedded image preview
