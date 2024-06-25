import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Example API URLs - replace with actual endpoints and include necessary authentication
TIKTOK_API_URL = "https://www.tiktok.com/api/video/details/?video_id={video_id}"
INSTAGRAM_API_URL = "https://graph.instagram.com/{post_id}?fields=video_views&access_token={access_token}"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"

# Add your API keys and access tokens here
INSTAGRAM_ACCESS_TOKEN = "replace_with_instagram_access_token"
YOUTUBE_API_KEY = "replace_with_youtube_api_key"

def get_tiktok_views(video_id):
    response = requests.get(TIKTOK_API_URL.format(video_id=video_id))
    data = response.json()
    return data['itemInfo']['itemStruct']['stats']['playCount']

def get_instagram_views(post_id):
    response = requests.get(INSTAGRAM_API_URL.format(post_id=post_id, access_token=INSTAGRAM_ACCESS_TOKEN))
    data = response.json()
    return data['video_views']

def get_youtube_views(video_id):
    response = requests.get(YOUTUBE_API_URL.format(video_id=video_id, api_key=YOUTUBE_API_KEY))
    data = response.json()
    return int(data['items'][0]['statistics']['viewCount'])

def track_views(platform, ids, interval=60):
    last_views = {id_: None for id_ in ids}
    last_timestamp = {id_: None for id_ in ids}

    get_views_func = {
        "tiktok": get_tiktok_views,
        "instagram": get_instagram_views,
        "youtube": get_youtube_views
    }[platform]

    try:
        while True:
            for id_ in ids:
                views = get_views_func(id_)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{platform.capitalize()} ID: {id_}, Time: {timestamp}, Views: {views}")

                rate_of_increase = None
                if last_views[id_] is not None and last_timestamp[id_] is not None:
                    rate_of_increase = (views - last_views[id_]) / ((datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_timestamp[id_], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60)
                    
                    label = "nice prospect" if rate_of_increase > 100 else ""
                    print(f"Rate of Increase for {platform.capitalize()} ID {id_}: {rate_of_increase:.2f} views/min, {label}")

                with open(f'data/{platform}_views_data_{id_}.csv', 'a') as f:
                    f.write(f"{timestamp},{views},{rate_of_increase if rate_of_increase is not None else ''}\n")

                last_views[id_] = views
                last_timestamp[id_] = timestamp

            time.sleep(interval)
    except KeyboardInterrupt:
        print("Tracking stopped.")

def plot_views(platform, ids):
    for id_ in ids:
        df = pd.read_csv(f'data/{platform}_views_data_{id_}.csv', names=['timestamp', 'views', 'rate_of_increase'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['views'] = pd.to_numeric(df['views'], errors='coerce')
        df['rate_of_increase'] = pd.to_numeric(df['rate_of_increase'], errors='coerce')

        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Views', color='tab:blue')
        ax1.plot(df['timestamp'], df['views'], marker='o', color='tab:blue', label='Views')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Rate of Increase (views/min)', color='tab:red')
        ax2.plot(df['timestamp'], df['rate_of_increase'], marker='x', color='tab:red', linestyle='dashed', label='Rate of Increase')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        fig.tight_layout()
        plt.title(f'{platform.capitalize()} Video Views and Rate of Increase Over Time - {platform.capitalize()} ID {id_}')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Track video views over time for multiple platforms.')
    parser.add_argument('--track', action='store_true', help='Start tracking views.')
    parser.add_argument('--plot', action='store_true', help='Plot the views data.')
    parser.add_argument('--platform', choices=['tiktok', 'instagram', 'youtube'], required=True, help='Platform to track.')
    parser.add_argument('--ids', nargs='+', required=True, help='List of video/post IDs to track.')

    args = parser.parse_args()

    if args.track:
        track_views(args.platform, args.ids)
    if args.plot:
        plot_views(args.platform, args.ids)
