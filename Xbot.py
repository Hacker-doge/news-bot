import tweepy
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

load_dotenv()

tokem = os.getenv("TOKEN")

with open("TOPIC.json", "r") as f:
    TOPIC = json.load(f)

# Method 1: OAuth 2.0 Bearer Token (Recommended for API v2)
bearer_token = tokem
# Create client with Bearer Token
client = tweepy.Client(bearer_token=bearer_token)

def search_recent_tweets(query, max_results=10):
    """
    Search for recent tweets (last 7 days)
    
    Args:
        query: Search query (e.g., "python -is:retweet")
        max_results: Number of tweets to return (10-100 per request)
    """
    try:
        tweets = client.search_recent_tweets(
            query=TOPIC,
            max_results=max_results,
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
            expansions=['author_id'],
            user_fields=['username', 'name', 'verified']
        )
        
        if tweets.data:
            # Create user lookup dictionary
            users = {user.id: user for user in tweets.includes['users']}
            
            print(f"\n=== Found {len(tweets.data)} tweets ===\n")
            
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                print(f"@{author.username} ({author.name}):")
                print(f"  {tweet.text}")
                print(f"  Likes: {tweet.public_metrics['like_count']}, "
                      f"Retweets: {tweet.public_metrics['retweet_count']}")
                print(f"  Created: {tweet.created_at}")
                print("-" * 80)
        else:
            print("No tweets found.")
            
        return tweets
        
    except tweepy.TweepyException as e:
        print(f"Error: {e}")
        return None
    
print("\n\n1. Searching for 'python programming' tweets...")
info = search_recent_tweets("python programming -is:retweet lang:en", max_results=10)

with open("info.json", "w") as f:
    json.dump(info, f)