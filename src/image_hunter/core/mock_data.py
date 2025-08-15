from __future__ import annotations

from typing import List
from .models import ImageItem, Source, License


def make_mock_items(query: str, n: int = 12) -> List[ImageItem]:
    """
    Produce a small list of demo ImageItems to exercise the gallery.
    No network calls here; URLs are placeholders.
    """
    authors = ["Jane Doe", "Alex Kim", "Marta Silva", "Louis Dupont"]
    titles = [
        f"{query or 'Sample'} — minimal",
        f"{query or 'Sample'} — dark",
        f"{query or 'Sample'} — texture",
        f"{query or 'Sample'} — modern",
    ]
    licenses = [License.PD_CC0, License.CC_BY, License.PEXELS, License.PIXABAY, License.UNSPLASH]
    sources = [Source.OPENVERSE, Source.PEXELS, Source.PIXABAY, Source.UNSPLASH]

    items: List[ImageItem] = []
    for i in range(n):
        src = sources[i % len(sources)]
        lic = licenses[i % len(licenses)]
        w = 2400 + (i % 3) * 600
        h = 1600 + (i % 3) * 600
        title = titles[i % len(titles)]
        author = authors[i % len(authors)]
        items.append(
            ImageItem(
                id=f"mock-{i}",
                source=src,
                title=title,
                author=author,
                thumbnail_url=f"https://example.com/thumb/{i}.jpg",
                image_url=f"https://example.com/full/{i}.jpg",
                source_url=f"https://example.com/src/{i}",
                license_url="https://creativecommons.org/publicdomain/zero/1.0/",
                license=lic,
                credit_text=f"Photo by {author} — {src.name.title()}",
                width=w,
                height=h,
                tags=[query] if query else None,
                color_hex="#22262B",
            )
        )
    return items
