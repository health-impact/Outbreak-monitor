"""
ملف تأسيس قاعدة بيانات الأمراض والقطاعات
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = ROOT / 'config'
CONFIG_DIR.mkdir(exist_ok=True)

# 1. قائمة الـ 48 مرضاً المعتمدة رسمياً
DISEASES = [
    # الفئة الأولى: التبليغ الفوري (19 مرضاً)
    {"code": "IMM-01", "name_ar": "الشلل الرخو الحاد", "name_en": "Acute Flaccid Paralysis", "reporting_tier": "immediate", "transmission_mode": "fecal_oral", "incubation_max": 35, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 5.0, "kw": ["شلل رخو", "polio", "afp", "flaccid paralysis"]},
    {"code": "IMM-02", "name_ar": "الجمرة الخبيثة", "name_en": "Anthrax", "reporting_tier": "immediate", "transmission_mode": "zoonotic_contact", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 20.0, "kw": ["الجمرة الخبيثة", "anthrax"]},
    {"code": "IMM-03", "name_ar": "الهيضة (الكوليرا)", "name_en": "Cholera", "reporting_tier": "immediate", "transmission_mode": "waterborne", "incubation_max": 5, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 1.5, "kw": ["الكوليرا", "الهيضة", "cholera"]},
    {"code": "IMM-04", "name_ar": "الخناق (الدفتيريا)", "name_en": "Diphtheria", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 5, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 10.0, "kw": ["الدفتيريا", "الخناق", "diphtheria"]},
    {"code": "IMM-05", "name_ar": "التسمم الغذائي", "name_en": "Food Poisoning", "reporting_tier": "immediate", "transmission_mode": "foodborne", "incubation_max": 2, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 0.5, "kw": ["تسمم غذائي", "food poisoning"]},
    {"code": "IMM-06", "name_ar": "الحصبة", "name_en": "Measles", "reporting_tier": "immediate", "transmission_mode": "airborne_aerosol", "incubation_max": 18, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 3.0, "kw": ["الحصبة", "measles"]},
    {"code": "IMM-07", "name_ar": "الالتهاب السحائي الوبائي", "name_en": "Meningococcal Meningitis", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 10, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 12.0, "kw": ["حزام السحايا", "سحايا وبائي", "meningococcal"]},
    {"code": "IMM-08", "name_ar": "التهاب السحايا بالمكورات الأخرى", "name_en": "Meningitis Unspecified", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 10.0, "kw": ["سحايا", "meningitis"]},
    {"code": "IMM-09", "name_ar": "الحميات النزفية الفيروسية", "name_en": "Viral Hemorrhagic Fevers", "reporting_tier": "immediate", "transmission_mode": "vector_and_contact", "incubation_max": 21, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 40.0, "kw": ["حمى نزفية", "إيبولا", "ماربورغ", "لاسا", "vhf", "ebola", "marburg", "lassa"]},
    {"code": "IMM-10", "name_ar": "الطاعون", "name_en": "Plague", "reporting_tier": "immediate", "transmission_mode": "vector_and_contact", "incubation_max": 7, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 30.0, "kw": ["طاعون", "plague"]},
    {"code": "IMM-11", "name_ar": "الحصبة الألمانية", "name_en": "Rubella", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.2, "kw": ["حصبة ألمانية", "rubella"]},
    {"code": "IMM-12", "name_ar": "داء الكلب", "name_en": "Rabies", "reporting_tier": "immediate", "transmission_mode": "zoonotic_bite", "incubation_max": 90, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 99.0, "kw": ["داء الكلب", "السعار", "rabies"]},
    {"code": "IMM-13", "name_ar": "لدغة الثعبان", "name_en": "Snake Bite", "reporting_tier": "immediate", "transmission_mode": "environmental", "incubation_max": 1, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 2.0, "kw": ["لدغة ثعبان", "snake bite"]},
    {"code": "IMM-14", "name_ar": "لدغة العقرب", "name_en": "Scorpion Bite", "reporting_tier": "immediate", "transmission_mode": "environmental", "incubation_max": 1, "climate_sensitive": True, "is_cross_border": False, "cfr_bench": 0.8, "kw": ["لدغة عقرب", "scorpion sting"]},
    {"code": "IMM-15", "name_ar": "الكزاز الوليدي", "name_en": "Tetanus Neonatorum", "reporting_tier": "immediate", "transmission_mode": "unhygienic_delivery", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 70.0, "kw": ["كزاز وليدي", "neonatal tetanus"]},
    {"code": "IMM-16", "name_ar": "التيفوس الوبائي", "name_en": "Epidemic Typhus", "reporting_tier": "immediate", "transmission_mode": "vector_lice", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 15.0, "kw": ["تيفوس وبائي", "typhus"]},
    {"code": "IMM-17", "name_ar": "الشاهوق (السعال الديكي)", "name_en": "Whooping Cough", "reporting_tier": "immediate", "transmission_mode": "airborne_droplet", "incubation_max": 10, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0, "kw": ["سعال ديكي", "شاهوق", "pertussis", "whooping cough"]},
    {"code": "IMM-18", "name_ar": "الحمى الصفراء", "name_en": "Yellow Fever", "reporting_tier": "immediate", "transmission_mode": "vector_mosquito", "incubation_max": 6, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 25.0, "kw": ["الحمى الصفراء", "yellow fever"]},
    {"code": "IMM-19", "name_ar": "طوارئ وبائية مستجدة / جدري القردة", "name_en": "PHEIC / Mpox / Novel", "reporting_tier": "immediate", "transmission_mode": "emerging_unknown", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 10.0, "kw": ["جدري القردة", "مرض غامض", "mpox", "disease x", "pheic"]},

    # الفئة الثانية: التبليغ الأسبوعي (29 مرضاً)
    {"code": "WKL-01", "name_ar": "الإسهالات الحادة", "name_en": "Acute Diarrhea", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 3, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.5, "kw": ["إسهال حاد", "acute diarrhea"]},
    {"code": "WKL-02", "name_ar": "الزحار الأميبي", "name_en": "Amoebiasis", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 28, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.3, "kw": ["زحار أميبي", "amoebiasis"]},
    {"code": "WKL-03", "name_ar": "عضة الحيوان", "name_en": "Animal Bite", "reporting_tier": "weekly", "transmission_mode": "zoonotic_contact", "incubation_max": 2, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.0, "kw": ["عضة حيوان", "animal bite"]},
    {"code": "WKL-04", "name_ar": "الحمى المالطية (البروسيلا)", "name_en": "Brucellosis", "reporting_tier": "weekly", "transmission_mode": "zoonotic_foodborne", "incubation_max": 60, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0, "kw": ["حمى مالطية", "بروسيلا", "brucellosis"]},
    {"code": "WKL-05", "name_ar": "الجديري المائي", "name_en": "Chickenpox", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.05, "kw": ["جديري مائي", "chickenpox"]},
    {"code": "WKL-06", "name_ar": "الليشمانيا الجلدية", "name_en": "Cutaneous Leishmaniasis", "reporting_tier": "weekly", "transmission_mode": "vector_sandfly", "incubation_max": 180, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.01, "kw": ["ليشمانيا جلدية", "حبة حلب", "leishmaniasis"]},
    {"code": "WKL-07", "name_ar": "الأكياس العدارية المائية", "name_en": "Echinococcosis", "reporting_tier": "weekly", "transmission_mode": "zoonotic_fecal_oral", "incubation_max": 3650, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 2.0, "kw": ["أكياس مائية", "echinococcosis"]},
    {"code": "WKL-08", "name_ar": "السيلان", "name_en": "Gonococcal Infection", "reporting_tier": "weekly", "transmission_mode": "sexual", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.0, "kw": ["سيلان", "gonorrhea"]},
    {"code": "WKL-09", "name_ar": "التهاب الكبد الفيروسي أ", "name_en": "Hepatitis A", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 50, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.3, "kw": ["التهاب كبد أ", "hepatitis a"]},
    {"code": "WKL-10", "name_ar": "التهاب الكبد الفيروسي ب", "name_en": "Hepatitis B", "reporting_tier": "weekly", "transmission_mode": "bloodborne", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0, "kw": ["التهاب كبد ب", "hepatitis b"]},
    {"code": "WKL-11", "name_ar": "التهاب الكبد الفيروسي ج", "name_en": "Hepatitis C", "reporting_tier": "weekly", "transmission_mode": "bloodborne", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.5, "kw": ["التهاب كبد ج", "hepatitis c"]},
    {"code": "WKL-12", "name_ar": "متلازمة العوز المناعي (الإيدز)", "name_en": "HIV (AIDS)", "reporting_tier": "weekly", "transmission_mode": "bloodborne_and_sexual", "incubation_max": 3650, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 20.0, "kw": ["إيدز", "hiv", "aids"]},
    {"code": "WKL-13", "name_ar": "الأنفلونزا الموسمية", "name_en": "Influenza (Seasonal)", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 4, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.1, "kw": ["إنفلونزا", "influenza", "flu"]},
    {"code": "WKL-14", "name_ar": "الجذام", "name_en": "Leprosy", "reporting_tier": "weekly", "transmission_mode": "close_contact", "incubation_max": 7300, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 0.1, "kw": ["جذام", "leprosy"]},
    {"code": "WKL-15", "name_ar": "البرداء (الملاريا)", "name_en": "Malaria", "reporting_tier": "weekly", "transmission_mode": "vector_mosquito", "incubation_max": 30, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 2.0, "kw": ["ملاريا", "البرداء", "malaria"]},
    {"code": "WKL-16", "name_ar": "الدرن المقاوم للأدوية (MDR-TB)", "name_en": "MDR-TB", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 15.0, "kw": ["درن مقاوم", "mdr-tb"]},
    {"code": "WKL-17", "name_ar": "النكاف", "name_en": "Mumps", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 25, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 0.05, "kw": ["نكاف", "mumps"]},
    {"code": "WKL-18", "name_ar": "الكزاز غير الوليدي", "name_en": "Other Tetanus", "reporting_tier": "weekly", "transmission_mode": "wound_soil", "incubation_max": 21, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 20.0, "kw": ["تيتانوس", "tetanus"]},
    {"code": "WKL-19", "name_ar": "الدرن الرئوي (السل)", "name_en": "Pulmonary Tuberculosis", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 180, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 5.0, "kw": ["سل رئوي", "tuberculosis", "tb"]},
    {"code": "WKL-20", "name_ar": "حمى الريكتسيا", "name_en": "Rickettsioses", "reporting_tier": "weekly", "transmission_mode": "vector_tick_flea", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 2.5, "kw": ["ريكتسيا", "rickettsia"]},
    {"code": "WKL-21", "name_ar": "البلهارسيا", "name_en": "Schistosomiasis", "reporting_tier": "weekly", "transmission_mode": "water_snail", "incubation_max": 60, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.1, "kw": ["بلهارسيا", "schistosoma"]},
    {"code": "WKL-22", "name_ar": "الزهري", "name_en": "Syphilis", "reporting_tier": "weekly", "transmission_mode": "sexual", "incubation_max": 90, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 1.0, "kw": ["زهري", "syphilis"]},
    {"code": "WKL-23", "name_ar": "الدرن خارج الرئة", "name_en": "Extra-Pulmonary TB", "reporting_tier": "weekly", "transmission_mode": "internal", "incubation_max": 365, "climate_sensitive": False, "is_cross_border": False, "cfr_bench": 5.0, "kw": ["درن خارج الرئة"]},
    {"code": "WKL-24", "name_ar": "التيفويد والباراتيفويد", "name_en": "Typhoid & Paratyphoid", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 30, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 1.5, "kw": ["تيفويد", "typhoid"]},
    {"code": "WKL-25", "name_ar": "التهاب كبدي غير محدد (E)", "name_en": "Hepatitis Unspecified (E)", "reporting_tier": "weekly", "transmission_mode": "waterborne", "incubation_max": 60, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 4.0, "kw": ["التهاب كبد هـ", "hepatitis e"]},
    {"code": "WKL-26", "name_ar": "الليشمانيا الحشوية (الكالازار)", "name_en": "Visceral Leishmaniasis", "reporting_tier": "weekly", "transmission_mode": "vector_sandfly", "incubation_max": 240, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 10.0, "kw": ["كالازار", "kala-azar"]},
    {"code": "WKL-27", "name_ar": "الفيروس التنفسي المخلوي (RSV)", "name_en": "Respiratory Syncytial Virus", "reporting_tier": "weekly", "transmission_mode": "airborne_droplet", "incubation_max": 8, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 0.2, "kw": ["تنفسي مخلوي", "rsv"]},
    {"code": "WKL-28", "name_ar": "التهاب الدماغ (غرب النيل)", "name_en": "Encephalitis / West Nile", "reporting_tier": "weekly", "transmission_mode": "vector_mosquito", "incubation_max": 14, "climate_sensitive": True, "is_cross_border": True, "cfr_bench": 8.0, "kw": ["غرب النيل", "west nile"]},
    {"code": "WKL-29", "name_ar": "كوفيد-19", "name_en": "COVID-19", "reporting_tier": "weekly", "transmission_mode": "airborne_aerosol", "incubation_max": 14, "climate_sensitive": False, "is_cross_border": True, "cfr_bench": 1.0, "kw": ["كوفيد", "covid-19"]}
]

# 2. مصفوفة القطاعات الحدودية الست
SECTORS = [
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

(CONFIG_DIR / 'ncdc_diseases.json').write_text(json.dumps({'diseases': DISEASES}, ensure_ascii=False, indent=2), encoding='utf-8')
(CONFIG_DIR / 'border_sectors.json').write_text(json.dumps({'sectors': SECTORS}, ensure_ascii=False, indent=2), encoding='utf-8')
print("✅ تم إنشاء ملفات التكوين بنجاح داخل مجلد config/")
