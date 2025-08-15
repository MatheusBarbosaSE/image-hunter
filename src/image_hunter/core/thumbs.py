from __future__ import annotations

import hashlib
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


# Cache directory: <repo>/thumbnails
CACHE_DIR = Path(__file__).resolve().parents[2] / "thumbnails"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _hash_name(url: str) -> str:
    """Return a stable filename for the URL (sha1 hex)."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest() + ".img"


@dataclass
class _Job:
    index: int
    url: str
    path: Path


class _Signals(QObject):
    """Qt signals for loader results."""
    loaded = Signal(int, str)   # index, file path
    failed = Signal(int, str)   # index, reason


class _Task(QRunnable):
    """Background task: download a single thumbnail to cache."""
    def __init__(self, job: _Job, signals: _Signals, timeout: float = 10.0, max_bytes: int = 5_000_000) -> None:
        super().__init__()
        self.job = job
        self.signals = signals
        self.timeout = timeout
        self.max_bytes = max_bytes

    def run(self) -> None:
        # If already cached, emit immediately
        if self.job.path.is_file():
            self.signals.loaded.emit(self.job.index, str(self.job.path))
            return

        # Prepare request (polite headers)
        req = urllib.request.Request(
            self.job.url,
            headers={
                "User-Agent": "ImageHunter/0.1 (thumb-loader)",
                "Accept": "image/*,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                # Basic size guard (if server provides Content-Length)
                length = resp.headers.get("Content-Length")
                if length and int(length) > self.max_bytes:
                    self.signals.failed.emit(self.job.index, "Content too large")
                    return

                # Stream to temp then move (atomic-ish)
                tmp = self.job.path.with_suffix(".tmp")
                with open(tmp, "wb") as f:
                    read = 0
                    while True:
                        chunk = resp.read(64 * 1024)
                        if not chunk:
                            break
                        read += len(chunk)
                        if read > self.max_bytes:
                            f.close()
                            tmp.unlink(missing_ok=True)
                            self.signals.failed.emit(self.job.index, "Exceeded max size")
                            return
                        f.write(chunk)
                os.replace(tmp, self.job.path)
                self.signals.loaded.emit(self.job.index, str(self.job.path))
        except Exception as e:  # network errors, timeouts, etc.
            self.signals.failed.emit(self.job.index, str(e))


class ThumbLoader(QObject):
    """Schedule thumbnail downloads and emit results back to the UI thread."""
    def __init__(self, parent: Optional[QObject] = None, max_workers: int = 6) -> None:
        super().__init__(parent)
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(max_workers)
        self.signals = _Signals()

    def load_for_list(self, list_widget) -> None:
        """
        Iterate items in a QListWidget, read each ImageItem from UserRole,
        and schedule thumbnail downloads.
        """
        from PySide6.QtCore import Qt  # local import to avoid hard dep here
        count = list_widget.count()
        for i in range(count):
            item = list_widget.item(i)
            model = item.data(Qt.UserRole)
            if not model or not getattr(model, "thumbnail_url", None):
                continue
            url = model.thumbnail_url
            path = CACHE_DIR / _hash_name(url)
            job = _Job(index=i, url=url, path=path)
            # If cached, short-circuit via a tiny task (still async)
            task = _Task(job, self.signals)
            self.pool.start(task)
