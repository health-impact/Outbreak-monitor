"""قاعدة الموثوقية: يُنشر الخبر إذا كان من مصدر رسمي،
أو أكده مصدران غير رسميين مستقلان (جهتان مختلفتان) خلال نافذة زمنية."""
from datetime import datetime, timedelta

WINDOW_DAYS = 7

def _dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def verify(events, window_days=WINDOW_DAYS):
    groups = {}
    for e in events:
        groups.setdefault((e['country'], e['disease']), []).append(e)
    out = []
    for evs in groups.values():
        for e in evs:
            if e['official']:
                e['status'], e['confirmed_by'] = 'verified', [e['org']]
                out.append(e); continue
            t = _dt(e['published'] or '')
            peers = set()
            for o in evs:
                if o['org'] == e['org']:
                    continue
                ot = _dt(o['published'] or '')
                if t and ot and abs(t - ot) <= timedelta(days=window_days):
                    peers.add(o['org'])
            if peers:
                e['status'], e['confirmed_by'] = 'verified', sorted(peers | {e['org']})
            else:
                e['status'], e['confirmed_by'] = 'pending', [e['org']]
            out.append(e)
    return out
