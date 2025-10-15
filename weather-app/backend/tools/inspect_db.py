#!/usr/bin/env python3
"""Inspect the SQLite weather DB and print the `queries` table neatly.

Usage:
  python backend/tools/inspect_db.py            # print markdown table to stdout
  python backend/tools/inspect_db.py --csv out.csv
  python backend/tools/inspect_db.py --json out.json
  python backend/tools/inspect_db.py --limit 50

This script uses only the Python stdlib so no extra deps are needed.
"""
import sqlite3
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def rows_to_markdown(headers, rows):
    # compute column widths
    widths = [len(h) for h in headers]
    for r in rows:
        for i, v in enumerate(r):
            s = '' if v is None else str(v)
            widths[i] = max(widths[i], len(s))

    def fmt_row(row):
        return '| ' + ' | '.join((str(v) if v is not None else '') .ljust(widths[i]) for i, v in enumerate(row)) + ' |'

    header = fmt_row(headers)
    sep = '| ' + ' | '.join('-' * w for w in widths) + ' |'
    body = '\n'.join(fmt_row(r) for r in rows)
    return '\n'.join([header, sep, body])


def main():
    p = argparse.ArgumentParser(description='Inspect weather sqlite DB queries table')
    p.add_argument('--db', default='weather.db', help='Path to SQLite DB (default: weather.db)')
    p.add_argument('--limit', type=int, default=100, help='Max rows to fetch')
    p.add_argument('--csv', help='Write CSV to this file')
    p.add_argument('--json', help='Write JSON to this file')
    args = p.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"DB file not found: {db_path.resolve()}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Found tables: {', '.join(tables)}\n")

    # If queries table exists, dump it
    if 'queries' not in tables:
        print("No `queries` table found in this DB.")
        return

    cur.execute(f"SELECT * FROM queries ORDER BY created_at DESC LIMIT ?", (args.limit,))
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]

    # Print markdown table
    if rows:
        md = rows_to_markdown(headers, [tuple(r) for r in rows])
        print(md)
    else:
        print("No records found in `queries`.")

    #  exports
    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in rows:
                writer.writerow([r[h] for h in headers])
        print(f"\nWrote CSV to {args.csv}")

    if args.json:
        out = [dict(r) for r in rows]
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\nWrote JSON to {args.json}")


if __name__ == '__main__':
    main()
