from __future__ import annotations
"""Entry point for the desktop application.

Preferred way to run (from repo root):
    python run.py

After editable install, this also works:
    python -m image_hunter.app
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication


def _load_stylesheet(app: QApplication) -> None:
    # Load the dark theme QSS (optional)
    qss_path = Path(__file__).resolve().parents[2] / "assets" / "ui.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


from image_hunter.ui.main_window import MainWindow  # noqa: E402


def main() -> int:
    # Create the Qt application (UI event loop)
    app = QApplication(sys.argv)
    app.setApplicationName("Image Hunter")
    app.setOrganizationName("Image Hunter")
    _load_stylesheet(app)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Enter the event loop and return the exit code
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
