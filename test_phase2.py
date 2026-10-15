import sys, pathlib
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from risk import compute_risk, load_cfg, level_for, spread_value

NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)

def ev(country, disease, days_ago, status='verified'):
    return {'country': country, 'disease': disease, 'status': status,
            'published': (NOW - timedelta(days=days_ago)).isoformat()}

def test_weights_sum_100():
    assert sum(load_cfg()['weights'].values()) == 100

def test_no_events_is_monitoring():
    r = compute_risk([], load_cfg(), NOW)
    assert r['national']['score'] == 0 and r['national']['level'] == 'monitor'

def test_pending_ignored():
    r = compute_risk([ev('SD', 'cholera', 1, 'pending')], load_cfg(), NOW)
    assert r['items'] == []

def test_old_events_ignored():
    assert compute_risk([ev('SD', 'cholera', 20)], load_cfg(), NOW)['items'] == []


def test_example_sudan_cholera():
    evs = [ev('SD', 'cholera', d) for d in (1, 2, 3)]
    r = compute_risk(evs, load_cfg(), NOW)
    it = r['items'][0]
    # قرب 24 + خطورة 12.5 + انتشار 18 + تنقل 7.5 + جاهزية 5
    assert it['score'] == 67.0 and it['level'] == 'preparedness'

def test_levels():
    lv = load_cfg()['levels']
    assert [level_for(s, lv)['id'] for s in (0, 24.9, 25, 50, 75, 100)] == \
        ['monitor', 'monitor', 'alert', 'preparedness', 'emergency', 'emergency']

def test_spread_grows():
    assert spread_value(0, 5) == 0 and spread_value(2, 0) > spread_value(2, 2)

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'):
            f(); print('ok', n)
          
