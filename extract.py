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

print(len(video_ids))