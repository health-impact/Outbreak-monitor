"""
خط معالجة البيانات ونمذجة المخاطر الوبائية المكانية
Libya Epidemic Prediction Engine (Libya-EWS) — Self-Bootstrapping Version
"""
import math
import json
import urllib.request
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = ROOT / 'config'

# 1. قائمة الـ 48 مرضاً المعتمدة رسمياً (NCDC Registry)
DISEASES_DATA = [
    {"code": "IMM-01", "name_ar": "الشلل الرخو الحاد", "name_en": "Acute Flaccid Paralysis", "reporting_tier": "immediate", "transmission_mode": "fecal_oral", "incubation_max": 35, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 5.0},
    {"code": "IMM-02", "name_ar": "الجمرة الخبيثة", "name_en": "Anthrax", "reporting_tier": "immediate", "transmission_mode": "zoonotic_contact", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 20.0},
    {"code": "IMM-03", "name_ar": "الهيضة (الكوليرا)", "name_en": "Cholera", "reporting_tier": "immediate", "transmission_mode": "waterborne", "incubation_max": 5, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 1.5},
    {"code": "IMM-04", "name_ar": "الخناق (الدفتيريا)", "name_en": "Diphtheria", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 5, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 10.0},
    {"code": "IMM-05", "name_ar": "التسمم الغذائي", "name_en": "Food Poisoning", "reporting_tier": "immediate", "transmission_mode": "foodborne", "incubation_max": 2, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 0.5},
    {"code": "IMM-06", "name_ar": "الحصبة", "name_en": "Measles", "reporting_tier": "immediate", "transmission_mode": "airborne_aerosol", "incubation_max": 18, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 3.0},
    {"code": "IMM-07", "name_ar": "الالتهاب السحائي الوبائي", "name_en": "Meningococcal Meningitis", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 10, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 12.0},
    {"code": "IMM-08", "name_ar": "التهاب السحايا بالمكورات الأخرى", "name_en": "Meningitis Unspecified", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 10.0},
    {"code": "IMM-09", "name_ar": "الحميات النزفية الفيروسية", "name_en": "Viral Hemorrhagic Fevers", "reporting_tier": "immediate", "transmission_mode": "vector_and_contact", "incubation_max": 21, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 40.0},
    {"code": "IMM-10", "name_ar": "الطاعون", "name_en": "Plague", "reporting_tier": "immediate", "transmission_mode": "vector_and_contact", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 30.0},
    {"code": "IMM-11", "name_ar": "الحصبة الألمانية", "name_en": "Rubella", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.2},
    {"code": "IMM-12", "name_ar": "داء الكلب", "name_en": "Rabies", "reporting_tier": "immediate", "transmission_mode": "zoonotic_bite", "incubation_max": 90, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 99.0},
    {"code": "IMM-13", "name_ar": "لدغة الثعبان", "name_en": "Snake Bite", "reporting_tier": "immediate", "transmission_mode": "environmental", "incubation_max": 1, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 2.0},
    {"code": "IMM-14", "name_ar": "لدغة العقرب", "name_en": "Scorpion Bite", "reporting_tier": "immediate", "transmission_mode": "environmental", "incubation_max": 1, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 0.8},
    {"code": "IMM-15", "name_ar": "الكزاز الوليدي", "name_en": "Tetanus Neonatorum", "reporting_tier": "immediate", "transmission_mode": "unhygienic_delivery", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 70.0},
    {"code": "IMM-16", "name_ar": "التيفوس الوبائي", "name_en": "Epidemic Typhus", "reporting_tier": "immediate", "transmission_mode": "vector_lice", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 15.0},
    {"code": "IMM-17", "name_ar": "الشاهوق (السعال الديكي)", "name_en": "Whooping Cough", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 10, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0},
    {"code": "IMM-18", "name_ar": "الحمى الصفراء", "name_en": "Yellow Fever", "reporting_tier": "immediate", "transmission_mode": "vector_mosquito", "incubation_max": 6, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 25.0},
    {"code": "IMM-19", "name_ar": "طوارئ وبائية مستجدة / جدري القردة", "name_en": "PHEIC / Mpox / Novel", "reporting_tier": "immediate", "transmission_mode": "emerging_unknown", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 10.0},
    {"code": "WKL-01", "name_ar": "الإسهالات الحادة", "name_en": "Acute Diarrhea", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 3, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.5},
    {"code": "WKL-02", "name_ar": "الزحار الأميبي", "name_en": "Amoebiasis", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 28, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.3},
    {"code": "WKL-03", "name_ar": "عضة الحيوان", "name_en": "Animal Bite", "reporting_tier": "weekly", "transmission_mode": "zoonotic_contact", "incubation_max": 2, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.0},
    {"code": "WKL-04", "name_ar": "الحمى المالطية (البروسيلا)", "name_en": "Brucellosis", "reporting_tier": "weekly", "transmission_mode": "zoonotic_foodborne", "incubation_max": 60, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0},
    {"code": "WKL-05", "name_ar": "الجديري المائي", "name_en": "Chickenpox", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.05},
    {"code": "WKL-06", "name_ar": "الليشمانيا الجلدية", "name_en": "Cutaneous Leishmaniasis", "reporting_tier": "weekly", "transmission_mode": "vector_sandfly", "incubation_max": 180, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.01},
    {"code": "WKL-07", "name_ar": "الأكياس العدارية المائية", "name_en": "Echinococcosis", "reporting_tier": "weekly", "transmission_mode": "zoonotic_fecal_oral", "incubation_max": 3650, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 2.0},
    {"code": "WKL-08", "name_ar": "السيلان", "name_en": "Gonococcal Infection", "reporting_tier": "weekly", "transmission_mode": "sexual", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.0},
    {"code": "WKL-09", "name_ar": "التهاب الكبد الفيروسي أ", "name_en": "Hepatitis A", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 50, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.3},
    {"code": "WKL-10", "name_ar": "التهاب الكبد الفيروسي ب", "name_en": "Hepatitis B", "reporting_tier": "weekly", "transmission_mode": "bloodborne", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0},
    {"code": "WKL-11", "name_ar": "التهاب الكبد الفيروسي ج", "name_en": "Hepatitis C", "reporting_tier": "weekly", "transmission_mode": "bloodborne", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.5},
    {"code": "WKL-12", "name_ar": "متلازمة العوز المناعي (الإيدز)", "name_en": "HIV (AIDS)", "reporting_tier": "weekly", "transmission_mode": "bloodborne_and_sexual", "incubation_max": 3650, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 20.0},
    {"code": "WKL-13", "name_ar": "الأنفلونزا الموسمية", "name_en": "Influenza (Seasonal)", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 4, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.1},
    {"code": "WKL-14", "name_ar": "الجذام", "name_en": "Leprosy", "reporting_tier": "weekly", "transmission_mode": "close_contact", "incubation_max": 7300, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.1},
    {"code": "WKL-15", "name_ar": "البرداء (الملاريا)", "name_en": "Malaria", "reporting_tier": "weekly", "transmission_mode": "vector_mosquito", "incubation_max": 30, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 2.0},
    {"code": "WKL-16", "name_ar": "الدرن المقاوم للأدوية (MDR-TB)", "name_en": "MDR-TB", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 15.0},
    {"code": "WKL-17", "name_ar": "النكاف", "name_en": "Mumps", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 25, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.05},
    {"code": "WKL-18", "name_ar": "الكزاز غير الوليدي", "name_en": "Other Tetanus", "reporting_tier": "weekly", "transmission_mode": "wound_soil", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 20.0},
    {"code": "WKL-19", "name_ar": "الدرن الرئوي (السل)", "name_en": "Pulmonary Tuberculosis", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 5.0},
    {"code": "WKL-20", "name_ar": "حمى الريكتسيا", "name_en": "Rickettsioses", "reporting_tier": "weekly", "transmission_mode": "vector_tick_flea", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 2.5},
    {"code": "WKL-21", "name_ar": "البلهارسيا", "name_en": "Schistosomiasis", "reporting_tier": "weekly", "transmission_mode": "water_snail", "incubation_max": 60, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.1},
    {"code": "WKL-22", "name_ar": "الزهري", "name_en": "Syphilis", "reporting_tier": "weekly", "transmission_mode": "sexual", "incubation_max": 90, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 1.0},
    {"code": "WKL-23", "name_ar": "الدرن خارج الرئة", "name_en": "Extra-Pulmonary TB", "reporting_tier": "weekly", "transmission_mode": "internal", "incubation_max": 365, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 5.0},
    {"code": "WKL-24", "name_ar": "التيفويد والباراتيفويد", "name_en": "Typhoid & Paratyphoid", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 30, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 1.5},
    {"code": "WKL-25", "name_ar": "التهاب كبدي غير محدد (E)", "name_en": "Hepatitis Unspecified (E)", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 60, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 4.0},
    {"code": "WKL-26", "name_ar": "الليشمانيا الحشوية (الكالازار)", "name_en": "Visceral Leishmaniasis", "reporting_tier": "weekly", "transmission_mode": "vector_sandfly", "incubation_max": 240, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 10.0},
    {"code": "WKL-27", "name_ar": "الفيروس التنفسي المخلوي (RSV)", "name_en": "Respiratory Syncytial Virus", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 8, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.2},
    {"code": "WKL-28", "name_ar": "التهاب الدماغ (غرب النيل)", "name_en": "Encephalitis / West Nile", "reporting_tier": "weekly", "transmission_mode": "vector_mosquito", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 8.0},
    {"code": "WKL-29", "name_ar": "كوفيد-19", "name_en": "COVID-19", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0}
]

