"""جلب RSS/Atom بدون مكتبات خارجية، مع تسجيل صحة كل مصدر."""
import re, time, hashlib, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

UA = "Libya-EWS/0.1 (+public health monitoring)"

def _text(el, *names):
    for n in names:
        for child in el.iter():
            tag = child.tag.split('}')[-1]
            if tag == n and (child.text or child.attrib.get('href')):
                return (child.text or child.attrib.get('href') or '').strip()
    return ''

def _date(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s).astimezone(timezone.utc).isoformat()
    except Exception:
        try:
            return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc).isoformat()
        except Exception:
            return None

def _clean(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html or '')).strip()

def parse_feed(xml_bytes, source):
    root = ET.fromstring(xml_bytes)
    items = [e for e in root.iter() if e.tag.split('}')[-1] in ('item', 'entry')]
    out = []
    for it in items:
        title = _clean(_text(it, 'title'))
        link = _text(it, 'link', 'guid')
        summary = _clean(_text(it, 'description', 'summary', 'content'))[:1500]
        published = _date(_text(it, 'pubDate', 'published', 'updated', 'date'))
        if not title or not link:
            continue
        out.append({
            'id': hashlib.sha1(link.encode()).hexdigest()[:16],
            'title': title, 'summary': summary, 'url': link, 'published': published,
            'source_id': source['id'], 'source_name': source['name'],
            'org': source['org'], 'official': bool(source['official']),
        })
    return out

def fetch_source(source, timeout=30):
    """يرجع (items, health). لا يرفع استثناء: الفشل يُسجَّل في health."""
    health = {'id': source['id'], 'ok': False, 'items': 0, 'error': None,
              'checked_at': datetime.now(timezone.utc).isoformat()}
    t0 = time.time()
    try:
        req = urllib.request.Request(source['url'], headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        items = parse_feed(data, source)
        health.update(ok=True, items=len(items))
    except Exception as e:
        items = []
        health['error'] = f'{type(e).__name__}: {e}'[:200]
    health['ms'] = int((time.time() - t0) * 1000)
    return items, health
