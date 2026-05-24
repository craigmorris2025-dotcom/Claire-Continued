from __future__ import annotations


class SourceReliabilityScorer:
    HIGH = {"sec.gov":0.96,"federalregister.gov":0.94,"congress.gov":0.93,"nist.gov":0.93,"nih.gov":0.92,"who.int":0.90,"oecd.org":0.88,"worldbank.org":0.88,"imf.org":0.88,"ftc.gov":0.90,"justice.gov":0.90,"treasury.gov":0.90,"fda.gov":0.90,"energy.gov":0.88,"europa.eu":0.88,"ec.europa.eu":0.88,"gov.uk":0.88,"reuters.com":0.82,"apnews.com":0.82,"nature.com":0.82,"science.org":0.82,"arxiv.org":0.72}
    def score(self, domain: str, content_length: int = 0, search_rank: int = 0) -> float:
        base=self.HIGH.get(domain,0.55)
        if content_length < 200: base -= 0.08
        elif content_length > 2000: base += 0.03
        if search_rank: base += max(0.0, 0.04 - (search_rank * 0.005))
        return round(max(0.05, min(1.0, base)), 4)
