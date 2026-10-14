"""ربط كل خبر بمرض ودولة (عربي/إنجليزي)."""
import re

def _hit(text, kws):
    for k in kws:
        k = k.lower()
        if k.isascii():
            if re.search(r'(?<![a-z])' + re.escape(k) + r'(?![a-z])', text):
                return True
        elif k in text:
            return True
    return False

def tag_item(item, diseases, countries):
    text = f"{item['title']} {item['summary']}".lower()
    ds = [d['id'] for d in diseases if _hit(text, d['kw'])]
    cs = [c['id'] for c in countries if _hit(text, c['kw'])]
    return ds, cs

def to_events(item, diseases, countries):
    ds, cs = tag_item(item, diseases, countries)
    if not ds:
        return []
    cs = cs or ['GLOBAL']
    return [dict(item, disease=d, country=c) for d in ds for c in cs]
