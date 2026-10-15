"""جلب RSS/Atom بدون مكتبات خارجية، مع تسجيل صحة كل مصدر."""
import re, time, json, hashlib, urllib.request
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


WHO_DON_BASE = "https://www.who.int/emergencies/disease-outbreak-news"

def parse_who_api(raw, source):
    """واجهة WHO الرسمية للأخبار (JSON/OData). الحقول تُقرأ بتسامح لأن الأسماء قد تتغير."""
    data = json.loads(raw)
    rows = data.get('value', data) if isinstance(data, dict) else data
    out = []
    for r in rows or []:
        title = _clean(r.get('Title') or r.get('title') or '')
        path = r.get('ItemDefaultUrl') or r.get('UrlName') or ''
        if path and not path.startswith('http'):
            path = WHO_DON_BASE + (path if path.startswith('/') else '/' + path)
        summary = _clean(r.get('Summary') or r.get('Overview') or r.get('Description') or '')[:1500]
        published = _date(r.get('PublicationDateAndTime') or r.get('PublicationDate') or r.get('DateCreated') or '')
        if not title or not path:
            continue
        out.append({
            'id': hashlib.sha1(path.encode()).hexdigest()[:16],
            'title': title, 'summary': summary, 'url': path, 'published': published,
            'source_id': source['id'], 'source_name': source['name'],
            'org': source['org'], 'official': bool(source['official']),
        })
    return out

def fetch_source(source, timeout=30):
    """يرجع (items, health). يجرّب الروابط بالترتيب (url أو urls) ولا يرفع استثناء."""
    urls = source.get('urls') or [source['url']]
    health = {'id': source['id'], 'ok': False, 'items': 0, 'error': None, 'tried': [],
              'checked_at': datetime.now(timezone.utc).isoformat()}
    t0 = time.time()
    items = []
    for url in urls:
        tr = {'url': url}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                tr['content_type'] = r.headers.get('Content-Type', '')
            if source.get('type') == 'who_api':
                got = parse_who_api(data, source)
            else:
                got = parse_feed(data, source)
            tr['items'] = len(got)
            if not got:
                tr['sample'] = data[:200].decode('utf-8', 'replace')
            health['tried'].append(tr)
            if got:
                items = got
                health.update(ok=True, items=len(got), url_used=url)
                break
        except Exception as e:
            tr['error'] = f'{type(e).__name__}: {e}'[:200]
            health['tried'].append(tr)
    if not items:
        health['error'] = 'no items from any url'
    health['ms'] = int((time.time() - t0) * 1000)
    return items, health
