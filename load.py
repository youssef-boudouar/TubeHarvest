import json
import psycopg2


with open("data/YTdata2026-09-14.json", "r") as f:
    content = json.load(f)

# print(content[0])

con = psycopg2.connect(host="localhost", database="tubeharvest", user="youssef", password="tubeharvest")

cursor = con.cursor() # create a cursor which sends sql commands and receive result back 


for v in content:

    cursor.execute("""INSERT INTO staging.videos (video_id, title, published_at, duration, views, likes, comments) VALUES(%s, %s,%s,%s, %s,%s, %s)
    ON CONFLICT (video_id) DO UPDATE SET
    title = EXCLUDED.title,
    published_at = EXCLUDED.published_at,
    duration = EXCLUDED.duration,
    views = EXCLUDED.views,
    likes = EXCLUDED.likes,
    comments = EXCLUDED.comments""",
        (
            v['video_id'],
            v["title"],
            v["published_at"],
            v["duration"],
            v["views"],
            v["likes"],
            v["comments"]
        )
    )

vid_ids = []

for v in content:
    vid_ids.append(v['video_id'])

cursor.execute("DELETE FROM staging.videos WHERE video_id NOT IN %s", (tuple(vid_ids),))

con.commit()
con.close()