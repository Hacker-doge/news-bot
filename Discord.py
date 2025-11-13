import discord
from discord import app_commands
from discord.ext import commands
import json
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

cookie = os.getenv("COOKIE")

TOPIC = "NONE"

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

token = cookie

@client.tree.command(name="test", description="A test command")
async def say(interaction: discord.Interaction, message: str):
    TOPIC = message

    with open("TOPIC.json", "w") as f:
        json.dump(TOPIC, f)

    with open("info.json", "r") as f:
        info = json.load(f)

    response = ollama.chat(model='deepseek-r1:14b', messages=[
    {'role': 'user', 'content': info}
    ]) 

    await interaction.response.send_message(response['message']['content'])

@client.event
async def on_ready():
    await client.tree.sync()  # Sync slash commands
    print(f"Logged in as {client.user}")

    
client.run(token)