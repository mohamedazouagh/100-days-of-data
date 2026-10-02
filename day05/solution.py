from collections import defaultdict
from datetime import datetime, timedelta

READINGS = [
    ("29/09/2026", 26.2),
    ("26/09/2026", 20.6),
    ("01/10/2026", 19.4),
    ("27/09/2026", 22.1),
    ("30/09/2026", 24.8),
    ("02/10/2026", 18.0),
    ("25/09/2026", 21.0),
    # 28/09/2026 is missing
]


def parse(readings):
    """Return [(date, temp)] sorted by date."""
    return sorted((datetime.strptime(d, "%d/%m/%Y").date(), t) for d, t in readings)


def weekly_averages(rows):
    weeks = defaultdict(list)
    for d, t in rows:
        year, week, _ = d.isocalendar()
        weeks[f"{year}-W{week:02d}"].append(t)
    return {k: round(sum(v) / len(v), 1) for k, v in sorted(weeks.items())}


def missing_days(rows):
    have = {d for d, _ in rows}
    first, last = rows[0][0], rows[-1][0]
    full = (first + timedelta(days=i) for i in range((last - first).days + 1))
    return [d.isoformat() for d in full if d not in have]


def weekend_vs_weekday(rows):
    weekend = [t for d, t in rows if d.weekday() >= 5]
    weekday = [t for d, t in rows if d.weekday() < 5]
    return round(sum(weekend) / len(weekend), 1), round(sum(weekday) / len(weekday), 1)


if __name__ == "__main__":
    rows = parse(READINGS)
    weekly = weekly_averages(rows)
    gaps = missing_days(rows)
    weekend, weekday = weekend_vs_weekday(rows)
    for week, avg in weekly.items():
        print(week, avg)
    print("missing:", gaps)
    print("weekend avg:", weekend, "| weekday avg:", weekday)

    # 25-27 Sep is W39 (Fri, Sat, Sun); 29 Sep - 2 Oct is W40
    assert weekly == {"2026-W39": 21.2, "2026-W40": 22.1}
    assert gaps == ["2026-09-28"]
    assert (weekend, weekday) == (21.4, 21.9)
