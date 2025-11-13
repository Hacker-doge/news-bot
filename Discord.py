import discord
from discord import app_commands
from discord.ext import commands
import json
import ollama
import os
from dotenv import load_dotenv
import tweepy
from datetime import datetime, timedelta

load_dotenv()

# Load environment variables
cookie = os.getenv("COOKIE")
tokem = os.getenv("TOKEN")
bearer_token = tokem

# Initialize Twitter client
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
            query=query,
            max_results=max_results,
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
            expansions=['author_id'],
            user_fields=['username', 'name', 'verified']
        )
        
        if tweets.data:
            # Create user lookup dictionary
            users = {user.id: user for user in tweets.includes['users']}
            
            print(f"\n=== Found {len(tweets.data)} tweets ===\n")
            
            tweet_list = []
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                tweet_info = {
                    'username': author.username,
                    'name': author.name,
                    'text': tweet.text,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'created_at': str(tweet.created_at)
                }
                tweet_list.append(tweet_info)
                
                print(f"@{author.username} ({author.name}):")
                print(f"  {tweet.text}")
                print(f"  Likes: {tweet.public_metrics['like_count']}, "
                      f"Retweets: {tweet.public_metrics['retweet_count']}")
                print(f"  Created: {tweet.created_at}")
                print("-" * 80)
            
            return tweet_list
        else:
            print("No tweets found.")
            return None
            
    except tweepy.TweepyException as e:
        print(f"Error: {e}")
        return None

# Initialize Discord bot
discord_client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
token = cookie

@discord_client.tree.command(name="search_news", description="Search recent tweets and get an AI summary")
@app_commands.describe(query="The search query for tweets (e.g., 'python programming')")
async def search_tweets(interaction: discord.Interaction, query: str):
    """
    Search for tweets using the provided query and summarize them with AI
    """
    # Defer the response since this might take a while
    await interaction.response.defer()
    
    try:
        # Search for tweets using the user's query
        print(f"\nSearching for tweets with query: '{query}'...")
        tweet_data = search_recent_tweets(query=query, max_results=10)
        
        if not tweet_data:
            await interaction.followup.send("No tweets found for your query.")
            return
        
        # Get AI summary
        response = ollama.chat(
            model='deepseek-r1:14b',
            messages=[
                {
                    'role': 'user',
                    'content': f'{tweet_data}\nSummarize the above tweets in a concise manner and less than 200 words.'
                }
            ]
        )
        
        # Send the summary
        summary = response['message']['content']
        
        # Discord messages have a 2000 character limit
        if len(summary) > 2000:
            summary = summary[:1997] + "..."
        
        await interaction.followup.send(f"**Search Query:** {query}\n\n**Summary:**\n{summary}")
        
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")
        print(f"Error in search_tweets command: {e}")

@discord_client.event
async def on_ready():
    await discord_client.tree.sync()  # Sync slash commands
    print(f"Logged in as {discord_client.user}")
    print("Bot is ready to search tweets!")

discord_client.run(token)