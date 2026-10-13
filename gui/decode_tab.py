"""
gui/decode_tab.py
Decoding & Steganographic Message Extraction Tab
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton, QFileDialog,
    QGroupBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from core.huffman import HuffmanEngine
from core.steganography import StegoEngine
from .tree_widget import AnimatedTreeWidget
from .encode_tab import DropImageLabel


class DecodeTab(QWidget):
    """Tab for loading a stego PNG image, authenticating header, and extracting text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stego_engine = StegoEngine()
        self.huffman_engine = HuffmanEngine()
        self.current_stego_path: str = ""
        self.extracted_root = None

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT PANEL: Stego Image Input & Status ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Stego Image Picker Card
        img_group = QGroupBox("1. Steganographic Carrier Image")
        img_layout = QVBoxLayout(img_group)

        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("Browse Carrier PNG...")
        self.btn_select.setObjectName("secondaryBtn")
        self.btn_select.clicked.connect(self._select_stego_image)
        self.file_lbl = QLabel("No image selected")
        self.file_lbl.setStyleSheet("color: #64748B; font-family: Consolas;")
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.file_lbl)
        img_layout.addLayout(btn_layout)

        # Watermark Authentication Badge
        self.auth_badge = QLabel("STATUS: Awaiting input image...")
        self.auth_badge.setStyleSheet(
            "background-color: #0B0F19; color: #94A3B8; padding: 6px 10px; "
            "border: 1px solid #334155; border-radius: 4px; font-family: Consolas; font-size: 11px;"
        )
        img_layout.addWidget(self.auth_badge)

        # Drag and Drop Target Box
        self.drop_target = DropImageLabel("Drag & Drop Stego Carrier PNG Here\nor click Browse above")
        self.drop_target.file_dropped.connect(self._load_stego_image)
        img_layout.addWidget(self.drop_target)

        left_layout.addWidget(img_group)

        # Extract Button
        self.btn_extract = QPushButton("Extract & Decode Payload")
        self.btn_extract.setStyleSheet("font-size: 13px; font-weight: 700; padding: 10px; background-color: #059669;")
        self.btn_extract.clicked.connect(self._execute_extraction)
        left_layout.addWidget(self.btn_extract)

        # Extracted Metadata Summary
        meta_group = QGroupBox("Extraction Telemetry")
        meta_layout = QVBoxLayout(meta_group)
        self.telemetry_lbl = QLabel("Telemetry inactive.")
        self.telemetry_lbl.setStyleSheet("color: #94A3B8; font-family: Consolas; font-size: 11px; line-height: 1.4;")
        self.telemetry_lbl.setWordWrap(True)
        meta_layout.addWidget(self.telemetry_lbl)
        left_layout.addWidget(meta_group)

        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # --- RIGHT PANEL: Decoded Message & Tree ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Extracted Message Card
        msg_group = QGroupBox("Recovered Plaintext Payload")
        msg_layout = QVBoxLayout(msg_group)

        self.msg_output = QTextEdit()
        self.msg_output.setReadOnly(True)
        self.msg_output.setPlaceholderText("Extracted plaintext will appear here upon decoding...")
        msg_layout.addWidget(self.msg_output)

        btn_copy = QPushButton("Copy Payload to Clipboard")
        btn_copy.setObjectName("secondaryBtn")
        btn_copy.clicked.connect(self._copy_to_clipboard)
        msg_layout.addWidget(btn_copy)
        right_layout.addWidget(msg_group, stretch=2)

        # Reconstructed Tree Preview
        tree_group = QGroupBox("Deserialized Huffman Prefix Tree")
        tree_layout = QVBoxLayout(tree_group)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        self.tree_widget = AnimatedTreeWidget()
        tree_layout.addWidget(self.tree_widget)
        right_layout.addWidget(tree_group, stretch=3)

        splitter.addWidget(right_widget)
        splitter.setSizes([450, 650])

        main_layout.addWidget(splitter)

    def _select_stego_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Stego Image", "", "PNG Images (*.png);;All Files (*.*)"
        )
        if file_path:
            self._load_stego_image(file_path)

    def _load_stego_image(self, file_path: str):
        self.current_stego_path = file_path
        self.file_lbl.setText(Path(file_path).name)

        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.drop_target.setPixmap(pixmap.scaled(220, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self._check_watermark(file_path)

    def _check_watermark(self, path: str):
        try:
            from PIL import Image
            import numpy as np
            with Image.open(path) as img:
                flat = np.array(img.convert("RGB"), dtype=np.uint8).flatten()
            magic = "".join(str(b & 1) for b in flat[:16])
            if magic == self.stego_engine.MAGIC_SIGNATURE:
                self.auth_badge.setText("AUTHENTICATED: Valid HuffStego Header (0x5354)")
                self.auth_badge.setStyleSheet(
                    "background-color: #064E3B; color: #34D399; padding: 6px 10px; "
                    "border: 1px solid #059669; border-radius: 4px; font-family: Consolas; font-size: 11px; font-weight: 700;"
                )
            else:
                self.auth_badge.setText("WARNING: Missing Magic Signature (0x5354)")
                self.auth_badge.setStyleSheet(
                    "background-color: #451A03; color: #FBBF24; padding: 6px 10px; "
                    "border: 1px solid #D97706; border-radius: 4px; font-family: Consolas; font-size: 11px; font-weight: 700;"
                )
        except Exception:
            self.auth_badge.setText("ERROR: Inspection Failed")
            self.auth_badge.setStyleSheet(
                "background-color: #450A0A; color: #F87171; padding: 6px 10px; "
                "border: 1px solid #DC2626; border-radius: 4px; font-family: Consolas; font-size: 11px; font-weight: 700;"
            )

    def _execute_extraction(self):
        if not self.current_stego_path:
            QMessageBox.warning(self, "Carrier Required", "Please select a stego PNG image to extract from.")
            return

        try:
            # 1. Extract raw bitstreams from LSBs
            tree_bits, payload_bits = self.stego_engine.extract(self.current_stego_path)

            # 2. Reconstruct Huffman tree from serialized bitstream
            reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
            self.extracted_root = reconstructed_root

            # 3. Decode payload bitstream to original Unicode string
            decoded_text = self.huffman_engine.decode_to_text(payload_bits, reconstructed_root)

            # 4. Update UI
            self.msg_output.setPlainText(decoded_text)
            self.tree_widget.set_tree(reconstructed_root, animate=True)

            telemetry = (
                f"Recovered Characters: {len(decoded_text):,}\n"
                f"UTF-8 Bytes: {len(decoded_text.encode('utf-8')):,}\n"
                f"Payload Bits: {len(payload_bits):,} bits\n"
                f"Tree Header: {len(tree_bits):,} bits\n"
                f"Total Extracted Bitstream: {len(tree_bits) + len(payload_bits) + 64:,} bits"
            )
            self.telemetry_lbl.setText(telemetry)

            QMessageBox.information(
                self, "Extraction Verified",
                f"Successfully extracted {len(decoded_text):,} characters from carrier."
            )
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"Failed to extract payload: {str(e)}")

    def _copy_to_clipboard(self):
        text = self.msg_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Clipboard", "Payload copied to clipboard.")
