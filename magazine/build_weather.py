#!/usr/bin/env python3
"""Fill the five-day Mangaluru weather box from Open-Meteo.

Usage: build_weather.py PAGE.html

Source: https://open-meteo.com (api.open-meteo.com/v1/forecast), Mangaluru 12.9141 N, 74.856 E,
Asia/Kolkata. Model forecast, not an observation. The box states when it was fetched. If the
service cannot be reached the box says so; an old forecast is never left in place as if current.
The first run adds the box (and its CSS) to a page that has no weather slot yet.
"""
import datetime, html, json, re, sys, time, urllib.request

E = html.escape
URL = ("https://api.open-meteo.com/v1/forecast?latitude=12.9141&longitude=74.856&timezone=Asia%2FKolkata&forecast_days=5"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max")
WMO = {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle",
       55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
       66: "Freezing rain", 67: "Freezing rain", 80: "Light showers", 81: "Showers", 82: "Heavy showers",
       95: "Thunderstorm", 96: "Thunderstorm, hail", 99: "Thunderstorm, hail"}
CSS = """/* Weather */
.wx { margin-top: 30px; border-top: 4px solid var(--rule); padding-top: 12px; }
.wx-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0; margin-top: 10px; }
.wx-day { padding: 8px 12px; border-left: 1px solid var(--hair); }
.wx-day:first-child { border-left: 0; padding-left: 0; }
.wx-day b { display: block; font: 700 13px/1.2 var(--label); letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); }
.wx-day .t { font: 800 26px/1.15 var(--head); margin: 4px 0; }
.wx-day .t small { font: 500 17px/1 var(--head); color: var(--ink-2); }
.wx-day .c { font: 600 15px/1.3 var(--text); }
.wx-day .r { font: 400 14px/1.35 var(--text); color: var(--ink-2); margin-top: 2px; }
.wx-src { font: 500 12.5px/1.4 var(--label); letter-spacing: .05em; color: var(--ink-2); margin-top: 10px; }
.wx-src a { color: inherit; }
@media (max-width: 720px) { .wx-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); } .wx-day:nth-child(odd) { border-left: 0; padding-left: 0; } }

"""
SRC = '<a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo.com</a>'


def fetch(tries=5):
    req = urllib.request.Request(URL, headers={"User-Agent": "KullangalVaarte/1.0"})
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)


def box(data, now):
    d = data["daily"]
    cells = []
    for i, iso in enumerate(d["time"]):
        day = datetime.date.fromisoformat(iso)
        label = "Today" if i == 0 else day.strftime("%a %-d %b")
        code = d["weather_code"][i]
        cells.append(
            f'<div class="wx-day"><b>{E(label)}</b><div class="t">{round(d["temperature_2m_max"][i])}&deg;<small> / {round(d["temperature_2m_min"][i])}&deg;</small></div>'
            f'<div class="c">{E(WMO.get(code, "Weather code %d" % code))}</div>'
            f'<div class="r">Rain chance {d["precipitation_probability_max"][i]}%, {d["precipitation_sum"][i]:g} mm</div></div>')
    return ('<div class="wx" id="weather"><span class="kicker">Weather &middot; Mangaluru, next five days</span>'
            f'<div class="wx-grid">{"".join(cells)}</div>'
            f'<p class="wx-src">High / low in &deg;C. Forecast from {SRC}, a computer model for 12.91&deg;N 74.86&deg;E, fetched {now:%-d %B %Y, %H:%M} India time. '
            'It is a forecast, not an observation, and can change.</p></div>')


def unavailable(now):
    return ('<div class="wx" id="weather"><span class="kicker">Weather &middot; Mangaluru</span>'
            f'<p class="wx-src">The five-day forecast could not be fetched on {now:%-d %B %Y}. Source: {SRC}.</p></div>')


def main():
    page = sys.argv[1]
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    try:
        body = box(fetch(), now)
        status = "ok"
    except Exception as e:
        print("Weather fetch failed:", e, file=sys.stderr)
        body, status = unavailable(now), "unavailable"
    s = open(page, encoding="utf-8").read()
    if "<!--weather:start-->" not in s:
        s = s.replace("/* Colophon */", CSS + "/* Colophon */", 1)
        anchor = '<div class="kn" id="kullangal">'
        assert anchor in s, "run add_interactive.py first"
        s = s.replace(anchor, "<!--weather:start--><!--weather:end-->\n    " + anchor, 1)
    s = re.sub(r"<!--weather:start-->.*?<!--weather:end-->", lambda m: f"<!--weather:start-->{body}<!--weather:end-->", s, count=1, flags=re.S)
    open(page, "w", encoding="utf-8").write(s)
    print("Weather:", status)


if __name__ == "__main__":
    main()
