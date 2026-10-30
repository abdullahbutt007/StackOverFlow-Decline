"""
Pull Stack Overflow question counts from the public Stack Exchange API
and write the data files the dashboard reads.

What it fetches
  - Whole site: number of questions created in each calendar month
  - Tags (python, pandas, sql, excel, powerbi): questions created in each quarter

How it counts
  /2.3/questions with filter=total returns only {"total": N} for the
  fromdate/todate window (creation date). Deleted questions are not counted.

Quota
  Without a key the API allows 300 requests per IP per day. A full refresh
  with the default settings is about 280 requests, so run it once a day at
  most. Register a free key at https://stackapps.com/apps/oauth/register and
  set STACKEXCHANGE_KEY to raise the limit to 10,000 a day.

Usage
  pip install -r scripts/requirements.txt
  python scripts/fetch_data.py                 # Jan 2018 to last full month
  python scripts/fetch_data.py --start 2016    # longer history (more requests)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

API = "https://api.stackexchange.com/2.3/questions"
TAGS = ["python", "pandas", "sql", "excel", "powerbi"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def ts(y: int, m: int) -> int:
    """Unix timestamp for 00:00 UTC on the first day of month m (m may be 13)."""
    if m > 12:
        y, m = y + 1, m - 12
    return int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp())


def count(session: requests.Session, start: int, end: int, tag: str | None, key: str | None) -> int:
    """Questions created in [start, end). Retries politely on throttling."""
    params = {"site": "stackoverflow", "fromdate": start, "todate": end - 1, "filter": "total"}
    if tag:
        params["tagged"] = tag
    if key:
        params["key"] = key
    for attempt in range(5):
        r = session.get(API, params=params, timeout=60)
        body = r.json()
        if "total" in body:
            if "backoff" in body:  # API asks clients to pause before the next call
                time.sleep(int(body["backoff"]))
            return int(body["total"])
        err = body.get("error_name", r.status_code)
        if err == "throttle_violation" or r.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  throttled, waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        raise RuntimeError(f"API error {err}: {body.get('error_message', '')}")
    raise RuntimeError("Gave up after repeated throttling")


def last_full_month(today: date) -> tuple[int, int]:
    return (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=int, default=2018, help="first year to fetch (default 2018)")
    ap.add_argument("--delay", type=float, default=0.15, help="seconds between requests")
    args = ap.parse_args()

    key = os.environ.get("STACKEXCHANGE_KEY")
    end_y, end_m = last_full_month(date.today())
    # quarters must be complete too
    end_q_y, end_q = (end_y, end_m // 3) if end_m >= 3 else (end_y - 1, 4)

    months = [(y, m) for y in range(args.start, end_y + 1) for m in range(1, 13) if (y, m) <= (end_y, end_m)]
    quarters = [(y, q) for y in range(args.start, end_q_y + 1) for q in range(1, 5) if (y, q) <= (end_q_y, end_q)]
    total_calls = len(months) + len(quarters) * len(TAGS)
    print(f"{total_calls} requests ({len(months)} months, {len(quarters)} quarters x {len(TAGS)} tags)")
    if total_calls > 300 and not key:
        print("Warning: over the 300/day no-key quota. Set STACKEXCHANGE_KEY or use a later --start.", file=sys.stderr)

    s = requests.Session()
    s.headers["User-Agent"] = "stack-overflow-cliff-dashboard (github)"
    site: dict[str, int] = {}
    for i, (y, m) in enumerate(months, 1):
        site[f"{y}-{m:02d}"] = count(s, ts(y, m), ts(y, m + 1), None, key)
        print(f"  [{i}/{total_calls}] {y}-{m:02d}: {site[f'{y}-{m:02d}']:,}")
        time.sleep(args.delay)

    tags: dict[str, dict[str, int]] = {t: {} for t in TAGS}
    n = len(months)
    for tag in TAGS:
        for y, q in quarters:
            n += 1
            m0 = (q - 1) * 3 + 1
            tags[tag][f"{y}-Q{q}"] = count(s, ts(y, m0), ts(y, m0 + 3), tag, key)
            print(f"  [{n}/{total_calls}] {tag} {y}-Q{q}: {tags[tag][f'{y}-Q{q}']:,}")
            time.sleep(args.delay)

    data = {
        "pulled": date.today().isoformat(),
        "source": "Stack Exchange API v2.3, /questions?filter=total, filtered by creation date",
        "site": site,
        "tags": tags,
    }
    write_outputs(data)


def write_outputs(data: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "so_counts.json").write_text(json.dumps(data, indent=1))
    (DATA_DIR / "so_counts.js").write_text(
        "// Generated by scripts/fetch_data.py. Same data as so_counts.json, as a script so "
        "index.html also works when opened straight from disk.\n"
        f"window.SO_DATA = {json.dumps(data, separators=(',', ':'))};\n"
    )
    with open(DATA_DIR / "so_monthly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "questions"])
        w.writerows(sorted(data["site"].items()))
    with open(DATA_DIR / "so_tags_quarterly.csv", "w", newline="") as f:
        w = csv.writer(f)
        tags = list(data["tags"])
        w.writerow(["quarter", *tags])
        for q in sorted(data["tags"][tags[0]]):
            w.writerow([q, *(data["tags"][t][q] for t in tags)])
    print(f"Wrote data files to {DATA_DIR}")


if __name__ == "__main__":
    main()
