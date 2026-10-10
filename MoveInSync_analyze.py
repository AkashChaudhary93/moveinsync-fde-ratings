import pandas as pd, re
df = pd.read_csv("moveinsync_reviews_raw.csv")
df['content'] = df['content'].fillna('')
themes = {
 'gps_tracking_eta_wrong': ['gps','location','tracking','live track','eta','where is cab','map'],
 'notifications_missing_delayed': ['notification','notify','alert','sms','not inform','no update'],
 'booking_selfbooking_date_fail': ['book','booking','schedule','roster','slot','date','self'],
 'login_otp_session_logout': ['login','log in','logout','logged out','otp','session','password','signin','sign in'],
 'cancel_accidental_no_confirm': ['cancel','accident','mistake','without confirm','no confirm'],
 'no_show_wrongly_marked': ['no show','no-show','noshow','marked absent'],
 'app_crash_freeze_slow': ['crash','freeze','hang','stuck','slow','lag','loading','glitch','bug'],
 'cab_late_no_cab_driver_issue': ['late','delay','driver','cab not','no cab','missed'],
 'ui_confusing_update_regression': ['update','ui','interface','confus','difficult to use','redesign'],
 'support_unresponsive': ['support','helpdesk','customer care','no response','helpline'],
 'offline_no_signal_otp_lost': ['offline','network','signal','internet','no otp'],
}
def hits(text, kws):
    t = text.lower()
    return any(k in t for k in kws)
for star in [1,2,3]:
    sub = df[df.score==star]
    print(f"\n===== {star}-STAR (n={len(sub)}) =====")
    for name, kws in themes.items():
        c = sub['content'].apply(lambda t: hits(t,kws)).sum()
        print(f"{name}: {c} ({c/len(sub)*100:.1f}%)")
# sample quotes per theme from 1-star
print("\n\n===== SAMPLE 1-STAR QUOTES =====")
for name, kws in themes.items():
    sub = df[(df.score==1) & (df['content'].apply(lambda t: hits(t,kws)))]
    print(f"\n--- {name} ({len(sub)}) ---")
    for _, r in sub.head(3).iterrows():
        txt = re.sub(r'\s+',' ', str(r['content']))[:280].encode('ascii','ignore').decode()
        print(f"[{str(r['at'])[:10]}] {txt}")
# version concentration of bad reviews
print("\n\n===== APP VERSIONS ON 1-2 STAR =====")
print(df[df.score.isin([1,2])]['reviewCreatedVersion'].value_counts().head(10))
print("\n===== DATES =====")
df['at'] = pd.to_datetime(df['at'])
print(df[df.score.isin([1,2])]['at'].dt.to_period('M').value_counts().head(8))
