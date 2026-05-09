from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import List

from .models import LiveFetchResult, NormalizedContent


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self.in_title = False
        self.title_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        clean = data.strip()
        if not clean:
            return
        if self.in_title:
            self.title_parts.append(clean)
        self.parts.append(clean)


class ContentNormalizer:
    def normalize(self, result: LiveFetchResult) -> NormalizedContent:
        text = result.text or ""
        title = ""

        if "html" in (result.content_type or "").lower() or "<html" in text.lower():
            parser = _TextExtractor()
            try:
                parser.feed(text)
                text = " ".join(parser.parts)
                title = " ".join(parser.title_parts)
            except Exception:
                text = self._strip_tags(text)

        text = " ".join(text.split())
        if not title:
            title = self._derive_title(text)

        summary = text[:400] + ("..." if len(text) > 400 else "")
        terms = self._terms(text)

        return NormalizedContent(
            source_url=result.url,
            title=title or "Untitled source",
            summary=summary,
            text=text,
            content_type=result.content_type,
            extracted_terms=terms,
            normalization_status="normalized" if text else "empty",
        )

    def _strip_tags(self, text: str) -> str:
        return re.sub(r"<[^>]+>", " ", text)

    def _derive_title(self, text: str) -> str:
        if not text:
            return "Untitled source"
        return text[:80] + ("..." if len(text) > 80 else "")

    def _terms(self, text: str) -> List[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
        counts = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        return [word for word, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:12]]
