import re
import psycopg2

def fix_duration(duration):
    h = re.findall(r"(\d+)H", duration)
    m = re.findall(r"(\d+)M", duration)
    s = re.findall(r"(\d+)S", duration)

    hours = int(h[0]) if h else 0
    minutes = int(m[0]) if m else 0
    seconds = int(s[0]) if s else 0

    return hours * 3600 + minutes * 60 + seconds

con = psycopg2.connect(host="localhost", database="tubeharvest", user="youssef", password="tubeharvest")

cursor = con.cursor()

cursor.execute("SELECT video_id, title, published_at, duration, views, likes, comments FROM staging.videos")
rows = cursor.fetchall()

cursor.execute( """DELETE FROM core.videos 
    WHERE video_id NOT IN (SELECT video_id FROM staging.videos)""")


for row in rows:
    video_id = row[0]
    title = row[1]
    published_at = row[2]
    duration = fix_duration(row[3])
    views = int(row[4])
    likes = int(row[5])
    comments = int(row[6])
    likes_per_views = likes / views if views > 0 else 0
    comments_per_views = comments / views if views > 0 else 0
    cursor.execute("""
    INSERT INTO core.videos (video_id, title, published_at, duration_seconds, views, likes, comments, likes_per_view, comments_per_view)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (video_id) DO UPDATE SET
        title = EXCLUDED.title,
        published_at = EXCLUDED.published_at,
        duration_seconds = EXCLUDED.duration_seconds,
        views = EXCLUDED.views,
        likes = EXCLUDED.likes,
        comments = EXCLUDED.comments,
        likes_per_view = EXCLUDED.likes_per_view,
        comments_per_view = EXCLUDED.comments_per_view,
        updated_at = CURRENT_TIMESTAMP
    """, (
        video_id, title, published_at, duration, views, likes, comments, likes_per_views, comments_per_views
    ))

con.commit()
con.close() 

