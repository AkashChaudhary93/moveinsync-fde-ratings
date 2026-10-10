# MoveInSync Play Store Ratings — FDE Diagnosis + 30-Day Action Plan
**Candidate: Sam | Forward Deployed Engineer (Intern → FTE) | Oct 2026**
**Data window:** live scrape Oct 10 2026 · `com.moveinsync.ets` · 2,000 newest reviews (400 per star) + full histogram + App Store + G2 cross-check

---

## 0. TL;DR for leadership (read this, act tomorrow)

**Headline rating 4.64 / 114,849 ratings looks healthy. It is not.**
The distribution is violently bimodal: **~85.4% are 5★ (98,141) and ~6.4% are 1★ (7,338)**. Almost nobody is in the middle. That is the classic signature of a *captive-audience app*: employees must use it, so the happy path rates 5★ by habit and every operational failure rates 1★ in anger. You cannot move the headline by chasing delight — you move it by **deleting the six failure modes that manufacture 1★s**.

**The six 1★ factories (ranked by frequency in 1–3★ reviews, n=1,200):**

| # | Failure | 1★ hit-rate | 2★ hit-rate | What the user feels at 6 AM |
|---|---------|-------------|-------------|------------------------------|
| 1 | Self-booking / schedule / date bugs | 17.5% | **26.0%** | "I booked and the app booked the wrong day. Salary gets cut for no-show." |
| 2 | Crash / freeze / slow / stuck-after-update | 14.0% | 18.5% | "Update dropped, app won't open unless I reinstall." |
| 3 | Login / OTP / forced logout loop | 11.8% | 12.0% | "No OTP. Logged out at midnight. Can't board." |
| 4 | GPS / live-track / ETA wrong | 11.5% | 17.5% | "Map says cab is here. Road is empty. I miss pickup." |
| 5 | UI regression after redesign (2-step shuttle, clutter) | 11.2% | 18.8% | "I thought I booked. I hadn't. Too late." |
| 6 | Cab late / no cab / driver unreachable + dead support line | 10.0% | 14.0% | "2:30 AM cab, 3:30 AM nothing, helpline disconnects." |

Cross-cutting amplifiers: **wrong "No-Show" marks (~2% but highest rage density — salary deduction), one-tap accidental Cancel with no confirm (iOS + Android both report it), offline dead-zone at gates (OTP/driver card vanishes with signal), contradictory push ("trip not booked" after booking).**

**My 30-day bet:** fix P0 items 1–3 below and you convert an estimated **1,500–2,500 1★/yr into 4–5★**, lifting the rolling average ~+0.05–0.10 and — more importantly — collapsing the 1★ share that enterprise buyers actually read. Full math in §5.

**What I'm handing you:** (a) this memo, (b) `moveinsync_reviews_raw.csv` (2,000 reviews, reproducible), (c) `MoveInSync_scrape.py` + `MoveInSync_analyze.py` (re-run anytime), (d) `rating_monitor.py` — a 60-line FDE-style reusable agent that answers *"How are our Play Store ratings?"* every Monday morning without a human. That last one is the FDE tell: I didn't just do the one-time ask, I productized the recurring question.

---

## 1. How I read the JD — and why this assignment is an FDE filter

The JD says, in order: *work directly with customers → identify product gaps → build with AI/code/automation → turn wins into reusable capabilities → take to production with Product/Eng → help others adopt.* It explicitly says **"You don't just configure what's already there — you build what's missing."**

This assignment tests exactly that loop in miniature:

1. **Ambiguous customer problem, no prepared data.** ("We haven't prepared any data. Everything is public.") An FDE doesn't ask for a ticket queue — they scrape Play, App Store, G2, and the public help-center KB and build their own dataset. Done (§2).
2. **Technical + AI-first.** 2,000 reviews is too many to read, too few to trust blindly. I used `google-play-scraper` + pandas keyword clustering + manual quote verification — scripting where it's deterministic, judgment where it's not. Reproducible in one command.
3. **Strong communicator.** The deliverable is not a dashboard, it's *a recommendation a PM/EM can start Monday*. So every finding below ends in: owner, file/screen, acceptance test, and what "done" looks like in the review stream.
4. **Reusable capability.** The brief says *"How are our ratings?" is a question we'll keep asking.* A one-time PDF decays. A cron job + Slack post doesn't. `rating_monitor.py` is that building block — the FDE habit of leaving something behind that makes the next deployment faster.

