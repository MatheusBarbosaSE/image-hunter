from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QDesktopServices


class PreviewDialog(QDialog):
    """Simple image preview dialog (uses cached thumbnail for now)."""

    def __init__(self, parent, item, thumb_path: str | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(item.title or "Preview")
        self._item = item
        self._orig_pix = QPixmap(thumb_path) if thumb_path and Path(thumb_path).is_file() else QPixmap()
        self._img = QLabel(alignment=Qt.AlignCenter)
        self._img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Buttons
        btn_open = QPushButton("Open in source")
        btn_license = QPushButton("License page")
        btn_close = QPushButton("Close")

        btn_open.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(item.source_url)))
        btn_license.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(item.license_url)))
        btn_close.clicked.connect(self.accept)

        # Layout
        lay = QVBoxLayout(self)
        lay.addWidget(self._img, 1)

        bar = QHBoxLayout()
        bar.addStretch(1)
        bar.addWidget(btn_open)
        bar.addWidget(btn_license)
        bar.addWidget(btn_close)
        lay.addLayout(bar)

        self.resize(900, 700)
        self._rescale()

    def resizeEvent(self, ev) -> None:  # Scale on resize
        super().resizeEvent(ev)
        self._rescale()

    def _rescale(self) -> None:
        if not self._orig_pix.isNull():
            # Fit-to-window while preserving aspect ratio
            size = self._img.size().boundedTo(QSize(max(100, self.width()-40), max(100, self.height()-140)))
            self._img.setPixmap(self._orig_pix.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._img.setText("No preview available")
