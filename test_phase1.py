import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import yaml
from fetch import parse_feed, parse_who_api
from normalize import to_events
from verify import verify

ROOT = pathlib.Path(__file__).resolve().parent
D = yaml.safe_load((ROOT/'diseases.yaml').read_text(encoding='utf-8'))['diseases']
C = yaml.safe_load((ROOT/'countries.yaml').read_text(encoding='utf-8'))['countries']

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
  
