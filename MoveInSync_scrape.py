from google_play_scraper import reviews, Sort
import pandas as pd, time
all_r = []
for score in [1,2,3,4,5]:
    token = None
    got = 0
    for _ in range(4):
        r, token = reviews('com.moveinsync.ets', lang='en', country='in',
            sort=Sort.NEWEST, count=100, filter_score_with=score,
            continuation_token=token)
        all_r.extend(r)
        got += len(r)
        if token is None: break
        time.sleep(1)
    print(f"score {score}: {got}")
df = pd.DataFrame(all_r)
df.to_csv("moveinsync_reviews_raw.csv", index=False)
print("TOTAL:", len(df))
print(df['score'].value_counts().sort_index())
