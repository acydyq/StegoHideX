import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog,
    QCheckBox, QMenuBar, QStatusBar, QFrame
)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt

class DnDLabel(QLabel):
    def __init__(self, text, file_types, callback):
        super().__init__(text)
        self.file_types = file_types  # list of extensions or None for any
        self.callback = callback
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #f5f5f5;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            if self.file_types is None or any(file.lower().endswith(ext) for ext in self.file_types):
                event.acceptProposedAction()
                self.setStyleSheet("background: #aee1f9;")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("background: #f5f5f5;")

    def dropEvent(self, event):
        self.setStyleSheet("background: #f5f5f5;")
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            if self.file_types is None or any(file.lower().endswith(ext) for ext in self.file_types):
                self.callback(file)

import os
from stegano import lsb
from cryptography.fernet import Fernet, InvalidToken

class EncodeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Image selection
        img_hbox = QHBoxLayout()
        self.img_label = DnDLabel("Select or drag carrier image (PNG/JPEG) here", ['.png', '.jpg', '.jpeg'], self.set_image)
        self.img_btn = QPushButton("Browse Image")
        self.img_btn.clicked.connect(self.browse_image)
        self.img_status = QLabel("")
        img_hbox.addWidget(self.img_label)
        img_hbox.addWidget(self.img_btn)
        img_hbox.addWidget(self.img_status)
        layout.addLayout(img_hbox)
        self.img_path = None

        # File selection
        file_hbox = QHBoxLayout()
        self.file_label = DnDLabel("Select or drag file to hide here", None, self.set_file)
        self.file_btn = QPushButton("Browse File")
        self.file_btn.clicked.connect(self.browse_file)
        self.file_status = QLabel("")
        file_hbox.addWidget(self.file_label)
        file_hbox.addWidget(self.file_btn)
        file_hbox.addWidget(self.file_status)
        layout.addLayout(file_hbox)
        self.file_path = None

        # Password
        self.pass_label = QLabel("Password (optional):")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        # Output path
        out_hbox = QHBoxLayout()
        self.out_label = QLabel("Output image filename:")
        self.out_btn = QPushButton("Choose Output Path")
        self.out_btn.clicked.connect(self.choose_output_path)
        self.out_status = QLabel("")
        out_hbox.addWidget(self.out_label)
        out_hbox.addWidget(self.out_btn)
        out_hbox.addWidget(self.out_status)
        layout.addLayout(out_hbox)
        self.output_path = None

        # Embed button
        self.embed_btn = QPushButton("Embed")
        self.embed_btn.clicked.connect(self.embed_file)
        layout.addWidget(self.embed_btn)

        # Image preview placeholder
        self.preview = QLabel("[Image preview will appear here]")
        self.preview.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(150)
        layout.addWidget(self.preview)

        # Status area
        self.status = QLabel("")
        layout.addWidget(self.status)

        self.setLayout(layout)

    def set_image(self, file):
        if file and file.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.img_path = file
            self.img_status.setText("✅")
            self.status.setText(f"Selected image: {file}")
            self.show_image_preview(file)
        else:
            self.img_path = None
            self.img_status.setText("❌")
            self.status.setText("⚠️ Please select a valid PNG/JPEG image.")
            self.preview.setText("[Image preview will appear here]")

    def set_file(self, file):
        if file:
            self.file_path = file
            self.file_status.setText("✅")
            self.status.setText(f"Selected file: {file}")
        else:
            self.file_path = None
            self.file_status.setText("❌")
            self.status.setText("⚠️ Please select a file to hide.")

    def browse_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.set_image(file)

    def show_image_preview(self, file):
        pixmap = QPixmap(file)
        if not pixmap.isNull():
            self.preview.setPixmap(pixmap.scaled(self.preview.width(), self.preview.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.preview.setText("[Image preview will appear here]")

    def extract_file(self):
        # Validation
        if not self.img_path or not os.path.isfile(self.img_path):
            self.status.setText("❌ Please select a valid image to extract from.")
            return
        try:
            # Extract hex string using stegano
            payload_hex = lsb.reveal(self.img_path)
            if not payload_hex:
                self.status.setText("❌ No hidden file found in image.")
                return
            payload_data = bytes.fromhex(payload_hex)
            password = self.pass_input.text().strip()
            # Decrypt if password is provided
            if password:
                try:
                    key = (password.ljust(32, '0')[:32]).encode('utf-8')
                    fernet_key = Fernet(base64.urlsafe_b64encode(key))
                    payload_data = fernet_key.decrypt(payload_data)
                except InvalidToken:
                    self.status.setText("❌ Incorrect password or corrupted data.")
                    return
            # Ask user where to save extracted file
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Extracted File As", "", "All Files (*)")
            if not save_path:
                self.status.setText("⚠️ Extraction cancelled by user.")
                return
            with open(save_path, "wb") as f:
                f.write(payload_data)
            self.status.setText(f"✅ File extracted and saved to: {save_path}")
        except Exception as e:
            self.status.setText(f"❌ Error during extraction: {e}")

    def embed_file(self):
        import time
        # Validation
        self.status.setText("Starting embedding...")
        QApplication.processEvents()
        if not self.img_path or not os.path.isfile(self.img_path):
            self.status.setText("❌ Please select a valid carrier image.")
            return
        if not self.file_path or not os.path.isfile(self.file_path):
            self.status.setText("❌ Please select a valid file to hide.")
            return
        if not self.output_path or not self.output_path.lower().endswith((".png", ".jpg", ".jpeg")):
            self.status.setText("❌ Please select a valid output image filename.")
            return
        try:
            # Read payload
            self.status.setText("Reading file to hide...")
            QApplication.processEvents()
            with open(self.file_path, "rb") as f:
                payload_data = f.read()
            # Estimate carrier image capacity (for PNG/JPEG, roughly width*height*3 bits)
            from PIL import Image
            img = Image.open(self.img_path)
            width, height = img.size
            max_capacity = (width * height * 3) // 8  # bytes
            if len(payload_data) > max_capacity // 2:
                self.status.setText(f"❌ File too large for selected image. Max recommended: {max_capacity//2} bytes, your file: {len(payload_data)} bytes.")
                return
            # Encrypt if password provided
            password = self.pass_input.text().strip()
            if password:
                self.status.setText("Encrypting payload...")
                QApplication.processEvents()
                key = (password.ljust(32, '0')[:32]).encode('utf-8')
                fernet_key = Fernet(base64.urlsafe_b64encode(key))
                payload_data = fernet_key.encrypt(payload_data)
            # Convert payload to hex string for stegano
            self.status.setText("Encoding payload...")
            QApplication.processEvents()
            payload_hex = payload_data.hex()
            # Embed using stegano
            self.status.setText("Embedding payload in image...")
            QApplication.processEvents()
            secret = lsb.hide(self.img_path, payload_hex)
            secret.save(self.output_path)
            self.status.setText(f"✅ File embedded successfully! Saved to: {self.output_path}")
        except Exception as e:
            self.status.setText(f"❌ Error during embedding: {e}")

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File to Hide", "", "All Files (*)")
        if file:
            self.set_file(file)

    def choose_output_path(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Output Image As", "", "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)")
        if file and file.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.output_path = file
            self.out_status.setText("✅")
            self.status.setText(f"Output image: {file}")
        else:
            self.output_path = None
            self.out_status.setText("❌")
            self.status.setText("⚠️ Please select a valid output PNG/JPEG filename.")

import base64

class DecodeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Define set_image before using it as a callback
        def set_image(file):
            if file and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.img_path = file
                self.img_status.setText("✅")
                self.status.setText(f"Selected image: {file}")
                self.show_image_preview(file)
            else:
                self.img_path = None
                self.img_status.setText("❌")
                self.status.setText("⚠️ Please select a valid PNG/JPEG image.")
                self.preview.setText("[Image preview will appear here]")
        self.set_image = set_image

        # Image selection
        img_hbox = QHBoxLayout()
        self.img_label = DnDLabel("Select or drag image with hidden file here", ['.png', '.jpg', '.jpeg'], self.set_image)
        self.img_btn = QPushButton("Browse Image")
        self.img_btn.clicked.connect(self.browse_image)
        self.img_status = QLabel("")
        img_hbox.addWidget(self.img_label)
        img_hbox.addWidget(self.img_btn)
        img_hbox.addWidget(self.img_status)
        layout.addLayout(img_hbox)
        self.img_path = None

        # Password
        self.pass_label = QLabel("Password (optional):")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        # Extract button
        self.extract_btn = QPushButton("Extract")
        self.extract_btn.clicked.connect(self.extract_file)
        layout.addWidget(self.extract_btn)

        # Image preview placeholder
        self.preview = QLabel("[Image preview will appear here]")
        self.preview.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview)

        # Status area
        self.status = QLabel("")
        layout.addWidget(self.status)

        self.setLayout(layout)

    def show_image_preview(self, file):
        pixmap = QPixmap(file)
        if not pixmap.isNull():
            self.preview.setPixmap(pixmap.scaled(self.preview.width(), self.preview.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.preview.setText("[Image preview will appear here]")

    def extract_file(self):
        # Validation
        if not self.img_path or not os.path.isfile(self.img_path):
            self.status.setText("❌ Please select a valid image to extract from.")
            return
        try:
            # Extract hex string using stegano
            payload_hex = lsb.reveal(self.img_path)
            if not payload_hex:
                self.status.setText("❌ No hidden file found in image.")
                return
            payload_data = bytes.fromhex(payload_hex)
            password = self.pass_input.text().strip()
            # Decrypt if password is provided
            if password:
                try:
                    key = (password.ljust(32, '0')[:32]).encode('utf-8')
                    fernet_key = Fernet(base64.urlsafe_b64encode(key))
                    payload_data = fernet_key.decrypt(payload_data)
                except InvalidToken:
                    self.status.setText("❌ Incorrect password or corrupted data.")
                    return
            # Ask user where to save extracted file
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Extracted File As", "", "All Files (*)")
            if not save_path:
                self.status.setText("⚠️ Extraction cancelled by user.")
                return
            with open(save_path, "wb") as f:
                f.write(payload_data)
            self.status.setText(f"✅ File extracted and saved to: {save_path}")
        except Exception as e:
            self.status.setText(f"❌ Error during extraction: {e}")

    def browse_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.img_path = file
            self.status.setText(f"Selected image: {file}")

class StegoHideXApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('StegoHideX')
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        # Tabs
        self.tabs = QTabWidget()
        self.encode_tab = EncodeTab()
        self.decode_tab = DecodeTab()
        self.tabs.addTab(self.encode_tab, "Encode (Hide File)")
        self.tabs.addTab(self.decode_tab, "Decode (Extract File)")
        self.setCentralWidget(self.tabs)

        # Menu bar
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        theme_menu = view_menu.addMenu('Theme')
        help_menu = menubar.addMenu('Help')

        # Theme actions
        self.theme_actions = {}
        themes = [
            ('Cyberpunk', 'cyberpunk.qss'),
            ('Classic', 'classic.qss')
        ]
        for theme_name, qss_file in themes:
            action = QAction(theme_name, self, checkable=True)
            action.triggered.connect(lambda checked, t=theme_name: self.set_theme(t))
            theme_menu.addAction(action)
            self.theme_actions[theme_name] = action
        # Default to Cyberpunk checked
        self.theme_actions['Cyberpunk'].setChecked(True)

        # Dark mode toggle (optional/legacy)
        self.dark_mode_action = QAction('Dark Mode', self, checkable=True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # About
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Apply default theme
        self.set_theme('Cyberpunk')

    def set_theme(self, theme_name):
        # Uncheck all, check selected
        for name, action in self.theme_actions.items():
            action.setChecked(name == theme_name)
        # Load QSS
        import os
        qss_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles', f'{theme_name.lower()}.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            self.setStyleSheet("")

    def toggle_dark_mode(self, checked):
        # Optional: disables theme if toggled
        if checked:
            self.setStyleSheet("""
                QMainWindow { background: #232629; color: #f0f0f0; }
                QLabel, QPushButton, QLineEdit { color: #f0f0f0; background: #232629; }
                QTabWidget::pane { border: 1px solid #444; }
            """)
            # Uncheck all theme actions
            for action in self.theme_actions.values():
                action.setChecked(False)
        else:
            self.set_theme('Cyberpunk')

    def show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "About StegoHideX", "StegoHideX\nHide any file inside an image using steganography.\nDeveloped by acyd + AI team.")

if __name__ == '__main__':
    from PyQt6.QtGui import QFontDatabase
    import os
    import sys

    app = QApplication(sys.argv)
    # Load Orbitron font
    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'Orbitron-Regular.ttf')
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
    window = StegoHideXApp()
    window.show()
    sys.exit(app.exec())

