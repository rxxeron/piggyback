"""
gui/styles.py
High-Contrast Technical Slate Dark Theme for HuffStego Engineering Workbench
Inspired by JetBrains, Wireshark, and Qt Creator. Zero AI-aesthetic artifacts.
"""

MODERN_STYLE = """
/* Global Window & Typography */
QMainWindow, QDialog {
    background-color: #0F172A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #F8FAFC;
}

QWidget {
    font-size: 13px;
    color: #F8FAFC;
    background-color: transparent;
}

/* Tab Bar */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #0F172A;
    top: -1px;
}

QTabBar::tab {
    background-color: #1E293B;
    color: #94A3B8;
    border: 1px solid #334155;
    border-bottom: none;
    padding: 8px 20px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #0F172A;
    color: #38BDF8;
    border-top: 2px solid #0284C7;
    border-bottom: 1px solid #0F172A;
}

QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: #E2E8F0;
}

/* Push Buttons */
QPushButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #0369A1;
    border-radius: 4px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #0369A1;
}

QPushButton:pressed {
    background-color: #075985;
}

QPushButton:disabled {
    background-color: #1E293B;
    color: #475569;
    border: 1px solid #334155;
}

QPushButton#secondaryBtn {
    background-color: #1E293B;
    color: #CBD5E1;
    border: 1px solid #334155;
}

QPushButton#secondaryBtn:hover {
    background-color: #334155;
    color: #FFFFFF;
    border: 1px solid #475569;
}

QPushButton#successBtn {
    background-color: #059669;
    color: #FFFFFF;
    border: 1px solid #047857;
}

QPushButton#successBtn:hover {
    background-color: #047857;
}

/* Group Boxes / Workbench Cards */
QGroupBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 600;
    color: #E2E8F0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #38BDF8;
    font-size: 12px;
    font-weight: 700;
}

/* Monospace Inputs & Editors */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0B0F19;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 6px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #E2E8F0;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #38BDF8;
}

/* Data Tables */
QTableWidget {
    background-color: #0B0F19;
    border: 1px solid #334155;
    border-radius: 4px;
    gridline-color: #1E293B;
    color: #E2E8F0;
    font-family: "Consolas", monospace;
    font-size: 11px;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #334155;
    font-weight: 600;
    font-size: 11px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Splitters */
QSplitter::handle {
    background-color: #334155;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #334155;
    height: 4px;
    background: #0B0F19;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #0284C7;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #38BDF8;
    border: 1px solid #0284C7;
    width: 12px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 6px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0B0F19;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar:horizontal {
    border: none;
    background: #0B0F19;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 20px;
    border-radius: 4px;
}

/* Menus & Toolbars */
QMenuBar {
    background-color: #0F172A;
    border-bottom: 1px solid #334155;
    color: #E2E8F0;
    font-size: 12px;
}

QMenuBar::item:selected {
    background-color: #1E293B;
    color: #38BDF8;
}

QMenu {
    background-color: #1E293B;
    border: 1px solid #334155;
    color: #E2E8F0;
}

QMenu::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background: #334155;
    margin: 4px 0;
}

/* Status Bar */
QStatusBar {
    background-color: #0B0F19;
    border-top: 1px solid #334155;
    color: #64748B;
    font-family: Consolas, monospace;
    font-size: 11px;
}
"""
