import json
import psycopg2


with open("data/YTdata2026-09-14.json", "r") as f:
    content = json.load(f)

# print(content[0])

con = psycopg2.connect(host="localhost", database="tubeharvest", user="youssef", password="tubeharvest")

cursor = con.cursor() # create a cursor which sends sql commands and receive result back 

for v in content:

    cursor.execute("INSERT INTO staging.videos (video_id, title, published_at, duration, views, likes, comments) VALUES(%s, %s,%s,%s, %s,%s, %s)",
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

con.commit()
con.close()