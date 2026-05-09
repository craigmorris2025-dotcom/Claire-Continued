from __future__ import annotations

import json, re
from html.parser import HTMLParser
from typing import List, Tuple


class _HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.parts=[]; self.title_parts=[]; self.in_title=False; self.skip_depth=0
    def handle_starttag(self, tag, attrs):
        if tag.lower()=="title": self.in_title=True
        if tag.lower() in {"script","style","noscript"}: self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag.lower()=="title": self.in_title=False
        if tag.lower() in {"script","style","noscript"} and self.skip_depth: self.skip_depth -= 1
    def handle_data(self, data):
        if self.skip_depth: return
        clean=" ".join(data.split())
        if not clean: return
        if self.in_title: self.title_parts.append(clean)
        self.parts.append(clean)


class ContentNormalizer:
    def normalize(self, text: str, content_type: str | None = None) -> Tuple[str, str, List[str]]:
        if not text: return "Untitled", "", []
        base=(content_type or "").split(";")[0].strip().lower()
        if base == "application/json":
            try: text=json.dumps(json.loads(text), ensure_ascii=False, indent=2)
            except Exception: pass
            title="JSON source"
        elif "html" in base or "<html" in text.lower():
            parser=_HTMLTextParser(); parser.feed(text); title=" ".join(parser.title_parts).strip() or "HTML source"; text=" ".join(parser.parts)
        else:
            clean=" ".join(text.split()); title=clean[:90]+("..." if len(clean)>90 else "")
        normalized=" ".join(text.split())
        return title, normalized, self.terms(normalized)
    def terms(self, text: str) -> List[str]:
        words=re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
        stop={"that","this","with","from","have","will","were","been","their","there","which","about","would","could","should","https","http","html","page","more","also"}
        counts={}
        for w in words:
            if w not in stop: counts[w]=counts.get(w,0)+1
        return [w for w,_ in sorted(counts.items(), key=lambda x:x[1], reverse=True)[:20]]