Assumptions (stated): Play histogram at scrape time is ground truth (4.6375, n=114,849, histogram [7338, 837, 1231, 7297, 98141]); sampled 400/star newest = recency-biased toward v12.x (correct — that's the version you can still fix); keyword hit-rates undercount (sarcasm, Hindi/Hinglish, typos) so treat as floors; App Store (4.6–4.7, ~51K) and G2 (4.5) used only as triangulation.

---

## 2. Method (so anyone can re-run this Monday)

```
python MoveInSync_scrape.py    # → moveinsync_reviews_raw.csv (2,000 rows, 400/star, Sort.NEWEST, in/en)
python MoveInSync_analyze.py   # → theme hit-rates per star + sample quotes + version/month cuts
python rating_monitor.py       # → weekly delta vs baseline, posts P0-cluster counts
```

Tools: Python 3.11, `google-play-scraper 1.2.7`, pandas, Play web (`hl=en_IN`), App Store review pages, AppBrain rating history (4.32 blended vs 4.64 native — third-party caches lag; noted, not used), MoveInSync public help center (login/OTP troubleshooting pages confirm OTP + session bugs are known internally), G2 ETS reviews (praise: scheduling ease; complaints: lag, map-view lag, GPS accuracy — same clusters).

Why newest-not-random: the hiring question is *what to fix now*. Version cut proves it: 1–2★ span every v11.x–v12.x build (top offenders 12.17.0, 12.14.1, 12.19.0-current) — this is not one bad release, it's systemic across the self-booking → tracking → boarding chain.

---

## 3. Diagnosis — the journey breaks in five places

Map every theme to the employee journey from your brief (onboard → self-book → assigned → pickup-time → live-track → OTP board → drop → raise issue):

### Break 1 — SELF-BOOKING creates the trip wrong (biggest 2★ driver, 26%)
Symptoms: wrong date booked despite correct selection; "next-day toggle" auto-schedules forward (multiple users beg for removal); monthly view missing so users can't verify; contradictory push *after* successful booking ("trip is not booked"); shuttle booking silently became 2-step in UI refresh — users think they booked, they hadn't.
Why it matters disproportionately: self-booking is *the* primary trip-creation path per your brief. A booking bug doesn't annoy — it strands, then triggers a false No-Show, then a salary deduction. One bug, triple rage. Representative: *"even when I carefully select specific dates, the system creates bookings for completely different dates… reported as No Show… then asked to rate the trip"* (June 2026, Play).
FDE read: this is a client-state vs server-state contract bug + a dangerous default (auto-roll to next day) + missing idempotency receipt. Fixable without touching routing.

### Break 2 — PICKUP-TIME + LIVE-TRACK lies (11–21% across 1–3★)
Symptoms: GPS dot frozen/wrong; ETA off by 3× vs Google Maps; tracking locked until <60 min before pickup ("won't let you track the van under an hour"); sequence mismatch (employee app shows seq X, driver app shows seq Y); offline gate zones wipe driver card + OTP (Jan 2026: *"lost signal and with it driver details and OTP"*).
FDE read: three separable defects — (a) ETA model not fused with traffic (users compare against Maps and you lose), (b) aggressive location throttling to save battery that reads as "frozen", (c) no offline snapshot of today's trip card. All three are client + backend-instrumentation fixes, not fleet ops.

### Break 3 — BOARDING fails at the door (OTP / login / No-Show / Cancel)
Symptoms: OTP never arrives (SMS/WhatsApp/email all reported); forced logout + re-login loop ("every time after opening app it requires login and OTP… it's not a banking app"); session lost exactly when OTP needed; seat-belt check overlays and swallows OTP; single-tap **Cancel Trip with zero confirm** (App Store 2023 report still true in 2026 samples; May 2026 Android: *"accidental touches… resulting in trips unintentionally cancelled… 3 AM stress"*); wrong No-Show → salary cut is the single most enraging event per unit volume.
FDE read: auth/session is over-strict for a captive workforce app; destructive actions lack the guardrails your own help-center implicitly admits users need. Highest trust-damage per incident.

### Break 4 — APP FOUNDATION cracks (crash/freeze/update-regression, 14–18%)
Symptoms: stuck on splash loop; crash on open/track; post-update won't open without reinstall (reported "3 months" running); map-view lag on seat booking; policy-acceptance nag on every tap; notification stack overflow hides latest alert.
FDE read: update-migration + cold-start + push-handling debt. Version spread proves no single bad build — it's the upgrade path and launch path.

### Break 5 — WHEN IT BREAKS, HELP ISN'T THERE (support ~6% of 1★, rage-dense)
Symptoms: helpline rings out / disconnects at 2–3 AM; in-app help buries the driver-call; SOS button reported non-functional (App Store 2024, still cited); "Data can't be deleted" data-safety label fuels distrust in reviews.
FDE read: support failure doesn't create detractors, it *locks them in* — the user who would have edited 3★ after a callback instead stays 1★ forever.

**What is NOT the problem:** pricing/ads (no ads, enterprise-paid), feature breadth (desk/meeting/shuttle breadth praised), driver supply per se (complaints center on *information* about the cab, not existence). Don't gold-plate features; repair truthfulness.

---

## 4. Recommendation — what to fix, in what order (start Monday)

### P0 — Week 1–2 (stop manufacturing 1★s)

**P0-1. Self-booking truthfulness + No-Show amnesty**
- Kill the auto-next-day default. Default = selected date, explicit user opt-in to roll forward. Delete the toggle users hate.
- Booking receipt screen: date, shift, pickup point, roster source, booking ID, server timestamp — plus monthly-view calendar back (explicitly requested).
- Idempotency key on book-tap (disable double-tap, return existing booking instead of duplicate/wrong-date).
- No-Show guardrail: check-in grace ping ("your vehicle crossed your pickup point — tap to confirm boarding", the exact feature Arvind Kumar requested June 2026) + one-tap "I was there" dispute that auto-pauses the salary-deduction feed pending ops review. Measure dispute-overturn rate.
- *Acceptance:* zero wrong-date bookings in dogfood across 2 roster cycles; No-Show dispute SLA <24h; watch 1★ containing "wrong date / no show" → down 50% in 30 days.
- *Owner:* App + rostering backend. Effort M.

**P0-2. Destructive-action guardrails (cheapest rating points on the board)**
- Cancel Trip → mandatory 2-step confirm showing date/time/pickup + undo window (15 min before cutoff). Same for SOS-adjacent buttons.
- Move Cancel away from notification banner tap-target (the App Store tap-from-notification misfire).
- *Acceptance:* zero one-tap cancels in telemetry; accidental-cancel reviews → zero in next 500 1★ sample.
- *Owner:* App. Effort S. Ship in a hotfix.

**P0-3. Session + OTP survivability**
- Persistent login (remember device 90 days; re-auth only on device change) — the #1 "it's not a banking app" complaint.
- OTP: parallel SMS+WhatsApp send, visible countdown + one-tap resend, auto-read on Android, and **offline trip card**: today's driver, vehicle, OTP, sequence cached at booking time and readable with zero bars (fixes the gate dead-zone strand).
- *Acceptance:* login-related 1★ halved; OTP-not-received tickets down; offline-card render tested in airplane mode.
- *Owner:* App + identity. Effort M.

### P1 — Week 3–4 (make the map truthful)

**P1-4. Tracking honesty**
- Fuse ETA with live traffic (or stop showing a false-precision ETA — show window + "updated Xm ago" staleness chip; never show a frozen dot as live).
- Unlock tracking earlier than 60-min gate; fix employee-vs-driver sequence mismatch (single sequence source of truth; surface mismatch as explicit error, not silent NA).
- Battery-throttle transparency: "low-power mode — updating every 2 min" beats a frozen lie.
- *Acceptance:* ETA within ±3 min on 80% of sampled trips; "ETA wrong / GPS" 1★ share down a third.
- *Owner:* Backend + apps. Effort M–L.

**P1-5. Notification reliability**
- Single notification pipeline audit: dedupe contradictory "not booked" push; priority channel for cab-assigned / 15-min / arrived; quiet-hours respect for non-urgent.
- *Owner:* Backend. Effort S–M.

**P1-6. Cold-start + update-migration hardening**
- Fix splash-loop (initialize async, fail open to cached trip card); migration test on update (the "reinstall to open" bug); map-view virtualization for seat lag; kill per-tap policy nag (once per version, not per tap).
- *Acceptance:* crash-free sessions >99.5%, ANR rate halved, cold start p95 <2.5s on mid-range devices.
- *Owner:* App + QA. Effort M.

### P2 — Week 4+ (close the loop, lift the floor)

**P2-7. In-app rescue when ops fails:** one-tap driver call + chat fallback, helpdesk callback request with queue position, SOS test mode. Publish a "missed-pickup playbook" card in-app.
**P2-8. Review-response + rating-prompt surgery:** reply to every 1–2★ within 48h with a named owner (your team already replies on App Store — extend to Play with substance, not templates); trigger the native rating prompt only after a completed, on-time, dispute-free trip — never after a cancel/No-Show (current prompts after No-Show read as mockery and manufacture rage).
**P2-9. Data-safety label:** "Data can't be deleted" is quoted angrily. If enterprise retention requires it, say so in one plain sentence in-app; unexplained, it costs stars.

**Explicitly NOT first:** new features, redesign, EV/desk-booking expansion, referral prompts. The data says repair truthfulness before adding surface.

---

## 5. Expected movement (honest math, no fairy dust)

Baseline: 114,849 ratings @ 4.6375 → ~532,600 star-points. Histogram shows ~13,072 sub-4★ vs 98k+ 5★.
- If P0 converts just **20% of the 7,338 1★ (≈1,470 users)** to re-rate/edit to 4★ via fixed flows + review-reply + corrected No-Shows: +~4,400 star-points → **≈4.676 (+0.04)**.
- At 40% conversion (≈2,935): **≈4.71 (+0.08)**.
- The real prize isn't +0.08, it's the **1★ share 6.4% → ~4–5%**, which is what enterprise buyers screenshot. Plus: every prevented No-Show is a salary dispute avoided — the highest-leverage goodwill in a B2B2C product where the buyer (employer) and the rater (employee) are different people.

Track weekly: total score, 1★ share of trailing-30-day reviews, P0-cluster hit-rate in 1–2★ (target: booking-cluster 26%→<13% in 60 days). `rating_monitor.py` computes all three.

---

## 6. The reusable asset — `rating_monitor.py` (the FDE flex)

Because *"How are our ratings?"* recurs, I built the answer as code, not a slide. It snapshots score/histogram/reviews, pulls the newest N reviews per star, counts the P0 clusters from §3, diffs against baseline, and prints a Monday-morning brief + JSON for Slack/cron. Product or Eng can run it tomorrow:

```
python rating_monitor.py --baseline baseline.json --notify
```

This is the pattern I'd repeat as an FDE: every customer firefight leaves behind an agent/skill/script so the second firefight is cheaper. Next extensions (named, not built — scope discipline): per-client (per-org) rating slice, version-regression detector (flags a build when its 1★ share exceeds trailing mean +2σ), auto-drafted review replies grounded in help-center KB.

---

## 7. How I got here + tools (the short note the brief asks for)

1. Located the real listing (`com.moveinsync.ets`, 1M+ installs, v12.19.0, updated Oct 8 2026) via Play web; cross-checked App Store (4.6–4.7), AppBrain, G2, and the public MoveInSync help center.
2. Scraped ground truth with `google-play-scraper` (`app()` for score/histogram; `reviews()` 400/star, newest, en/IN) → `moveinsync_reviews_raw.csv` (2,000 rows).
3. Clustered with pandas keyword buckets mapped to the employee journey in your brief, then hand-verified with 30+ full quotes (dates/versions kept) to avoid keyword theater.
4. Ranked by 1–2★ frequency × damage (salary/strand/stranded-at-night weights rage, not just count), wrote acceptance tests per fix, sized effort T-shirt style.
5. Productized the loop as `rating_monitor.py`.

Tools: Python 3.11, google-play-scraper 1.2.7, pandas, Play/App Store web, G2, helpcenter.moveinsync.com. AI used for clustering drafts and prose; every number above is from the scrape, re-runnable. Assumptions listed in §1. Files attached; one command reproduces everything.

*— Sam. FDE mindset: own the problem end-to-end, leave the reusable block behind. Happy to walk through the code or extend the monitor per-org live.*
