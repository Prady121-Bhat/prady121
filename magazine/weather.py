#!/usr/bin/env python3
"""Five-day Mangaluru forecast from Open-Meteo (https://open-meteo.com), or None if it cannot be fetched."""
import datetime, json, sys, time, urllib.request

URL = ("https://api.open-meteo.com/v1/forecast?latitude=12.9141&longitude=74.856&timezone=Asia%2FKolkata&forecast_days=5"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max")
WMO = {0: "ಶುಭ್ರ ಆಕಾಶ", 1: "ಬಹುತೇಕ ಶುಭ್ರ", 2: "ಭಾಗಶಃ ಮೋಡ", 3: "ಮೋಡ ಕವಿದಿದೆ", 45: "ಮಂಜು", 48: "ಮಂಜು", 51: "ಹಗುರ ಸಿಂಚನ", 53: "ಸಿಂಚನ",
       55: "ಭಾರಿ ಸಿಂಚನ", 61: "ಹಗುರ ಮಳೆ", 63: "ಮಳೆ", 65: "ಭಾರಿ ಮಳೆ", 80: "ಹಗುರ ಮಳೆ ಸರಿ", 81: "ಮಳೆ ಸರಿ", 82: "ಭಾರಿ ಮಳೆ ಸರಿ",
       95: "ಗುಡುಗು ಸಹಿತ ಮಳೆ", 96: "ಗುಡುಗು, ಆಲಿಕಲ್ಲು", 99: "ಗುಡುಗು, ಆಲಿಕಲ್ಲು"}


def forecast(tries=5):
    req = urllib.request.Request(URL, headers={"User-Agent": "KullangalVaarte/1.0"})
    for i in range(tries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))["daily"]
            days = []
            for k, iso in enumerate(d["time"]):
                days.append(dict(date=datetime.date.fromisoformat(iso), hi=round(d["temperature_2m_max"][k]), lo=round(d["temperature_2m_min"][k]),
                                 sky=WMO.get(d["weather_code"][k], "ಹವಾಮಾನ ಸಂಕೇತ %d" % d["weather_code"][k]),
                                 pop=d["precipitation_probability_max"][k], mm=d["precipitation_sum"][k], wind=round(d["wind_speed_10m_max"][k])))
            return days
        except Exception as e:
            print("weather retry:", str(e)[:80], file=sys.stderr)
            time.sleep(2 ** i)
    return None
