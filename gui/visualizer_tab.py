"""
gui/visualizer_tab.py
Interactive Step-by-Step Priority Queue & Tree Construction Sandbox
"""

from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QSlider,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from core.huffman import HuffmanEngine, HuffmanNode
from .tree_widget import AnimatedTreeWidget


class VisualizerTab(QWidget):
    """Educational visualizer for stepping through the Greedy algorithm."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = HuffmanEngine()
        self.current_step_idx: int = 0
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._on_timer_tick)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # --- Top Input Bar ---
        top_bar = QHBoxLayout()
        lbl = QLabel("Input Text / Alphabet:")
        lbl.setStyleSheet("font-weight: 600;")
        self.text_input = QLineEdit("ICE245 ALGORITHMS")
        self.text_input.setPlaceholderText("Enter text to simulate min-heap merges...")
        self.btn_build = QPushButton("Build Tree")
        self.btn_build.clicked.connect(self._build_tree)

        top_bar.addWidget(lbl)
        top_bar.addWidget(self.text_input, stretch=1)
        top_bar.addWidget(self.btn_build)
        main_layout.addLayout(top_bar)

        # Quick preset buttons (De-AI-ified)
        preset_bar = QHBoxLayout()
        preset_lbl = QLabel("Presets:")
        preset_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        preset_bar.addWidget(preset_lbl)

        for text_example in ["ABRACADABRA", "GREEDY CHOICE", "আমাদের অ্যালগরিদম", "ICE245 BENCHMARK"]:
            btn = QPushButton(text_example)
            btn.setObjectName("secondaryBtn")
            btn.setFixedHeight(24)
            btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
            btn.clicked.connect(lambda checked, t=text_example: self._load_preset(t))
            preset_bar.addWidget(btn)
        preset_bar.addStretch()
        main_layout.addLayout(preset_bar)

        # --- Middle Splitter: Tree Canvas (Left) + Queue / Codebook (Right) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree Canvas
        tree_card = QGroupBox("Greedy Priority Queue Tree Assembly")
        tree_layout = QVBoxLayout(tree_card)
        tree_layout.setContentsMargins(4, 4, 4, 4)
        self.tree_canvas = AnimatedTreeWidget()
        tree_layout.addWidget(self.tree_canvas)
        splitter.addWidget(tree_card)

        # Right Panel: Priority Queue & Code Table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Priority Queue State Card
        pq_group = QGroupBox("Priority Queue (Min-Heap State)")
        pq_layout = QVBoxLayout(pq_group)
        self.pq_status_lbl = QLabel("Min-heap awaiting build initialization...")
        self.pq_status_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: Consolas;")
        self.pq_status_lbl.setWordWrap(True)
        pq_layout.addWidget(self.pq_status_lbl)
        right_layout.addWidget(pq_group, stretch=1)

        # Code Table Card
        code_group = QGroupBox("Variable-Length Prefix Codebook")
        code_layout = QVBoxLayout(code_group)
        self.code_table = QTableWidget(0, 4)
        self.code_table.setHorizontalHeaderLabels(["Byte", "Symbol", "Prefix Code", "Bits"])
        self.code_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        code_layout.addWidget(self.code_table)
        right_layout.addWidget(code_group, stretch=2)

        splitter.addWidget(right_panel)
        splitter.setSizes([720, 340])
        main_layout.addWidget(splitter, stretch=1)

        # --- Bottom Control Toolbar ---
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(8)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("secondaryBtn")
        self.btn_reset.clicked.connect(self._step_reset)

        self.btn_prev = QPushButton("Prev Step")
        self.btn_prev.setObjectName("secondaryBtn")
        self.btn_prev.clicked.connect(self._step_prev)

        self.btn_play = QPushButton("Play Simulation")
        self.btn_play.clicked.connect(self._toggle_play)

        self.btn_next = QPushButton("Next Step")
        self.btn_next.setObjectName("secondaryBtn")
        self.btn_next.clicked.connect(self._step_next)

        self.btn_end = QPushButton("Final Tree")
        self.btn_end.setObjectName("secondaryBtn")
        self.btn_end.clicked.connect(self._step_end)

        ctrl_bar.addWidget(self.btn_reset)
        ctrl_bar.addWidget(self.btn_prev)
        ctrl_bar.addWidget(self.btn_play)
        ctrl_bar.addWidget(self.btn_next)
        ctrl_bar.addWidget(self.btn_end)

        # Speed Slider
        ctrl_bar.addSpacing(16)
        speed_lbl = QLabel("Interval:")
        speed_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        ctrl_bar.addWidget(speed_lbl)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(200, 2000)
        self.speed_slider.setValue(700)
        self.speed_slider.setFixedWidth(110)
        self.speed_slider.valueChanged.connect(self._update_speed)
        ctrl_bar.addWidget(self.speed_slider)

        self.step_counter_lbl = QLabel("Step 0 / 0")
        self.step_counter_lbl.setStyleSheet("font-weight: 700; color: #38BDF8; padding-left: 8px; font-family: Consolas;")
        ctrl_bar.addWidget(self.step_counter_lbl)

        main_layout.addLayout(ctrl_bar)

        # Initial build
        self._build_tree()

    def _load_preset(self, text: str):
        self.text_input.setText(text)
        self._build_tree()

    def _build_tree(self):
        text = self.text_input.text().strip()
        if not text:
            return

        self.play_timer.stop()
        self.btn_play.setText("Play Simulation")

        self.engine.build_tree_from_bytes(text.encode("utf-8"))
        self.current_step_idx = len(self.engine.build_history) - 1

        self._render_current_step(animate=False)
        self._populate_code_table()

    def _render_current_step(self, animate: bool = True):
        total_steps = len(self.engine.build_history)
        if total_steps == 0:
            return

        step_info = self.engine.build_history[self.current_step_idx]
        self.step_counter_lbl.setText(f"Step {self.current_step_idx} / {total_steps - 1}")

        # Update animation duration based on speed slider
        interval_ms = self.speed_slider.value()
        self.tree_canvas.anim_duration = min(0.38, max(0.12, (interval_ms / 1000.0) * 0.70))

        remaining = step_info.get("remaining", [])
        queue_tokens = [f"{item['label']}" for item in remaining]
        self.pq_status_lbl.setText(
            f"<b>Greedy Step Action:</b><br>{step_info['description']}<br><br>"
            f"<b>Min-Heap Priority Queue ({len(remaining)} elements):</b><br>" +
            "  →  ".join(queue_tokens[:12]) + ("..." if len(queue_tokens) > 12 else "")
        )

        if self.current_step_idx == total_steps - 1:
            self.tree_canvas.set_tree(self.engine.root, animate=animate)
        else:
            forest = step_info.get("forest", [])
            active_merged = step_info.get("active_merged")
            popped = step_info.get("popped")
            self.tree_canvas.set_forest(forest, active_merged=active_merged, popped=popped, animate=animate)

    def _populate_code_table(self):
        rows = self.engine.get_code_table_display()
        self.code_table.setRowCount(len(rows))
        for r, item in enumerate(rows):
            self.code_table.setItem(r, 0, QTableWidgetItem(f"0x{item['byte']:02X}"))
            self.code_table.setItem(r, 1, QTableWidgetItem(item['char']))
            self.code_table.setItem(r, 2, QTableWidgetItem(item['code']))
            self.code_table.setItem(r, 3, QTableWidgetItem(str(item['length'])))

    def _toggle_play(self):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.btn_play.setText("Play Simulation")
        else:
            if self.current_step_idx >= len(self.engine.build_history) - 1:
                self.current_step_idx = 0
                self._render_current_step(animate=False)
            self.play_timer.start(self.speed_slider.value())
            self.btn_play.setText("Pause")

    def _update_speed(self, val):
        if self.play_timer.isActive():
            self.play_timer.setInterval(val)

    def _on_timer_tick(self):
        if self.current_step_idx < len(self.engine.build_history) - 1:
            self.current_step_idx += 1
            self._render_current_step(animate=True)
        else:
            self.play_timer.stop()
            self.btn_play.setText("Play Simulation")

    def _step_next(self):
        if self.current_step_idx < len(self.engine.build_history) - 1:
            self.current_step_idx += 1
            self._render_current_step(animate=True)

    def _step_prev(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self._render_current_step(animate=True)

    def _step_reset(self):
        self.play_timer.stop()
        self.btn_play.setText("Play Simulation")
        self.current_step_idx = 0
        self._render_current_step(animate=False)

    def _step_end(self):
        self.play_timer.stop()
        self.btn_play.setText("Play Simulation")
        self.current_step_idx = len(self.engine.build_history) - 1
        self._render_current_step(animate=True)
