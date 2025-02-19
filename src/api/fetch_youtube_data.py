import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import requests
import pymongo
from datetime import datetime, timedelta
from config import MONGO_URI, DATABASE_NAME, VIDEO_COLLECTION, COMMENT_COLLECTION

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
videos_collection = db[VIDEO_COLLECTION]
comments_collection = db[COMMENT_COLLECTION]

# YouTube API Key
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Define brands to fetch data for
BRANDS = [
    "Apple Watch Review",
    "Samsung Galaxy Watch Review",
    "Garmin Watch Review",
    "Fitbit Watch Review",
    "Google Pixel Watch Review",
    "OnePlus Watch Review"
]

# Set time range (Last 12 months)
published_after = (datetime.utcnow() - timedelta(days=365)).isoformat() + "Z"

# Function to fetch video details
def fetch_videos(brand, max_results=50):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={brand}&type=video&maxResults={max_results}&publishedAfter={published_after}&key={API_KEY}"
    response = requests.get(url).json()

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        published_at = item["snippet"]["publishedAt"]
        channel_name = item["snippet"]["channelTitle"]
        channel_id = item["snippet"]["channelId"]
        description = item["snippet"].get("description", "")

        # Fetch additional video details (views, likes, dislikes, tags, etc.)
        stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,topicDetails&id={video_id}&key={API_KEY}"
        stats_response = requests.get(stats_url).json()

        if "items" in stats_response and stats_response["items"]:
            stats = stats_response["items"][0]

            # Extract statistics
            views = int(stats["statistics"].get("viewCount", 0))
            likes = int(stats["statistics"].get("likeCount", 0))
            dislikes = int(stats["statistics"].get("dislikeCount", 0)) if "dislikeCount" in stats["statistics"] else None
            comment_count = int(stats["statistics"].get("commentCount", 0))

            # Extract additional metadata
            tags = stats["snippet"].get("tags", [])
            category_id = stats["snippet"].get("categoryId", None)
            video_duration = stats["contentDetails"].get("duration", "")

            video_data = {
                "brand": brand,
                "video_id": video_id,
                "title": title,
                "published_at": published_at,
                "channel_name": channel_name,
                "channel_id": channel_id,
                "description": description,
                "views": views,
                "likes": likes,
                "dislikes": dislikes,
                "comment_count": comment_count,
                "tags": tags,
                "category_id": category_id,
                "video_duration": video_duration
            }
            videos.append(video_data)

    return videos

# Function to fetch comments
def fetch_comments(videos, max_results=100):
    comments = []
    
    for video in videos:
        video_id = video["video_id"]
        print(f"Fetching comments for Video ID: {video_id}")
        
        url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={video_id}&maxResults={max_results}&textFormat=plainText&key={API_KEY}"
        response = requests.get(url).json()

        while True:
            for item in response.get("items", []):
                comment_id = item["id"]
                author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                like_count = int(item["snippet"]["topLevelComment"]["snippet"]["likeCount"])
                published_at = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                reply_count = int(item["snippet"].get("totalReplyCount", 0))

                comment_data = {
                    "video_id": video_id,
                    "comment_id": comment_id,
                    "author": author,
                    "comment_text": comment_text,
                    "like_count": like_count,
                    "published_at": published_at,
                    "reply_count": reply_count
                }
                comments.append(comment_data)

            # Check if there are more comments (Pagination)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break  # No more pages, exit loop
            
            # Fetch next page of comments
            url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={video_id}&maxResults={max_results}&pageToken={next_page_token}&textFormat=plainText&key={API_KEY}"
            response = requests.get(url).json()

    return comments

# Function to store data in MongoDB
def store_in_mongodb(videos, comments):
    if videos:
        videos_collection.insert_many(videos)
        print(f"{len(videos)} videos inserted into MongoDB!")

    if comments:
        comments_collection.insert_many(comments)
        print(f"{len(comments)} comments inserted into MongoDB!")

# Main function to fetch and store YouTube data
def main():
    all_videos = []
    all_comments = []

    for brand in BRANDS:
        print(f"Fetching videos for: {brand}")
        videos = fetch_videos(brand, max_results=50)
        all_videos.extend(videos)

        print(f"Fetching comments for {len(videos)} videos...")
        comments = fetch_comments(videos, max_results=10)
        all_comments.extend(comments)

    # Store data in MongoDB
    store_in_mongodb(all_videos, all_comments)

if __name__ == "__main__":
    main()