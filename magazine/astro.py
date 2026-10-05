#!/usr/bin/env python3
"""Sunrise, sunset and moon phase for Mangaluru, calculated (no network).

Sun times use the NOAA solar equations and are good to about a minute. Moon phase uses the mean
synodic month from the new moon of 6 Jan 2000 and is good to about a day.
"""
import datetime, math

LAT, LON, TZ = 12.9141, 74.856, 5.5


def sun_times(day):
    n = day.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1)
    eq = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    lat = math.radians(LAT)
    cosha = math.cos(math.radians(90.833)) / (math.cos(lat) * math.cos(decl)) - math.tan(lat) * math.tan(decl)
    ha = math.degrees(math.acos(max(-1, min(1, cosha))))
    rise = 720 - 4 * (LON + ha) - eq + TZ * 60
    sset = 720 - 4 * (LON - ha) - eq + TZ * 60
    fmt = lambda m: f"{int(m // 60) % 24}:{int(round(m % 60)) % 60:02d}"
    return fmt(rise), fmt(sset), sset - rise


def moon(day):
    base = datetime.datetime(2000, 1, 6, 18, 14)
    now = datetime.datetime(day.year, day.month, day.day, 6, 0)
    age = ((now - base).total_seconds() / 86400) % 29.530588853
    frac = (1 - math.cos(2 * math.pi * age / 29.530588853)) / 2
    names = [(1.85, "ಅಮಾವಾಸ್ಯೆ"), (5.53, "ಬೆಳೆಯುತ್ತಿರುವ ಚಂದ್ರ, ಚಿಕ್ಕ ಕಲೆ"), (9.22, "ಬೆಳೆಯುತ್ತಿರುವ ಅರ್ಧ ಚಂದ್ರ"), (12.91, "ಬೆಳೆಯುತ್ತಿರುವ ಚಂದ್ರ, ದೊಡ್ಡ ಕಲೆ"),
             (16.61, "ಹುಣ್ಣಿಮೆ"), (20.30, "ಕ್ಷೀಣಿಸುತ್ತಿರುವ ಚಂದ್ರ, ದೊಡ್ಡ ಕಲೆ"), (23.99, "ಕ್ಷೀಣಿಸುತ್ತಿರುವ ಅರ್ಧ ಚಂದ್ರ"), (27.68, "ಕ್ಷೀಣಿಸುತ್ತಿರುವ ಚಂದ್ರ, ಚಿಕ್ಕ ಕಲೆ"), (99, "ಅಮಾವಾಸ್ಯೆ")]
    name = next(n for lim, n in names if age < lim)
    return name, round(frac * 100), round(age, 1)


if __name__ == "__main__":
    import sys
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    print(sun_times(d), moon(d))
