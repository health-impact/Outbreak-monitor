import json, pathlib
from datetime import datetime, timezone
import yaml
from fetch import fetch_source
from normalize import to_events
from verify import verify

ROOT = pathlib.Path(__file__).resolve().parent

def load(name):
    return yaml.safe_load((ROOT / name).read_text(encoding='utf-8'))

def run():
    sources = [s for s in load('sources.yaml')['sources'] if s.get('enabled') and (s.get('url') or s.get('urls'))]
    diseases = load('diseases.yaml')['diseases']
    countries = load('countries.yaml')['countries']
    raw, health = [], []
    for s in sources:
        items, h = fetch_source(s)
        raw += items; health.append(h)
    events = []
    for it in raw:
        events += to_events(it, diseases, countries)
    events = verify(events)
    events.sort(key=lambda e: e['published'] or '', reverse=True)
    now = datetime.now(timezone.utc).isoformat()
