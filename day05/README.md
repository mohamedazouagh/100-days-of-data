# Day 05 - Dates and times with datetime

Almost every dataset has a date column, and it arrives as **text**. Comparing or sorting dates as
strings only works for ISO `YYYY-MM-DD`; anything else (`02/10/2026`, `Oct 2 2026`) has to be parsed
before you can do arithmetic or group by week or month.

Key points:
- `date.fromisoformat("2026-10-02")` parses ISO dates; `datetime.strptime(text, "%d/%m/%Y")` parses any other fixed format.
- `strftime` goes the other way: `d.strftime("%A %d %B")` → `Friday 02 October`.
- Subtracting two dates gives a `timedelta`; `.days` is the number of days between them. Add `timedelta(days=7)` to move forward a week.
- `d.weekday()` is 0 for Monday … 6 for Sunday; `d.isocalendar()` gives `(year, week, weekday)` - the usual key for "per week" grouping.
- Missing calendar days are easy to find: build the full range with `timedelta` and compare it to the dates you have.

Run it: `python day05/lesson.py`

## Exercise
`READINGS` in `solution.py` holds daily max temperatures with dates written as `DD/MM/YYYY`,
out of order, and with one day missing. Parse the dates, then:
1. print the average temperature per ISO week (`YYYY-Www`), in week order, rounded to 1 decimal;
2. print every calendar day between the first and last reading that has no reading;
3. print the weekend average and the weekday average.
Solution: `day05/solution.py`.
