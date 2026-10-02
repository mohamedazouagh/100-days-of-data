from datetime import date, datetime, timedelta

ROWS = [
    ("2026-09-26", 20.6),
    ("2026-09-27", 22.1),
    ("2026-09-29", 26.2),
    ("2026-09-30", 24.8),
]


if __name__ == "__main__":
    # 1. Parse ISO strings into real dates
    days = [date.fromisoformat(d) for d, _ in ROWS]
    print(days[0], type(days[0]).__name__)

    # 2. Other formats need strptime with an explicit pattern
    print(datetime.strptime("02/10/2026", "%d/%m/%Y").date())

    # 3. Formatting back to text
    print(days[0].strftime("%A %d %B %Y"))

    # 4. Arithmetic: differences are timedeltas
    span = days[-1] - days[0]
    print(span, "->", span.days, "days")
    print("one week later:", days[0] + timedelta(weeks=1))

    # 5. Weekday and ISO week for grouping
    for d in days:
        year, week, _ = d.isocalendar()
        kind = "weekend" if d.weekday() >= 5 else "weekday"
        print(d, f"{year}-W{week:02d}", kind)

    # 6. Find missing calendar days in the range
    have = set(days)
    full = [days[0] + timedelta(days=i) for i in range(span.days + 1)]
    print("missing:", [d.isoformat() for d in full if d not in have])
