import json, pathlib
from datetime import datetime, timezone
import yaml
from fetch import fetch_source
from normalize import to_events
from verify import verify
import risk

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
    out = ROOT / 'data'; out.mkdir(exist_ok=True)
    (out / 'events.json').write_text(json.dumps(
        {'generated_at': now, 'count': len(events), 'events': events[:2000]},
        ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'source_health.json').write_text(json.dumps(
        {'generated_at': now, 'sources': health}, ensure_ascii=False, indent=1), encoding='utf-8')
    risk.run()
    bad = [h['id'] for h in health if not h['ok']]
    print(f'events={len(events)} sources_ok={len(health)-len(bad)}/{len(health)} failed={bad}')

if __name__ == '__main__':
    run()
