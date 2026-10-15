"""محرك الخطر: درجة 0-100 لكل (مرض، دولة) + مؤشر وطني."""
import json, math, pathlib
from datetime import datetime, timedelta, timezone
import yaml

ROOT = pathlib.Path(__file__).resolve().parent

def _dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def level_for(score, levels):
    cur = levels[0]
    for lv in sorted(levels, key=lambda x: x['min']):
        if score >= lv['min']:
            cur = lv
    return cur

def spread_value(recent, prev):
    """0-10: يرتفع بعدد الأخبار الموثقة الحديثة وبالزيادة عن الأسبوع السابق."""
    if recent == 0:
        return 0.0
    return min(10.0, recent * 1.5 + max(0, recent - prev) * 1.5)
  
def compute_risk(events, cfg, now=None):
    now = now or datetime.now(timezone.utc)
    w = cfg['weights']
    groups = {}
    for e in events:
        if e.get('status') != 'verified':
            continue
        t = _dt(e.get('published') or '')
        if not t:
            continue
        age = (now - t).days
        if age < 0 or age >= 14:
            continue
        g = groups.setdefault((e['country'], e['disease']), {'recent': 0, 'prev': 0})
        g['recent' if age < 7 else 'prev'] += 1
    items = []
    for (country, disease), g in groups.items():
        vals = {
            'proximity': cfg['proximity'].get(country, 2),
            'severity': cfg['severity'].get(disease, 5),
            'spread': spread_value(g['recent'], g['prev']),
            'mobility': cfg['mobility'].get(country, 5),
            'readiness': cfg['readiness_gap'],
        }
        parts = {k: round(w[k] * vals[k] / 10, 1) for k in w}
        score = round(sum(parts.values()), 1)
        lv = level_for(score, cfg['levels'])
        items.append({'country': country, 'disease': disease, 'score': score,
                      'level': lv['id'], 'level_ar': lv['ar'],
                      'components': parts, 'events_7d': g['recent'], 'events_prev_7d': g['prev']})
    items.sort(key=lambda x: x['score'], reverse=True)
    top = items[0] if items else None
    score = top['score'] if top else 0.0
    lv = level_for(score, cfg['levels'])
    national = {'score': score, 'level': lv['id'], 'level_ar': lv['ar'], 'level_en': lv['en'],
                'driver': {'country': top['country'], 'disease': top['disease']} if top else None}
    return {'generated_at': now.isoformat(), 'national': national, 'items': items,
            'tables_filled': cfg.get('tables_filled', False)}

def load_cfg():
    return yaml.safe_load((ROOT / 'risk.yaml').read_text(encoding='utf-8'))

def run():
    cfg = load_cfg()
    data = json.loads((ROOT / 'data' / 'events.json').read_text(encoding='utf-8'))
    out = compute_risk(data['events'], cfg)
    (ROOT / 'data' / 'risk.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    n = out['national']
    print(f"risk national={n['score']} level={n['level']} items={len(out['items'])}")

if __name__ == '__main__':
    run()
  
