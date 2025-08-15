from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List


class Source(Enum):
    """Where an image item comes from (provider)."""
    OPENVERSE = auto()
    PEXELS = auto()
    PIXABAY = auto()
    UNSPLASH = auto()


class License(Enum):
    """
    Normalized license categories we care about for UI/badges/filters.
    Keep this small & provider-agnostic; store exact license URL separately.
    """
    PD_CC0 = auto()      # Public Domain / CC0
    CC_BY = auto()       # Creative Commons Attribution (any version)
    CC_BY_SA = auto()    # Creative Commons Attribution-ShareAlike
    UNSPLASH = auto()    # Unsplash License
    PEXELS = auto()      # Pexels License
    PIXABAY = auto()     # Pixabay License
    OTHER = auto()       # Unknown / other permissive-but-not-PD


@dataclass
class ImageItem:
    """
    Unified model used by the Gallery and Details panel.

    Required:
      - id: Provider-specific stable id (use str).
      - source: Which provider (Source enum).
      - title: Human-friendly title (fallback to query or file name).
      - author: Creator/photographer/owner display name.

    URLs:
      - thumbnail_url: small image used in the grid (fast to load).
      - image_url: direct file URL for download/preview (may be large).
      - source_url: provider page URL (Open in source).
      - license_url: canonical page for the license text.

    License:
      - license: normalized License enum.
      - credit_text: ready-to-copy attribution line (if required).

    Extras:
      - width/height: pixels (for quality filters, aspect/orientation).
      - tags: optional keywords from the provider.
      - color_hex: optional dominant color (e.g., "#112233").
    """
    id: str
    source: Source
    title: str
    author: str

    thumbnail_url: str
    image_url: str
    source_url: str
    license_url: str

    license: License
    credit_text: str

    width: Optional[int] = None
    height: Optional[int] = None
    tags: Optional[List[str]] = None
    color_hex: Optional[str] = None

    # Convenience properties/methods used by the UI
    @property
    def is_public_domain(self) -> bool:
        """True if the item is PD/CC0."""
        return self.license == License.PD_CC0

    @property
    def orientation(self) -> Optional[str]:
        """Return 'landscape' | 'portrait' | 'square' (or None if unknown)."""
        if self.width and self.height:
            if self.width > self.height:
                return "landscape"
            if self.width < self.height:
                return "portrait"
            return "square"
        return None

    def license_badge(self) -> str:
        """Short badge text for the gallery tile."""
        mapping = {
            License.PD_CC0: "PD/CC0",
            License.CC_BY: "CC-BY",
            License.CC_BY_SA: "CC-BY-SA",
            License.UNSPLASH: "Unsplash",
            License.PEXELS: "Pexels",
            License.PIXABAY: "Pixabay",
            License.OTHER: "Free",
        }
        return mapping.get(self.license, "Free")

    def tooltip_text(self) -> str:
        """Multi-line tooltip shown over the tile/thumbnail."""
        wh = f"{self.width}×{self.height}px" if (self.width and self.height) else "—"
        return (
            f"{self.title}\n"
            f"{self.author} — {self.source.name.title()}\n"
            f"License: {self.license_badge()}\n"
            f"Dimensions: {wh}"
        )
