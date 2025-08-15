from __future__ import annotations

# Add ./src to sys.path so we can import the package from the repo root
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Now imports work regardless of the editor/terminal cwd
from image_hunter.core.models import ImageItem, Source, License


def main() -> None:
    # Build a sample item to exercise properties/helpers
    item = ImageItem(
        id="demo-1",
        source=Source.OPENVERSE,
        title="Minimal dark fabric bag",
        author="Jane Doe",
        thumbnail_url="https://example.com/thumb.jpg",
        image_url="https://example.com/full.jpg",
        source_url="https://example.com/page",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        license=License.PD_CC0,
        credit_text="Photo by Jane Doe (CC0)",
        width=3000,
        height=2000,
    )

    print("orientation:", item.orientation)       # expected: landscape
    print("badge:", item.license_badge())         # expected: PD/CC0
    print("tooltip:\n" + item.tooltip_text())     # multi-line preview


if __name__ == "__main__":
    main()
