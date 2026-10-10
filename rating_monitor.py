#!/usr/bin/env python3
"""MoveInSync Play Store rating monitor — answers 'How are our ratings?' weekly.
Usage: python rating_monitor.py [--baseline baseline.json] [--count 100] [--notify]
First run creates baseline.json. Later runs diff the P0 clusters from the FDE memo.
Built as the reusable FDE asset for the MoveInSync candidate assignment (Oct 2026).
"""
import argparse, json, os, datetime
from google_play_scraper import app, reviews, Sort

APP_ID = "com.moveinsync.ets"
CLUSTERS = {
    "booking_date_fail": ["book", "schedule", "roster", "wrong date", "next day"],
    "crash_freeze_slow": ["crash", "freeze", "hang", "stuck", "slow", "lag", "loading", "glitch"],
    "login_otp_logout": ["login", "log in", "logout", "logged out", "otp", "session"],
    "gps_eta_wrong": ["gps", "location", "tracking", "live track", "eta", "map"],
    "ui_regression": ["update", "ui ", "interface", "confus", "difficult to use", "redesign"],
    "cablate_support": ["late", "driver", "no cab", "missed", "support", "helpdesk", "helpline", "no show", "no-show"],
}

def snapshot(count=100):
    meta = app(APP_ID, lang="en", country="in")
    rows = []
    for score in (1, 2):
        r, _ = reviews(APP_ID, lang="en", country="in", sort=Sort.NEWEST,
                       count=count, filter_score_with=score)
        rows.extend(r)
    texts = [str(x.get("content", "")).lower() for x in rows]
    clusters = {k: sum(1 for t in texts if any(w in t for w in ws))
                for k, ws in CLUSTERS.items()}
    return {
        "date": datetime.date.today().isoformat(),
        "score": round(float(meta["score"]), 4),
        "ratings_total": int(meta["ratings"]),
        "histogram": [int(x) for x in meta.get("histogram", [])],
        "one_star_share": round(int(meta["histogram"][0]) / int(meta["ratings"]), 4),
        "low_sample_n": len(rows),
        "p0_clusters_in_1_2star": clusters,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="baseline.json")
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--notify", action="store_true")
    a = ap.parse_args()
    snap = snapshot(a.count)
    print(f"=== MoveInSync ratings brief — {snap['date']} ===")
    print(f"Score: {snap['score']} across {snap['ratings_total']:,} ratings "
          f"| 1-star share: {snap['one_star_share']*100:.2f}%")
    print("P0 clusters in newest 1-2 star sample:")
    for k, v in snap["p0_clusters_in_1_2star"].items():
        print(f"  {k}: {v}/{snap['low_sample_n']}")
    if os.path.exists(a.baseline):
        base = json.load(open(a.baseline))
        d = round(snap["score"] - base["score"], 4)
        d1 = snap["histogram"][0] - base["histogram"][0]
        print(f"Delta vs {base['date']}: score {d:+.4f}, 1-star count {d1:+d}")
        worst = max(snap["p0_clusters_in_1_2star"], key=snap["p0_clusters_in_1_2star"].get)
        print(f"Loudest cluster right now: {worst} — staff it first Monday.")
        if a.notify:
            print(f"[notify] Score {snap['score']} ({d:+.4f}) | 1-star {snap['one_star_share']*100:.2f}% | top: {worst}")
    else:
        json.dump(snap, open(a.baseline, "w"), indent=2)
        print(f"Baseline saved to {a.baseline}. Re-run weekly with --notify.")

if __name__ == "__main__":
    main()
