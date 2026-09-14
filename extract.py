import requests
import os 
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")
CHANNEL = '@Fireship'

# print(API_KEY)

url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&forHandle={CHANNEL}&key={API_KEY}"

response = requests.get(url)
data = response.json()

# print(data)

uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
# print(uploads_id)

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

# print(len(video_ids))

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

print(all_vids[0])
print(len(all_vids))
