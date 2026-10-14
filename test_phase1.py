import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import yaml
from ews.fetch import parse_feed
from ews.normalize import to_events
from ews.verify import verify

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = yaml.safe_load((ROOT/'config/diseases.yaml').read_text(encoding='utf-8'))['diseases']
C = yaml.safe_load((ROOT/'config/countries.yaml').read_text(encoding='utf-8'))['countries']

RSS = b"""<rss><channel><item><title>Cholera outbreak in Sudan</title>
<link>https://x.org/1</link><description>&lt;p&gt;Cases rising near Chad border&lt;/p&gt;</description>
<pubDate>Tue, 13 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"""

def src(i, org, official):
    return {'id': i, 'name': i, 'org': org, 'official': official}

def ev(i, org, official):
    return to_events(parse_feed(RSS, src(i, org, official))[0], D, C)

def test_parse_and_tag():
    items = parse_feed(RSS, src('a', 'WHO', True))
    assert len(items) == 1 and 'Cases rising' in items[0]['summary']
    evs = to_events(items[0], D, C)
    assert {(e['disease'], e['country']) for e in evs} == {('cholera', 'SD'), ('cholera', 'TD')}

def test_official_verified():
    assert all(e['status'] == 'verified' for e in verify(ev('a', 'WHO', True)))

def test_unofficial_needs_two_orgs():
    assert all(e['status'] == 'pending' for e in verify(ev('p', 'ISID', False)))
    res = verify(ev('p', 'ISID', False) + ev('h', 'HealthMap', False))
    assert all(e['status'] == 'verified' for e in res)

def test_same_org_is_not_independent():
    res = verify(ev('p1', 'ISID', False) + ev('p2', 'ISID', False))
    assert all(e['status'] == 'pending' for e in res)

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'):
            f(); print('ok', n)
