#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_who_data.py
-------------------
يسحب هذا السكربت أحدث بلاغات "Disease Outbreak News" من الواجهة الرسمية
لمنظمة الصحة العالمية (WHO)، ويُصفّيها للاحتفاظ فقط بالبلاغات الخاصة
بالدول المجاورة لليبيا (تونس، الجزائر، مصر، السودان، تشاد، النيجر)،
ثم يكتبها في ملف who_data.json ليقرأه موقع "أثر رصد" مباشرة.

يعمل هذا السكربت من خادم (GitHub Actions) وليس من متصفح المستخدم،
لذلك لا يتأثر بسياسات CORS التي قد تمنع الاتصال المباشر من المتصفح.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone

WHO_ENDPOINT = (
    "https://www.who.int/api/news/diseaseoutbreaknews"
    "?$orderby=PublicationDateAndTime%20desc&$top=60"
)

COUNTRIES = [
    {"id": "tunisia", "ar": "تونس",   "en": "Tunisia", "keywords": ["tunisia"]},
    {"id": "algeria", "ar": "الجزائر", "en": "Algeria", "keywords": ["algeria"]},
    {"id": "egypt",   "ar": "مصر",    "en": "Egypt",   "keywords": ["egypt"]},
    {"id": "sudan",   "ar": "السودان", "en": "Sudan",   "keywords": ["sudan"]},
    {"id": "chad",    "ar": "تشاد",   "en": "Chad",    "keywords": ["chad"]},
    {"id": "niger",   "ar": "النيجر", "en": "Niger",   "keywords": ["niger"]},
]

OUTPUT_FILE = "who_data.json"


def fetch_who_data():
    req = urllib.request.Request(
        WHO_ENDPOINT,
        headers={"Accept": "application/json", "User-Agent": "AtharRasd-EWS/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def match_countries(title: str):
    lower = title.lower()
    matched = []
    for c in COUNTRIES:
        if any(kw in lower for kw in c["keywords"]):
            matched.append(c["id"])
    return matched


def build_report(item, country_id):
    return {
        "id": "live-" + str(item.get("Id", "")),
        "countryId": country_id,
        "titleAr": item.get("Title", ""),
        "titleEn": item.get("Title", ""),
        "summary": item.get("Summary", "") or "",
        "date": (item.get("PublicationDateAndTime") or "")[:10],
        "source": "https://www.who.int" + (item.get("ItemDefaultUrl") or ""),
        "donId": item.get("DonId", ""),
    }


def main():
    try:
        data = fetch_who_data()
    except Exception as exc:  # noqa: BLE001
        print(f"[update_who_data] فشل الاتصال بواجهة WHO: {exc}", file=sys.stderr)
        # لا نكسر البناء إن فشل الاتصال؛ نكتب حالة خطأ بدل تعطيل الموقع بالكامل
        output = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(exc),
            "reports": [],
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        sys.exit(0)  # ننهي بنجاح حتى لا يفشل الـ workflow، لكن الحالة موثقة داخل الملف

    items = data.get("value", [])
    reports = []
    for item in items:
        title = (item.get("Title") or "") + " " + (item.get("OverrideTitle") or "")
        for country_id in match_countries(title):
            reports.append(build_report(item, country_id))

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "checkedItems": len(items),
        "matchedReports": len(reports),
        "reports": reports,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[update_who_data] تم فحص {len(items)} بلاغ، وجد {len(reports)} بلاغ مطابق لجيران ليبيا.")


if __name__ == "__main__":
    main()