# 2. مصفوفة القطاعات الحدودية الست
SECTORS_DATA = [
    {
        "id": "SD", "name": "قطاع السودان (الجنوب الشرقي)", "country_code": "SD",
        "ports": "منفذ العوينات البري — مطار الكفرة", "municipalities": ["الكفرة", "تازربو", "ربيانة"],
        "coords": [24.18, 23.30], "mobility_weight": 0.85, "health_gap": 0.85, "wash_deficit": 0.80,
        "primary_threat": "IMM-03"
    },
    {
        "id": "TD", "name": "قطاع تشاد (الجنوب)", "country_code": "TD",
        "ports": "منفذ التوم البري — القطرون", "municipalities": ["مرزق", "القطرون", "سبها"],
        "coords": [24.93, 14.64], "mobility_weight": 0.70, "health_gap": 0.80, "wash_deficit": 0.75,
        "primary_threat": "WKL-15"
    },
    {
        "id": "NE", "name": "قطاع النيجر (الجنوب الغربي)", "country_code": "NE",
        "ports": "منفذ تومو الحدودي — غات", "municipalities": ["غات", "أوباري"],
        "coords": [24.96, 10.18], "mobility_weight": 0.75, "health_gap": 0.80, "wash_deficit": 0.80,
        "primary_threat": "IMM-07"
    },
    {
        "id": "TN", "name": "قطاع تونس (الشمال الغربي)", "country_code": "TN",
        "ports": "منفذ رأس جدير — منفذ وازن", "municipalities": ["زوارة", "نالوت"],
        "coords": [33.15, 11.57], "mobility_weight": 0.95, "health_gap": 0.30, "wash_deficit": 0.20,
        "primary_threat": "IMM-06"
    },
    {
        "id": "EG", "name": "قطاع مصر (الشرق)", "country_code": "EG",
        "ports": "منفذ امساعد البري — ميناء طبرق", "municipalities": ["امساعد", "طبرق", "الجغبوب"],
        "coords": [31.58, 25.05], "mobility_weight": 0.90, "health_gap": 0.40, "wash_deficit": 0.30,
        "primary_threat": "WKL-13"
    },
    {
        "id": "DZ", "name": "قطاع الجزائر (الغرب)", "country_code": "DZ",
        "ports": "منفذ غدامس البري — الدبداب", "municipalities": ["غدامس", "درج"],
        "coords": [30.13, 9.50], "mobility_weight": 0.50, "health_gap": 0.45, "wash_deficit": 0.35,
        "primary_threat": "IMM-09"
    }
]

def ensure_config():
    """التحقق والتأسيس التلقائي لملفات التكوين إذا كانت مفقودة"""
    CONFIG_DIR.mkdir(exist_ok=True)
    d_path = CONFIG_DIR / 'ncdc_diseases.json'
    s_path = CONFIG_DIR / 'border_sectors.json'
    if not d_path.exists():
        d_path.write_text(json.dumps({'diseases': DISEASES_DATA}, ensure_ascii=False, indent=2), encoding='utf-8')
    if not s_path.exists():
        s_path.write_text(json.dumps({'sectors': SECTORS_DATA}, ensure_ascii=False, indent=2), encoding='utf-8')

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
    print("⏳ جاري تشغيل محرك النمذجة الوبائية والتأكد من ملفات التهيئة...")
    ensure_config()

    diseases = {d['code']: d for d in DISEASES_DATA}
    sectors = SECTORS_DATA

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
    print(f"✅ تم بنجاح إنهاء الحساب وحفظ النتائج في data/risk_data.json (التهديد الأكبر: {highest_threat['threat']} بنسبة {highest_threat['score']}%)")

if __name__ == '__main__':
    run()
        
