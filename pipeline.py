"""
خط معالجة البيانات ونمذجة المخاطر الوبائية المكانية
Libya Epidemic Prediction Engine (Libya-EWS)
"""
import math
import json
import urllib.request
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent

def load_json(rel_path):
    return json.loads((ROOT / rel_path).read_text(encoding='utf-8'))

def get_live_weather(lat: float, lon: float) -> dict:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain&timezone=auto"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Libya-EWS/2.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode())
            current = res.get('current', {})
            return {
                'temp_c': current.get('temperature_2m', 28.0),
                'humidity': current.get('relative_humidity_2m', 35.0),
                'rain_mm': current.get('rain', 0.0)
            }
    except Exception:
        return {'temp_c': 28.0, 'humidity': 35.0, 'rain_mm': 0.0}

def compute_climate_suitability(disease: dict, weather: dict) -> float:
    if not disease.get('climate_sensitive'):
        return 0.15
    
    t = weather['temp_c']
    h = weather['humidity']
    rain = weather['rain_mm']
    mode = disease.get('transmission_mode', '')

    if 'vector_mosquito' in mode or 'vector_and_contact' in mode:
        temp_factor = 1.0 if (20.0 <= t <= 34.0) else 0.3
        water_factor = min(1.0, rain / 15.0) if rain > 0 else (h / 100.0)
        return round((temp_factor * 0.6) + (water_factor * 0.4), 2)

    if 'waterborne' in mode:
        return 0.9 if rain > 5.0 or t > 32.0 else 0.4

    if disease['code'] in ['IMM-07', 'IMM-08']:
        return 0.95 if (t > 28.0 and h < 30.0) else 0.3

    return 0.25

def run():
    print("⏳ جاري تشغيل محرك النمذجة الوبائية وحساب درجات التهديد...")
    diseases = {d['code']: d for d in load_json('config/ncdc_diseases.json')['diseases']}
    sectors = load_json('config/border_sectors.json')['sectors']

    incident_stats = {
        "SD": {"cases": 420, "deaths": 28, "growth": 0.45},
        "TD": {"cases": 180, "deaths": 4,  "growth": 0.25},
        "NE": {"cases": 95,  "deaths": 6,  "growth": 0.15},
        "TN": {"cases": 60,  "deaths": 0,  "growth": 0.10},
        "EG": {"cases": 45,  "deaths": 1,  "growth": 0.05},
        "DZ": {"cases": 20,  "deaths": 0,  "growth": 0.02}
    }

    evaluated_sectors = []
    highest_threat = None

    for sec in sectors:
        d_code = sec['primary_threat']
        d = diseases[d_code]
        stats = incident_stats.get(sec['id'], {"cases": 10, "deaths": 0, "growth": 0.0})
        
        weather = get_live_weather(sec['coords'][0], sec['coords'][1])
        c_suit = compute_climate_suitability(d, weather)

        cfr_obs = (stats['deaths'] / max(1, stats['cases'])) * 100.0
        cfr_corr = min(4.0, max(1.0, cfr_obs / d['cfr_bench']))

        i_adj = min(1.0, (stats['cases'] * cfr_corr) / 400.0)
        m_flow = sec['mobility_weight']
        g_rate = min(1.0, stats['growth'] * (d['incubation_max'] / 20.0))
        v_local = (sec['health_gap'] * 0.6) + (sec['wash_deficit'] * 0.4)

        z = (0.40 * (i_adj * m_flow * 4.0)) + (0.25 * g_rate * 2.5) + (0.20 * c_suit * 2.0) + (0.15 * v_local * 1.5) - 2.1
        score = round((1.0 / (1.0 + math.exp(-z))) * 100.0, 1)

        if score >= 75.0 or (d['reporting_tier'] == 'immediate' and score >= 65.0):
            level = "red"
        elif score >= 50.0:
            level = "orange"
        elif score >= 25.0:
            level = "yellow"
        else:
            level = "green"

        res = {
            "id": sec['id'],
            "name": sec['name'],
            "ports": sec['ports'],
            "municipalities": sec['municipalities'],
            "threat": f"{d['name_ar']} ({d['code']})",
            "threat_code": d['code'],
            "score": score,
            "level": level,
            "coords": sec['coords'],
            "weather": weather,
            "epi": {
                "cases_14d": stats['cases'],
                "cfr_percent": round(cfr_obs, 1),
                "climate_suitability": c_suit
            }
        }
        evaluated_sectors.append(res)
        if highest_threat is None or score > highest_threat['score']:
            highest_threat = res

    flash_text = (
        f"🚨 بلاغ عاجل لإدارة الرصد والاستجابة السريعة:\n"
        f"المرض: {highest_threat['threat']}\n"
        f"القطاع: {highest_threat['name']}\n"
        f"المنافذ المستهدفة: {highest_threat['ports']}\n"
        f"البلديات المهددة: {', '.join(highest_threat['municipalities'])}\n"
        f"مؤشر التهديد المحسوب: {highest_threat['score']}% (المستوى: {highest_threat['level'].upper()})\n"
        f"الطقس الميداني بالمنفذ: {highest_threat['weather']['temp_c']}°C، رطوبة {highest_threat['weather']['humidity']}%\n"
        f"التوجيه: تفعيل الرصد النشط وفحص الوافدين فوراً، وتأمين المخزون الوقائي بمستشفى القطاع."
    )

    out_data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "national_score": round(sum(s['score'] for s in evaluated_sectors) / len(evaluated_sectors), 1),
        "sectors": evaluated_sectors,
        "flash_report": flash_text
    }

    out_dir = ROOT / 'data'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'risk_data.json').write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ تم تحديث مخرجات الخطر بنجاح في data/risk_data.json (أعلى تهديد: {highest_threat['threat']} بنسبة {highest_threat['score']}%)")

if __name__ == '__main__':
    run()
    
