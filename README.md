# 🟢 MoveInSync FDE — Play Store Ratings: Why 4.64★ Lies + 30-Day Fix

![stars](https://img.shields.io/badge/rating-4.64★%20·%20114k-green) ![reviews](https://img.shields.io/badge/reviews-2000%20scraped-blue) ![repro](https://img.shields.io/badge/repro-one%20command-orange) ![role](https://img.shields.io/badge/FDE-intern→FTE-purple)

> **Candidate: Sam · Forward Deployed Engineer (Intern → FTE) · Oct 2026**
> Live data: `com.moveinsync.ets` · 114,849 ratings · 2,000 newest reviews scraped Oct 10 2026

## 🌐 Live interactive report — read this first

### 👉 https://akashchaudhary93.github.io/moveinsync-fde-ratings/moveinsync_report.html

Charts, journey breaks, 30-day roadmap, file guide. *(If Pages is still deploying, open `moveinsync_report.html` in this repo directly — same content.)*

---

## TL;DR

Headline **4.64★ looks healthy. It isn't.** Distribution is bimodal: **85.4% five-star (98,141) vs 6.4% one-star (7,338)** — classic captive-audience signature (employees must use it; happy path rates 5★, every failure rates 1★).

Six failure factories manufacture the 1★s. Fix the P0s in 2 weeks → convert ~1,500–2,500 1★/yr, **+0.05–0.10** on the rolling average, 1★ share **6.4% → ~4–5%** (the number enterprise buyers screenshot).

| # | 1★ factory | 1★ rate | 2★ rate |
|---|------------|---------|---------|
| 1 | 📅 Self-booking / wrong date / schedule bugs | 17.5% | **26.0%** |
| 2 | 🧊 Crash / freeze / slow / stuck-after-update | 14.0% | 18.5% |
| 3 | 🔐 Login / OTP / forced logout loop | 11.8% | 12.0% |
| 4 | 📍 GPS / live-track / ETA wrong | 11.5% | 17.5% |
| 5 | 🎨 UI regression (2-step shuttle, clutter) | 11.2% | 18.8% |
| 6 | 🚕 Cab late / no cab / dead support line | 10.0% | 14.0% |

Amplifiers: wrong **No-Show → salary cut** (highest rage per incident), one-tap **Cancel with no confirm**, offline gate dead-zones wiping OTP/driver card, contradictory "trip not booked" push after success.

---

## 📁 What's in this repo

| File | What it is | Open / run |
|------|------------|------------|
| 🌐 `moveinsync_report.html` | Full visual report (the site) | [open live](https://akashchaudhary93.github.io/moveinsync-fde-ratings/moveinsync_report.html) |
| 📝 `MoveInSync_FDE_Submission.md` | The memo: diagnosis + 30-day plan + JD tie-in + method | [read](https://github.com/AkashChaudhary93/moveinsync-fde-ratings/blob/main/MoveInSync_FDE_Submission.md) |
| 📊 `moveinsync_reviews_raw.csv` | 2,000 real reviews (400/star) — open in Excel | [view](https://github.com/AkashChaudhary93/moveinsync-fde-ratings/blob/main/moveinsync_reviews_raw.csv) |
| ⬇️ `MoveInSync_scrape.py` | Re-pulls live Play data | `python MoveInSync_scrape.py` |
| 🔍 `MoveInSync_analyze.py` | Theme rates + quotes + version cuts | `python MoveInSync_analyze.py` |
| 🤖 `rating_monitor.py` | **Reusable asset** — weekly Monday brief | `python rating_monitor.py --notify` |
| 📸 `baseline.json` | Oct 10 2026 snapshot for weekly diffs | — |

---

## 🗓️ 30-day plan (start Monday)

- **P0-W1 📅 Booking truthfulness + No-Show amnesty** — kill auto-next-day default; booking receipt w/ server timestamp; monthly calendar back; idempotency key; "vehicle crossed your pickup — confirm boarding" grace ping + dispute pausing salary feed.
- **P0-W1 🛑 Cancel guardrails** — mandatory 2-step confirm + 15-min undo; move off notification banner.
- **P0-W2 🔐 Session + OTP survivability** — 90-day device remember; parallel SMS+WhatsApp OTP + auto-read; **offline trip card** cached at booking (readable with zero bars).
- **P1-W3 📍 Honest tracking** — fuse ETA with traffic or show window + staleness chip; unlock tracking early; single sequence source of truth.
- **P1-W3/4 🔔 Notifications + cold-start** — dedupe contradictory push; fix splash-loop + migration + map lag.
- **P2-W4+ 💬 Close the loop** — driver call/chat fallback; reply every 1–2★ in 48h; rating prompt ONLY after clean trips; explain data-retention label.

---

## 🔬 Method + tools

`google-play-scraper 1.2.7` (`app()` for score/histogram, `reviews()` 400/star newest, en/IN) → pandas keyword clustering mapped to the employee journey → 30+ hand-verified quotes → ranked by frequency × damage. Cross-checked App Store (4.6–4.7), AppBrain, G2, public help-center KB. Python 3.11, pandas. AI for clustering drafts + prose; every number re-runnable.

Assumptions: histogram = ground truth; newest-sample = recency bias toward v12.x (correct — fixable versions); keyword rates are floors (sarcasm/Hinglish undercount).

---

## ⚡ The FDE flex

The brief says *"How are our ratings?" recurs.* So the answer is code, not a slide: `rating_monitor.py` snapshots score/histogram, counts P0 clusters, diffs vs baseline, prints a Monday brief + JSON for Slack/cron.

Verified live Oct 10: `Score 4.6375 | 1-star 6.39% | loudest: booking_date_fail — staff it first Monday.` Every firefight leaves a tool behind.

---

*Built by Sam · FDE mindset: own it end-to-end, leave the tool behind · Re-run anytime.*
