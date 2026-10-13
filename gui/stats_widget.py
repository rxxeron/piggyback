"""
gui/stats_widget.py
Statistics & Information Theory Metrics Dashboard Widget
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt


class StatCard(QFrame):
    """Clean metric card with a title, primary value, and subtitle."""

    def __init__(self, title: str, initial_value: str = "-", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0B0F19;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748B; font-family: Consolas;")

        self.val_lbl = QLabel(initial_value)
        self.val_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #38BDF8; font-family: Consolas;")

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-family: Consolas;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)

    def set_value(self, val: str, subtitle: str = None):
        self.val_lbl.setText(val)
        if subtitle is not None:
            self.sub_lbl.setText(subtitle)


class StatsWidget(QWidget):
    """Container holding metric cards and symbol distribution table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 2x2 Grid of Cards
        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)

        self.card_ratio = StatCard("Compression Ratio", "-", "Original / Stego Bits")
        self.card_savings = StatCard("Space Savings", "-", "Payload size reduction")
        self.card_entropy = StatCard("Shannon Entropy", "-", "Theoretical bound (b/B)")
        self.card_efficiency = StatCard("Shannon Efficiency", "-", "Greedy optimality")

        cards_grid.addWidget(self.card_ratio, 0, 0)
        cards_grid.addWidget(self.card_savings, 0, 1)
        cards_grid.addWidget(self.card_entropy, 1, 0)
        cards_grid.addWidget(self.card_efficiency, 1, 1)

        main_layout.addLayout(cards_grid)

        # Summary details text
        self.details_lbl = QLabel("Awaiting compression execution.")
        self.details_lbl.setStyleSheet("font-size: 11px; color: #94A3B8; font-family: Consolas; line-height: 1.4;")
        self.details_lbl.setWordWrap(True)
        main_layout.addWidget(self.details_lbl)

        # Top symbols table
        self.sym_table = QTableWidget(0, 4)
        self.sym_table.setHorizontalHeaderLabels(["Byte", "Symbol", "Count", "Frequency"])
        self.sym_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sym_table.setMaximumHeight(140)
        main_layout.addWidget(self.sym_table)

    def update_stats(self, stats: dict, stego_meta: dict = None):
        """Populates cards and table with computed statistical report."""
        ratio = stats.get("compression_ratio", 0)
        savings = stats.get("space_savings_pct", 0)
        entropy = stats.get("shannon_entropy", 0)
        efficiency = stats.get("shannon_efficiency_pct", 0)

        self.card_ratio.set_value(f"{ratio}x", f"{stats.get('total_stego_bits', 0):,} bits total")
        self.card_savings.set_value(f"{savings}%", f"{stats.get('uncompressed_bits', 0):,} orig bits")
        self.card_entropy.set_value(f"{entropy:.2f} b/B", f"Actual: {stats.get('avg_bits_per_symbol', 0):.2f} b/B")
        self.card_efficiency.set_value(f"{efficiency:.1f}%", "Greedy optimality")

        details = (
            f"Payload: {stats.get('character_count', 0):,} chars ({stats.get('byte_count', 0):,} UTF-8 bytes) | "
            f"Alphabet: {stats.get('unique_symbols', 0)} symbols | "
            f"Header: {stats.get('tree_overhead_bits', 0)} bits"
        )
        if stego_meta:
            details += f"\nCarrier Usage: {stego_meta.get('capacity_usage_pct', 0)}% ({stego_meta.get('modified_channel_values', 0):,} pixels modified)"

        self.details_lbl.setText(details)

        # Populate top symbols
        top_symbols = stats.get("top_symbols", [])
        self.sym_table.setRowCount(len(top_symbols))
        for row, item in enumerate(top_symbols):
            b_val = item["byte"]
            sym = item["repr"]
            cnt = item["count"]
            freq = f"{item['frequency_pct']}%"

            self.sym_table.setItem(row, 0, QTableWidgetItem(f"0x{b_val:02X}"))
            self.sym_table.setItem(row, 1, QTableWidgetItem(sym))
            self.sym_table.setItem(row, 2, QTableWidgetItem(str(cnt)))
            self.sym_table.setItem(row, 3, QTableWidgetItem(freq))
