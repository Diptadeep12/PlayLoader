import discord
import yt_dlp
import os
import re

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Function to extract the video ID from any YouTube URL
def extract_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!download'):
        try:
            url = message.content.split(' ')[1]
            video_id = extract_video_id(url)

            if video_id:
                clean_url = f'https://www.youtube.com/watch?v={video_id}'
                await message.channel.send(f"Processing video: {clean_url}")

                try:
                    # Set up yt-dlp to download the video
                    ydl_opts = {
                        'format': 'mp4',
                        'outtmpl': 'downloaded_video.mp4'
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([clean_url])

                    file_path = 'downloaded_video.mp4'
                    await message.channel.send("Here is your video:", file=discord.File(file_path))
                    os.remove(file_path)  # Remove file after sending to save space

                except Exception as yt_error:
                    await message.channel.send(f"Error downloading video: {yt_error}")
                    print(f"Download error details: {yt_error}")

            else:
                await message.channel.send("Invalid YouTube URL. Please try again.")

        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

keep_alive()
client.run(TOKEN)
