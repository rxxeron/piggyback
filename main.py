"""
main.py
Application Entry Point for HuffStego
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow


def main():
    # High-DPI attributes are handled automatically in PyQt6
    app = QApplication(sys.argv)
    app.setApplicationName("HuffStego")
    app.setOrganizationName("ICE245")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
