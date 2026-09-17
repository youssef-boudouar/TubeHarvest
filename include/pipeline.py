import os
import psycopg2
import requests
import json
import re
from datetime import datetime


DB_HOST = os.getenv("POSTGRES_CONN_HOST", "localhost")
DB_NAME = os.getenv("ELT_DATABASE_NAME", "tubeharvest")
API_KEY = os.getenv("AIRFLOW_VAR_API_KEY")

CHANNEL = os.getenv('CHANNEL_HANDLE')


def extract_channel():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&forHandle={CHANNEL}&key={API_KEY}"

    response = requests.get(url)
    data = response.json()
    uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return uploads_id

def extract_video_ids(uploads_id):
    video_ids= []
    next_page = None

    while(True):
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_id}&maxResults=50&key={API_KEY}"
        if next_page:
            playlist_url += f"&pageToken={next_page}"
        response = requests.get(playlist_url)
        playlist_data = response.json()

        for i in playlist_data['items']:
            video_ids.append(i['contentDetails']['videoId'])
        next_page = playlist_data.get("nextPageToken")
        if next_page is None:
            break
    return video_ids

def extract_video_details(video_ids):
    all_vids = []

    for i in range(0, len(video_ids), 50):
        ids = ",".join(video_ids[i:i+50])

        video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={ids}&key={API_KEY}"

        response = requests.get(video_url)
        video_data = response.json()
        for item in video_data['items']:
            video = {
                "video_id": item['id'],
                "title": item['snippet']['title'],
                "published_at" : item['snippet']['publishedAt'],
                "duration": item["contentDetails"]["duration"],
                "views": item["statistics"].get("viewCount", 0),
                "likes": item["statistics"].get("likeCount", 0),
                "comments": item["statistics"].get("commentCount", 0)
            }
            all_vids.append(video)
    return all_vids

def save_to_json(all_vids):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"data/YTdata{today}.json", "w") as f:
        json.dump(all_vids, f, indent=2)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_CONN_HOST", "localhost"),
        database=os.getenv("ELT_DATABASE_NAME", "tubeharvest"),
        user=os.getenv("ELT_DATABASE_USERNAME", "youssef"),
        password=os.getenv("ELT_DATABASE_PASSWORD", "tubeharvest")
    )


def load_to_staging():
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"data/YTdata{today}.json", "r") as f:
        content = json.load(f)

    con = get_db_connection()
    cursor = con.cursor()

    for v in content:
        cursor.execute("""
            INSERT INTO staging.videos (video_id, title, published_at, duration, views, likes, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO UPDATE SET
                title = EXCLUDED.title,
                published_at = EXCLUDED.published_at,
                duration = EXCLUDED.duration,
                views = EXCLUDED.views,
                likes = EXCLUDED.likes,
                comments = EXCLUDED.comments
        """, (
            v['video_id'], v["title"], v["published_at"],
            v["duration"], v["views"], v["likes"], v["comments"]
        ))

    vid_ids = []
    for v in content:
        vid_ids.append(v['video_id'])
    cursor.execute("DELETE FROM staging.videos WHERE video_id NOT IN %s", (tuple(vid_ids),))

    con.commit()
    con.close()

def fix_duration(duration):
    h = re.findall(r"(\d+)H", duration)
    m = re.findall(r"(\d+)M", duration)
    s = re.findall(r"(\d+)S", duration)
    hours = int(h[0]) if h else 0
    minutes = int(m[0]) if m else 0
    seconds = int(s[0]) if s else 0
    return hours * 3600 + minutes * 60 + seconds

def transform_to_core():
    con = get_db_connection()
    cursor = con.cursor()

    cursor.execute("SELECT video_id, title, published_at, duration, views, likes, comments FROM staging.videos")
    rows = cursor.fetchall()

    cursor.execute("""DELETE FROM core.videos 
        WHERE video_id NOT IN (SELECT video_id FROM staging.videos)""")

    for row in rows:
        video_id = row[0]
        title = row[1]
        published_at = row[2]
        duration = fix_duration(row[3])
        views = int(row[4])
        likes = int(row[5])
        comments = int(row[6])
        likes_per_view = likes / views if views > 0 else 0
        comments_per_view = comments / views if views > 0 else 0
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
            video_id, title, published_at, duration, views, likes, comments, likes_per_view, comments_per_view
        ))

    con.commit()
    con.close()