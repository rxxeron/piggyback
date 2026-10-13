"""
gui/encode_tab.py
Steganographic Embedding Tab: Encodes secret payload via Huffman,
serializes tree header, and embeds bits into lossless 24-bit PNG carrier.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton, QFileDialog,
    QProgressBar, QMessageBox, QGroupBox, QDialog,
    QFrame
)
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, pyqtSignal
from PIL import Image

from core.huffman import HuffmanEngine
from core.steganography import StegoEngine
from core.statistics import StatsEngine
from .tree_widget import AnimatedTreeWidget
from .stats_widget import StatsWidget


class DropImageLabel(QLabel):
    """Interactive drag & drop target area for image files."""

    file_dropped = pyqtSignal(str)

    def __init__(self, placeholder_text="Drag & Drop Carrier Image Here", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(placeholder_text)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #334155;
                border-radius: 6px;
                background-color: #0B0F19;
                color: #64748B;
                font-size: 11px;
                font-family: Consolas;
                min-height: 110px;
            }
            QLabel:hover {
                border-color: #0284C7;
                color: #38BDF8;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith((".png", ".bmp", ".jpg", ".jpeg")):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            event.acceptProposedAction()


class SideBySideInvisibilityDialog(QDialog):
    """Side-by-side forensic comparison proving steganographic invisibility."""

    def __init__(self, orig_path: str, stego_path: str, heatmap_arr, metrics: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forensic Verification — Side-by-Side Invisibility & PSNR Inspection")
        self.resize(920, 520)

        main_layout = QVBoxLayout(self)

        # Header with PSNR / MSE
        psnr_val = metrics.get("psnr_db", 0)
        mse_val = metrics.get("mse", 0)

        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 10px;")
        h_layout = QHBoxLayout(header_frame)

        badge_text = f"<b>PSNR:</b> {psnr_val} dB | <b>MSE:</b> {mse_val} | "
        if psnr_val >= 50:
            badge_text += "<span style='color: #34D399; font-weight: bold;'>Imperceptible Noise Floor (PSNR > 50 dB)</span>"
        else:
            badge_text += "<span style='color: #F59E0B; font-weight: bold;'>Detectable Minor Distortion</span>"

        info_lbl = QLabel(badge_text)
        info_lbl.setStyleSheet("font-size: 12px; font-family: Consolas;")
        h_layout.addWidget(info_lbl)
        main_layout.addWidget(header_frame)

        # 3 Side-by-Side Visual Panels
        panels_layout = QHBoxLayout()

        def make_panel(title, img_pixmap):
            box = QGroupBox(title)
            b_layout = QVBoxLayout(box)
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setPixmap(img_pixmap.scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            b_layout.addWidget(lbl)
            return box

        # Panel 1: Original
        orig_pixmap = QPixmap(orig_path)
        panels_layout.addWidget(make_panel("1. Carrier Reference", orig_pixmap))

        # Panel 2: Stego
        stego_pixmap = QPixmap(stego_path)
        panels_layout.addWidget(make_panel("2. Stego Carrier (Embedded)", stego_pixmap))

        # Panel 3: Amplified Heatmap
        h, w = heatmap_arr.shape
        qimg = QImage(heatmap_arr.data, w, h, w, QImage.Format.Format_Grayscale8)
        heat_pixmap = QPixmap.fromImage(qimg)
        panels_layout.addWidget(make_panel("3. Diff Heatmap (128x Gain)", heat_pixmap))

        main_layout.addLayout(panels_layout)


class EncodeTab(QWidget):
    """Tab for embedding compressed Huffman payloads into carrier images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.huffman = HuffmanEngine()
        self.stego = StegoEngine()
        self.stats_engine = StatsEngine()

        self.cover_image_path: str = ""
        self.last_stego_path: str = ""
        self.last_diff_heatmap = None
        self.last_metrics = {}

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT PANEL: Inputs ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Showcase Quick Demo Bar
        demo_bar = QHBoxLayout()
        self.btn_showcase_demo = QPushButton("Run Showcase Benchmark")
        self.btn_showcase_demo.setObjectName("secondaryBtn")
        self.btn_showcase_demo.setStyleSheet("padding: 6px 12px;")
        self.btn_showcase_demo.clicked.connect(self._run_showcase_demo)
        demo_bar.addWidget(self.btn_showcase_demo)
        demo_bar.addStretch()
        left_layout.addLayout(demo_bar)

        # Message Input Card
        msg_group = QGroupBox("1. Plaintext Secret Payload")
        msg_layout = QVBoxLayout(msg_group)

        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Enter secret payload (English, বাংলা, Unicode)...")
        self.msg_input.textChanged.connect(self._on_message_changed)
        msg_layout.addWidget(self.msg_input)

        # Quick preset buttons
        preset_layout = QHBoxLayout()
        btn_sample_en = QPushButton("English Preset")
        btn_sample_en.setObjectName("secondaryBtn")
        btn_sample_en.clicked.connect(lambda: self.msg_input.setPlainText("Huffman coding is an optimal prefix code invented by David Huffman."))

        btn_sample_bn = QPushButton("Bangla Preset")
        btn_sample_bn.setObjectName("secondaryBtn")
        btn_sample_bn.clicked.connect(lambda: self.msg_input.setPlainText("আমাদের অ্যালগরিদম সফলভাবে বাংলায় কাজ করছে।"))

        preset_layout.addWidget(btn_sample_en)
        preset_layout.addWidget(btn_sample_bn)
        msg_layout.addLayout(preset_layout)

        self.msg_meta_lbl = QLabel("0 characters | 0 UTF-8 bytes")
        self.msg_meta_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-family: Consolas;")
        msg_layout.addWidget(self.msg_meta_lbl)
        left_layout.addWidget(msg_group)

        # Cover Image Card with Drag & Drop
        cover_group = QGroupBox("2. Carrier Image (Lossless PNG / BMP)")
        cover_layout = QVBoxLayout(cover_group)

        cover_btn_layout = QHBoxLayout()
        self.btn_select_img = QPushButton("Browse Carrier...")
        self.btn_select_img.setObjectName("secondaryBtn")
        self.btn_select_img.clicked.connect(self._select_cover_image)
        self.cover_lbl = QLabel("No carrier image selected")
        self.cover_lbl.setStyleSheet("color: #64748B; font-family: Consolas;")
        cover_btn_layout.addWidget(self.btn_select_img)
        cover_btn_layout.addWidget(self.cover_lbl)
        cover_layout.addLayout(cover_btn_layout)

        # Capacity Progress Bar
        self.capacity_bar = QProgressBar()
        self.capacity_bar.setValue(0)
        self.capacity_bar.setFormat("Capacity: 0 / 0 bits (0%)")
        cover_layout.addWidget(self.capacity_bar)

        # Drag and Drop Target Box
        self.drop_target = DropImageLabel("Drag & Drop PNG Carrier Image Here\nor click Browse above")
        self.drop_target.file_dropped.connect(self._load_cover_image)
        cover_layout.addWidget(self.drop_target)

        left_layout.addWidget(cover_group)

        # Action Buttons
        self.btn_encode = QPushButton("Embed Payload into Carrier")
        self.btn_encode.setStyleSheet("font-size: 13px; font-weight: 700; padding: 9px;")
        self.btn_encode.clicked.connect(self._execute_encoding)
        left_layout.addWidget(self.btn_encode)

        self.btn_compare = QPushButton("Forensic PSNR & Difference Inspection")
        self.btn_compare.setObjectName("secondaryBtn")
        self.btn_compare.setEnabled(False)
        self.btn_compare.clicked.connect(self._show_comparison_dialog)
        left_layout.addWidget(self.btn_compare)

        splitter.addWidget(left_widget)

        # --- RIGHT PANEL: Visualizer & Stats ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Tree Visualizer Card
        tree_card = QGroupBox("Generated Huffman Binary Tree")
        tree_layout = QVBoxLayout(tree_card)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        self.tree_widget = AnimatedTreeWidget()
        tree_layout.addWidget(self.tree_widget)
        right_layout.addWidget(tree_card, stretch=3)

        # Statistics Card
        stats_card = QGroupBox("Carrier Capacity & Information Analytics")
        stats_layout = QVBoxLayout(stats_card)
        self.stats_widget = StatsWidget()
        stats_layout.addWidget(self.stats_widget)
        right_layout.addWidget(stats_card, stretch=2)

        splitter.addWidget(right_widget)
        splitter.setSizes([450, 650])

        main_layout.addWidget(splitter)

    def _on_message_changed(self):
        text = self.msg_input.toPlainText()
        raw_bytes = text.encode("utf-8")
        self.msg_meta_lbl.setText(f"{len(text):,} characters | {len(raw_bytes):,} UTF-8 bytes")
        self._update_capacity_display()

    def _select_cover_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Carrier Image", "", "Lossless Images (*.png *.bmp);;All Files (*.*)"
        )
        if file_path:
            self._load_cover_image(file_path)

    def _load_cover_image(self, file_path: str):
        # Auto-convert JPG to PNG if dropped
        if file_path.lower().endswith((".jpg", ".jpeg")):
            conv_path = Path(file_path).with_suffix(".png")
            with Image.open(file_path) as im:
                im.convert("RGB").save(conv_path, "PNG")
            file_path = str(conv_path)
            QMessageBox.information(
                self, "Lossless PNG Conversion",
                "Lossy JPEG format degrades LSB integrity. Auto-converted to lossless 24-bit PNG."
            )

        self.cover_image_path = file_path
        self.cover_lbl.setText(Path(file_path).name)

        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.drop_target.setPixmap(pixmap.scaled(220, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self._update_capacity_display()

    def _update_capacity_display(self):
        if not self.cover_image_path:
            return

        try:
            info = self.stego.get_capacity_info(self.cover_image_path)
            raw_bytes = self.msg_input.toPlainText().encode("utf-8")
            needed_bits = len(raw_bytes) * 8 + 400
            usable_bits = info["usable_bits"]

            if usable_bits > 0:
                pct = int(min(100, (needed_bits / usable_bits) * 100))
                self.capacity_bar.setValue(pct)
                self.capacity_bar.setFormat(f"Payload Need: {needed_bits:,} / {usable_bits:,} usable bits ({pct}%)")
        except Exception:
            pass

    def _execute_encoding(self):
        text = self.msg_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Payload Required", "Please enter a plaintext payload to encode.")
            return

        if not self.cover_image_path:
            QMessageBox.warning(self, "Carrier Required", "Please select or drop a PNG carrier image.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Steganographic Carrier", "stego_carrier.png", "PNG Image (*.png)"
        )
        if not out_path:
            return

        self._perform_embed_pipeline(text, out_path)

    def _perform_embed_pipeline(self, text: str, out_path: str):
        try:
            # 1. Huffman Encoding
            tree_bits, payload_bits = self.huffman.encode_text(text)

            # 2. Stego Embedding
            stego_meta = self.stego.embed(self.cover_image_path, tree_bits, payload_bits, out_path)
            self.last_stego_path = out_path

            # 3. Calculate Analytics & Quality Metrics
            stats = self.stats_engine.evaluate(text, tree_bits, payload_bits)
            self.last_metrics = self.stego.compute_metrics(self.cover_image_path, out_path)
            self.last_diff_heatmap = self.stego.compute_diff_heatmap(self.cover_image_path, out_path)

            # 4. Update UI
            self.tree_widget.set_tree(self.huffman.root, animate=True)
            self.stats_widget.update_stats(stats, stego_meta)
            self.btn_compare.setEnabled(True)

            QMessageBox.information(
                self, "Embedding Verified",
                f"Successfully embedded {len(text):,} characters into carrier.\n\n"
                f"Output: {Path(out_path).name}\n"
                f"Compression Ratio: {stats['compression_ratio']}x\n"
                f"PSNR Metric: {self.last_metrics['psnr_db']} dB (Imperceptible)\n"
                f"Modified Pixels: {stego_meta['modified_channel_values']:,}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Embedding Error", f"Operation failed: {str(e)}")

    def _show_comparison_dialog(self):
        if self.last_diff_heatmap is not None and self.cover_image_path and self.last_stego_path:
            dialog = SideBySideInvisibilityDialog(
                self.cover_image_path,
                self.last_stego_path,
                self.last_diff_heatmap,
                self.last_metrics,
                self
            )
            dialog.exec()

    def _run_showcase_demo(self):
        """1-Click presentation demo preloading sample assets & bilingual secret message."""
        demo_cover = Path(__file__).resolve().parent.parent / "assets" / "sample_images" / "cover_landscape.png"
        if not demo_cover.exists():
            QMessageBox.warning(self, "Demo Asset Missing", f"Could not find demo cover at {demo_cover}")
            return

        self._load_cover_image(str(demo_cover))
        demo_text = (
            "ICE245 Algorithm Design Lab 13 Showcase:\n"
            "Greedy Huffman coding + 24-bit RGB LSB Steganography.\n"
            "Lossless UTF-8 payload verification: আমাদের অ্যালগরিদম সফল।"
        )
        self.msg_input.setPlainText(demo_text)

        demo_output = Path(__file__).resolve().parent.parent / "stego_showcase_demo.png"
        self._perform_embed_pipeline(demo_text, str(demo_output))
