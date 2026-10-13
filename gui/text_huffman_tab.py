"""
gui/text_huffman_tab.py
Pure Textbook Huffman Coding Tab (Text In -> Bits Out -> Text Out)
Designed specifically for ICE245 Lab 4 (Standard Greedy Huffman Requirements).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt

from core.huffman import HuffmanEngine
from core.statistics import StatsEngine
from .tree_widget import AnimatedTreeWidget
from .stats_widget import StatsWidget


class TextHuffmanTab(QWidget):
    """
    Standard textbook Huffman coding interface.
    Separates pure algorithmic text compression from image steganography.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = HuffmanEngine()
        self.stats_engine = StatsEngine()
        self.last_encoded_bits = ""
        self.last_tree_bits = ""

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ==========================================
        # LEFT PANEL: Text Encoding & Decoding
        # ==========================================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # 1. Plain Text Input Card
        input_group = QGroupBox("1. Input Plaintext Payload")
        input_layout = QVBoxLayout(input_group)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text for Huffman compression...")
        self.text_input.setPlainText("BEEP BOOP BEER! Huffman coding achieves optimal prefix codes.")
        self.text_input.textChanged.connect(self._on_input_changed)
        input_layout.addWidget(self.text_input)

        # Presets
        preset_bar = QHBoxLayout()
        for label, txt in [
            ("Textbook", "ABRACADABRA"),
            ("Greedy Property", "The greedy choice property ensures optimal prefix codes."),
            ("Bangla Script", "আমাদের অ্যালগরিদম সফলভাবে বাংলায় কাজ করছে।")
        ]:
            btn = QPushButton(label)
            btn.setObjectName("secondaryBtn")
            btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
            btn.clicked.connect(lambda ch, t=txt: self.text_input.setPlainText(t))
            preset_bar.addWidget(btn)
        preset_bar.addStretch()
        input_layout.addLayout(preset_bar)

        self.input_meta_lbl = QLabel("Length: 0 chars | UTF-8: 0 bytes")
        self.input_meta_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-family: Consolas;")
        input_layout.addWidget(self.input_meta_lbl)

        btn_encode = QPushButton("Compress (Encode Payload → Bitstream)")
        btn_encode.setStyleSheet("font-size: 12px; font-weight: 700; padding: 8px;")
        btn_encode.clicked.connect(self._execute_encode)
        input_layout.addWidget(btn_encode)

        left_layout.addWidget(input_group)

        # 2. Huffman Bitstream Output & Decoder
        output_group = QGroupBox("2. Huffman Encoded Bitstream [0/1 Payload]")
        output_layout = QVBoxLayout(output_group)

        self.bits_output = QTextEdit()
        self.bits_output.setPlaceholderText("Compressed binary bitstream will appear here...")
        output_layout.addWidget(self.bits_output)

        bits_btn_bar = QHBoxLayout()
        btn_copy_bits = QPushButton("Copy Bitstream")
        btn_copy_bits.setObjectName("secondaryBtn")
        btn_copy_bits.clicked.connect(self._copy_bitstream)

        btn_decode = QPushButton("Decompress (Decode Bitstream → Text)")
        btn_decode.setStyleSheet("background-color: #059669; color: white; font-weight: 700;")
        btn_decode.clicked.connect(self._execute_decode)

        bits_btn_bar.addWidget(btn_copy_bits)
        bits_btn_bar.addWidget(btn_decode)
        output_layout.addLayout(bits_btn_bar)

        # Decoded Output Banner
        self.decoded_text_lbl = QLabel("Decoded Text: [Ready for decompression]")
        self.decoded_text_lbl.setStyleSheet(
            "font-size: 12px; font-family: Consolas; color: #94A3B8; background: #0B0F19; "
            "padding: 8px; border: 1px solid #334155; border-radius: 4px;"
        )
        self.decoded_text_lbl.setWordWrap(True)
        output_layout.addWidget(self.decoded_text_lbl)

        left_layout.addWidget(output_group)
        splitter.addWidget(left_widget)

        # ==========================================
        # RIGHT PANEL: Tree, Codebook & Stats
        # ==========================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Huffman Tree Canvas
        tree_card = QGroupBox("Reconstructed Huffman Prefix Tree")
        tree_layout = QVBoxLayout(tree_card)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        self.tree_canvas = AnimatedTreeWidget()
        tree_layout.addWidget(self.tree_canvas)
        right_layout.addWidget(tree_card, stretch=3)

        # Codebook Table & Stats in Splitter
        lower_right = QHBoxLayout()

        # Codebook
        code_card = QGroupBox("Prefix-Free Codebook")
        code_layout = QVBoxLayout(code_card)
        self.code_table = QTableWidget(0, 3)
        self.code_table.setHorizontalHeaderLabels(["Symbol", "Binary Code", "Bits"])
        self.code_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        code_layout.addWidget(self.code_table)
        lower_right.addWidget(code_card, stretch=2)

        # Stats Cards
        stats_card = QGroupBox("Information Bounds & Compression Metrics")
        stats_layout = QVBoxLayout(stats_card)
        self.stats_widget = StatsWidget()
        stats_layout.addWidget(self.stats_widget)
        lower_right.addWidget(stats_card, stretch=3)

        right_layout.addLayout(lower_right, stretch=2)
        splitter.addWidget(right_widget)

        splitter.setSizes([480, 680])
        main_layout.addWidget(splitter)

        # Initial trigger
        self._on_input_changed()
        self._execute_encode()

    def _on_input_changed(self):
        text = self.text_input.toPlainText()
        raw_bytes = text.encode("utf-8")
        self.input_meta_lbl.setText(f"Length: {len(text):,} chars | UTF-8: {len(raw_bytes):,} bytes")

    def _execute_encode(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return

        tree_bits, payload_bits = self.engine.encode_text(text)
        self.last_encoded_bits = payload_bits
        self.last_tree_bits = tree_bits

        self.bits_output.setPlainText(payload_bits)

        # Update Tree Canvas (with smooth auto-fit)
        self.tree_canvas.set_tree(self.engine.root, animate=True)

        # Update Codebook Table
        rows = self.engine.get_code_table_display()
        self.code_table.setRowCount(len(rows))
        for r, item in enumerate(rows):
            self.code_table.setItem(r, 0, QTableWidgetItem(item["char"]))
            self.code_table.setItem(r, 1, QTableWidgetItem(item["code"]))
            self.code_table.setItem(r, 2, QTableWidgetItem(str(item["length"])))

        # Update Stats
        stats = self.stats_engine.evaluate(text, tree_bits, payload_bits)
        self.stats_widget.update_stats(stats)

    def _execute_decode(self):
        bits = self.bits_output.toPlainText().strip()
        if not bits:
            QMessageBox.warning(self, "No Bitstream", "Please enter or generate a bitstream to decode.")
            return

        if not self.engine.root:
            QMessageBox.warning(self, "No Huffman Tree", "No active tree found. Please encode a text first.")
            return

        try:
            decoded = self.engine.decode_to_text(bits, self.engine.root)
            self.decoded_text_lbl.setText(f"DECODED PAYLOAD: \"{decoded}\"")
            self.decoded_text_lbl.setStyleSheet(
                "font-size: 12px; font-family: Consolas; font-weight: 700; color: #34D399; "
                "background: #064E3B; padding: 8px; border: 1px solid #059669; border-radius: 4px;"
            )
        except Exception as e:
            self.decoded_text_lbl.setText(f"DECOMPRESSION ERROR: {str(e)}")
            self.decoded_text_lbl.setStyleSheet(
                "font-size: 12px; font-family: Consolas; font-weight: 700; color: #F87171; "
                "background: #450A0A; padding: 8px; border: 1px solid #DC2626; border-radius: 4px;"
            )

    def _copy_bitstream(self):
        bits = self.bits_output.toPlainText().strip()
        if bits:
            QApplication.clipboard().setText(bits)
            QMessageBox.information(self, "Clipboard", "Huffman bitstream copied to clipboard.")
