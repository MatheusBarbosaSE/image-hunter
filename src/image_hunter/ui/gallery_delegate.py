from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QPixmap
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
    QStyle,
)



class GalleryDelegate(QStyledItemDelegate):
    """Custom tile renderer for the gallery: image + overlays (author/source, license badge)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.padding = 8
        self.badge_pad = 6
        self.caption_h = 28
        self.radius = 8

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        r = option.rect.adjusted(4, 4, -4, -4)

        # Background card
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("#22262B")))
        painter.setBrush(QColor("#161A1E"))
        painter.drawRoundedRect(r, self.radius, self.radius)

        # Extract icon pixmap (set by our loader) and model payload (UserRole)
        data = index.data(Qt.UserRole)
        icon = index.data(Qt.DecorationRole)

        # Draw image area
        img_rect = QRect(r.left() + self.padding, r.top() + self.padding,
                         r.width() - 2 * self.padding, r.height() - self.caption_h - 2 * self.padding)
        if isinstance(icon, QIcon):
            px = icon.pixmap(img_rect.size())
        elif isinstance(icon, QPixmap):
            px = icon.scaled(img_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            px = QPixmap()
        if not px.isNull():
            target = self._centered_rect(img_rect, px.size())
            painter.drawPixmap(target, px)

        # License badge (top-left)
        if data is not None:
            badge = getattr(data, "license_badge")() if hasattr(data, "license_badge") else ""
            if badge:
                self._draw_badge(painter, r.left() + self.badge_pad, r.top() + self.badge_pad, badge)

        # Caption strip (bottom)
        painter.setBrush(QColor(0, 0, 0, 90))
        painter.setPen(Qt.NoPen)
        cap_rect = QRect(r.left(), r.bottom() - self.caption_h, r.width(), self.caption_h)
        painter.drawRect(cap_rect)

        # Text: author — source
        painter.setPen(QColor("#D7DBDF"))
        painter.setFont(QFont("Segoe UI", 9))
        if data is not None:
            author = getattr(data, "author", "") or "—"
            source = (getattr(getattr(data, "source", None), "name", "") or "").title()
            text = f"{author} — {source}" if source else author
        else:
            text = "—"
        text_rect = cap_rect.adjusted(self.padding, 0, -self.padding, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.TextSingleLine, text)

        # Selection outline
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor("#2FB5B5"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(r, self.radius, self.radius)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        # Tile size (including padding, caption, and card)
        return QSize(170, 190)

    def _centered_rect(self, bounds: QRect, size: QSize) -> QRect:
        x = bounds.x() + (bounds.width() - size.width()) // 2
        y = bounds.y() + (bounds.height() - size.height()) // 2
        return QRect(x, y, size.width(), size.height())

    def _draw_badge(self, painter: QPainter, x: int, y: int, text: str) -> None:
        pad_x, pad_y = 8, 4
        painter.setFont(QFont("Segoe UI", 8, QFont.Medium))
        metrics = painter.fontMetrics()
        w = metrics.horizontalAdvance(text) + pad_x * 2
        h = metrics.height() + pad_y * 2
        painter.setBrush(QColor("#2FB5B5"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRect(x, y, w, h), 8, 8)
        painter.setPen(QColor("#0E1414"))
        painter.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
