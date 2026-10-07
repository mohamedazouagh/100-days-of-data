import heapq
from collections import defaultdict
from operator import itemgetter
from statistics import mean

# Fictional quiz results
RESULTS = [
    {"name": "Ada", "team": "red", "score": 9, "seconds": 41},
    {"name": "Ben", "team": "blue", "score": 7, "seconds": 30},
    {"name": "Cleo", "team": "red", "score": 9, "seconds": 41},
    {"name": "Dev", "team": "green", "score": 10, "seconds": 55},
    {"name": "Eli", "team": "blue", "score": 9, "seconds": 38},
    {"name": "Fay", "team": "green", "score": 6, "seconds": 20},
    {"name": "Gus", "team": "red", "score": 5, "seconds": 25},
    {"name": "Hana", "team": "blue", "score": 9, "seconds": 38},
]


def performance(row):
    """Higher is better: more points first, then less time."""
    return row["score"], -row["seconds"]


def leaderboard(rows):
    return sorted(rows, key=lambda r: (-r["score"], r["seconds"], r["name"]))


def competition_ranks(board):
    """(name, rank) pairs; equal performance shares a rank and the next rank skips (1, 2, 2, 4)."""
    out, prev = [], None
    for position, row in enumerate(board, start=1):
        if performance(row) != prev:
            rank, prev = position, performance(row)
        out.append((row["name"], rank))
    return out


def top_per_team(rows, n=2):
    by_team = defaultdict(list)
    for row in rows:
        by_team[row["team"]].append(row)
    return {team: [r["name"] for r in heapq.nlargest(n, members, key=performance)]
            for team, members in sorted(by_team.items())}


def best_team(rows):
    by_team = defaultdict(list)
    for row in rows:
        by_team[row["team"]].append(row["score"])
    averages = {team: mean(scores) for team, scores in by_team.items()}
    team = min(averages, key=lambda t: (-averages[t], t))
    return team, round(averages[team], 2)


if __name__ == "__main__":
    board = leaderboard(RESULTS)
    names = [r["name"] for r in board]
    ranks = competition_ranks(board)
    tops = top_per_team(RESULTS)
    team = best_team(RESULTS)
    print("leaderboard:", names)
    print("ranks:", ranks)
    print("top 2 per team:", tops)
    print("best team:", team)

    assert names == ["Dev", "Eli", "Hana", "Ada", "Cleo", "Ben", "Fay", "Gus"]
    assert ranks == [("Dev", 1), ("Eli", 2), ("Hana", 2), ("Ada", 4), ("Cleo", 4),
                     ("Ben", 6), ("Fay", 7), ("Gus", 8)]
    assert tops == {"blue": ["Eli", "Hana"], "green": ["Dev", "Fay"], "red": ["Ada", "Cleo"]}
    assert team == ("blue", 8.33)
    assert sorted(RESULTS, key=itemgetter("seconds"))[0]["name"] == "Fay"  # input untouched by sorted()
    print("all checks passed")
