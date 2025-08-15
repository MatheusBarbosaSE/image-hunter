from __future__ import annotations

from typing import Callable, Optional, Iterable
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from .models import ImageItem


def clear_gallery(widget: QListWidget) -> None:
    """Remove all items from the gallery list."""
    widget.clear()


def _placeholder_icon(text: str, size: int = 128) -> QIcon:
    """Create a simple square placeholder pixmap used as an icon."""
    px = QPixmap(size, size)
    px.fill(QColor("#1A1F24"))
    painter = QPainter(px)
    painter.setPen(QColor("#2FB5B5"))
    painter.setFont(QFont("Segoe UI", 10))
    painter.drawRect(2, 2, size - 4, size - 4)
    painter.drawText(px.rect(), Qt.AlignCenter, text)
    painter.end()
    return QIcon(px)


def render_items(widget: QListWidget, items: Iterable[ImageItem]) -> None:
    """
    Render ImageItem tiles into the gallery.
    - Sets a placeholder icon (real thumbnails come later).
    - Stores the ImageItem in UserRole so the UI can read it on selection.
    """
    widget.setIconSize(QSize(128, 128))
    for it in items:
        li = QListWidgetItem()
        li.setText(it.title or "—")
        li.setToolTip(it.tooltip_text())
        li.setIcon(_placeholder_icon(it.license_badge()))
        li.setData(Qt.UserRole, it)
        widget.addItem(li)


def bind_selection_changed(widget: QListWidget, callback: Callable[[Optional[ImageItem]], None]) -> None:
    """Call `callback(ImageItem|None)` whenever the current selection changes."""
    def _on_change(cur: QListWidgetItem, _prev: QListWidgetItem) -> None:
        payload = cur.data(Qt.UserRole) if cur is not None else None
        callback(payload)
    widget.currentItemChanged.connect(_on_change)
