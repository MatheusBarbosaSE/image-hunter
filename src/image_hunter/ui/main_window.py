from __future__ import annotations

from PySide6.QtCore import Qt, QSettings, QUrl
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QListWidget, QListWidgetItem, QLabel,
    QGroupBox, QSplitter, QSizePolicy
)

from image_hunter.i18n.i18n import load, t, SUPPORTED
from image_hunter.core.gallery import clear_gallery, render_items, bind_selection_changed
from image_hunter.core.models import ImageItem
from image_hunter.core.mock_data import make_mock_items


class MainWindow(QMainWindow):
    """Main application window (i18n-aware)."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("Image Hunter", "Image Hunter")
        lang = self.settings.value("lang", "en")
        load(lang)

        self._is_placeholder_gallery = False
        self._current_item: ImageItem | None = None

        self._build_ui()
        self._apply_texts()
        self._build_language_menu(lang)

        # Bind selection for details updates
        bind_selection_changed(self.gallery, self._on_item_selected)

        self.statusBar().showMessage(
            t("status.results").format(n=0, scope=t("scope.pd"), ms=0)
        )

    # UI construction
    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Top bar
        top = QHBoxLayout()
        top.setSpacing(8)

        self.scope_pd = QRadioButton()
        self.scope_free = QRadioButton()
        self.scope_group = QButtonGroup(self)
        self.scope_group.addButton(self.scope_pd, 0)
        self.scope_group.addButton(self.scope_free, 1)
        self.scope_pd.setChecked(True)

        self.search_edit = QLineEdit()
        self.search_edit.setClearButtonEnabled(True)

        self.btn_search = QPushButton()
        self.btn_search.clicked.connect(self._on_search_clicked)
        self.search_edit.returnPressed.connect(self._on_search_clicked)

        top.addWidget(self.scope_pd, 0)
        top.addWidget(self.scope_free, 0)
        top.addWidget(self.search_edit, 1)
        top.addWidget(self.btn_search, 0)

        splitter = QSplitter(Qt.Horizontal, self)

        # Left: Filters
        self.grp_filters = QGroupBox()
        lay_filters = QVBoxLayout(self.grp_filters)
        lay_filters.setContentsMargins(12, 12, 12, 12)
        lay_filters.setSpacing(8)

        self.lbl_quality = QLabel()
        self.min_width = QLineEdit()
        self.orientation = QLineEdit()
        self.color = QLineEdit()

        lay_filters.addWidget(self.lbl_quality)
        lay_filters.addWidget(self.min_width)
        lay_filters.addWidget(self.orientation)
        lay_filters.addWidget(self.color)
        lay_filters.addStretch()

        # Center: Gallery
        self.grp_gallery = QGroupBox()
        lay_gallery = QVBoxLayout(self.grp_gallery)
        lay_gallery.setContentsMargins(12, 12, 12, 12)
        lay_gallery.setSpacing(8)

        self.gallery = QListWidget()
        self.gallery.setViewMode(QListWidget.IconMode)
        self.gallery.setResizeMode(QListWidget.Adjust)
        self.gallery.setMovement(QListWidget.Static)
        self.gallery.setSpacing(10)
        self.gallery.setUniformItemSizes(True)

        lay_gallery.addWidget(self.gallery)

        # Right: Details
        self.grp_details = QGroupBox()
        lay_details = QVBoxLayout(self.grp_details)
        lay_details.setContentsMargins(12, 12, 12, 12)
        lay_details.setSpacing(8)

        self.lbl_details_title = QLabel()
        self.lbl_details_source = QLabel()
        self.lbl_details_license = QLabel()
        self.lbl_details_dims = QLabel()
        self.lbl_links = QLabel()

        self.val_title = QLabel("—")
        self.val_source = QLabel("—")
        self.val_license = QLabel("—")
        self.val_dims = QLabel("—")

        self.btn_open_source = QPushButton()
        self.btn_open_license = QPushButton()
        self.btn_download = QPushButton()
        self.btn_copy_credit = QPushButton()

        self.btn_open_source.clicked.connect(self._action_open_source)
        self.btn_open_license.clicked.connect(self._action_open_license)
        self.btn_copy_credit.clicked.connect(self._action_copy_credit)
        # Download will be implemented later (thumbnail/full image pipeline)
        self.btn_download.setEnabled(False)

        for b in (self.btn_open_source, self.btn_open_license, self.btn_download, self.btn_copy_credit):
            b.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        lay_details.addWidget(self._labeled_value(self.lbl_details_title, self.val_title))
        lay_details.addWidget(self._labeled_value(self.lbl_details_source, self.val_source))
        lay_details.addWidget(self._labeled_value(self.lbl_details_license, self.val_license))
        lay_details.addWidget(self._labeled_value(self.lbl_details_dims, self.val_dims))
        lay_details.addSpacing(6)
        lay_details.addWidget(self._labeled_button(self.lbl_links, self.btn_open_source))
        lay_details.addWidget(self.btn_open_license)
        lay_details.addSpacing(6)
        lay_details.addWidget(self.btn_download)
        lay_details.addWidget(self.btn_copy_credit)
        lay_details.addStretch()

        splitter.addWidget(self.grp_filters)
        splitter.addWidget(self.grp_gallery)
        splitter.addWidget(self.grp_details)
        splitter.setSizes([260, 920, 340])

        root.addLayout(top)
        root.addWidget(splitter, 1)
        self.setCentralWidget(central)
        self.resize(1280, 800)

    # Helpers
    def _labeled_value(self, label_widget: QLabel, value_widget: QWidget) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(label_widget)
        v.addWidget(value_widget)
        return w

    def _labeled_button(self, label_widget: QLabel, button: QPushButton) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(label_widget)
        v.addWidget(button)
        return w

    # Language menu (exclusive)
    def _build_language_menu(self, current: str) -> None:
        self.lang_menu = self.menuBar().addMenu(t("menu.language"))
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)
        self._lang_actions: dict[str, QAction] = {}

        for code, label in SUPPORTED.items():
            act = QAction(label, self, checkable=True)
            act.setData(code)
            act.setChecked(code == current)
            self.lang_group.addAction(act)
            self.lang_menu.addAction(act)
            self._lang_actions[code] = act

        self.lang_group.triggered.connect(self._on_lang_triggered)

    def _on_lang_triggered(self, action: QAction) -> None:
        self._change_language(action.data())

    def _change_language(self, code: str) -> None:
        load(code)
        self.settings.setValue("lang", code)
        self._apply_texts()
        self.lang_menu.setTitle(t("menu.language"))

    # i18n application
    def _apply_texts(self) -> None:
        # Window & top bar
        self.setWindowTitle(t("app.title"))
        self.scope_pd.setText(t("scope.pd"))
        self.scope_free.setText(t("scope.free"))
        self.search_edit.setPlaceholderText(t("search.placeholder"))
        self.btn_search.setText(t("btn.search"))

        # Left
        self.grp_filters.setTitle(t("panel.filters"))
        self.lbl_quality.setText(t("filters.quality"))
        self.min_width.setPlaceholderText(t("filters.min_width"))
        self.orientation.setPlaceholderText(t("filters.orientation"))
        self.color.setPlaceholderText(t("filters.color"))

        # Center
        self.grp_gallery.setTitle(t("panel.gallery"))

        # Right
        self.grp_details.setTitle(t("panel.details"))
        self.lbl_details_title.setText(t("details.title"))
        self.lbl_details_source.setText(t("details.source"))
        self.lbl_details_license.setText(t("details.license"))
        self.lbl_details_dims.setText(t("details.dimensions"))
        self.lbl_links.setText(t("details.links"))

        self.btn_open_source.setText(t("link.open_source"))
        self.btn_open_license.setText(t("link.license_page"))
        self.btn_download.setText(t("btn.download"))
        self.btn_copy_credit.setText(t("btn.copy_credit"))

    # Search + selection
    def _on_search_clicked(self) -> None:
        query = self.search_edit.text().strip()
        clear_gallery(self.gallery)
        items = make_mock_items(query, n=18)
        render_items(self.gallery, items)
        scope = t("scope.pd") if self.scope_pd.isChecked() else t("scope.free")
        self.statusBar().showMessage(t("status.results").format(n=len(items), scope=scope, ms=3))
        if self.gallery.count() > 0:
            self.gallery.setCurrentRow(0)

    def _on_item_selected(self, item: ImageItem | None) -> None:
        self._current_item = item
        if not item:
            self.val_title.setText("—")
            self.val_source.setText("—")
            self.val_license.setText("—")
            self.val_dims.setText("—")
            for b in (self.btn_open_source, self.btn_open_license, self.btn_copy_credit):
                b.setEnabled(False)
            return

        self.val_title.setText(item.title or "—")
        self.val_source.setText(f"{item.author} — {item.source.name.title()}")
        self.val_license.setText(item.license_badge())
        wh = f"{item.width}×{item.height}px" if (item.width and item.height) else "—"
        self.val_dims.setText(wh)

        for b in (self.btn_open_source, self.btn_open_license, self.btn_copy_credit):
            b.setEnabled(True)

    # Actions (open/copy)
    def _action_open_source(self) -> None:
        if self._current_item:
            QDesktopServices.openUrl(QUrl(self._current_item.source_url))

    def _action_open_license(self) -> None:
        if self._current_item:
            QDesktopServices.openUrl(QUrl(self._current_item.license_url))

    def _action_copy_credit(self) -> None:
        if self._current_item:
            cb = self.clipboard() if hasattr(self, "clipboard") else None
            # Use QApplication clipboard
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(self._current_item.credit_text or "")
