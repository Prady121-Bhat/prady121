#!/usr/bin/env python3
"""Five-day Mangaluru forecast from Open-Meteo (https://open-meteo.com), or None if it cannot be fetched."""
import datetime, json, sys, time, urllib.request

URL = ("https://api.open-meteo.com/v1/forecast?latitude=12.9141&longitude=74.856&timezone=Asia%2FKolkata&forecast_days=5"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max")
WMO = {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle",
       55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain", 80: "Light showers", 81: "Showers", 82: "Heavy showers",
       95: "Thunderstorm", 96: "Thunderstorm, hail", 99: "Thunderstorm, hail"}


def forecast(tries=5):
    req = urllib.request.Request(URL, headers={"User-Agent": "KullangalVaarte/1.0"})
    for i in range(tries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))["daily"]
            days = []
            for k, iso in enumerate(d["time"]):
                days.append(dict(date=datetime.date.fromisoformat(iso), hi=round(d["temperature_2m_max"][k]), lo=round(d["temperature_2m_min"][k]),
                                 sky=WMO.get(d["weather_code"][k], "Weather code %d" % d["weather_code"][k]),
                                 pop=d["precipitation_probability_max"][k], mm=d["precipitation_sum"][k], wind=round(d["wind_speed_10m_max"][k])))
            return days
        except Exception as e:
            print("weather retry:", str(e)[:80], file=sys.stderr)
            time.sleep(2 ** i)
    return None
