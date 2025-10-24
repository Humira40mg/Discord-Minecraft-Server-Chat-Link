import asyncio
import aiohttp
import discord
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import config

TOKEN = config["discord"]["token"]
CHANNEL_ID = config["discord"]["channel_id"]
MINECRAFT_LOG = config["minecraft"]["log_path"]

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# --- Link Minecraft -> Discord ---
class LogHandler(FileSystemEventHandler):
    def __init__(self, channel):
        self.channel = channel
        self.last_size = os.path.getsize(MINECRAFT_LOG)

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            new_size = os.path.getsize(MINECRAFT_LOG)
            if new_size > self.last_size:
                with open(MINECRAFT_LOG, "r", encoding="utf-8") as f:
                    f.seek(self.last_size)
                    lines = f.read().strip().splitlines()
                    asyncio.run_coroutine_threadsafe(self.send_to_discord(lines), client.loop)
                self.last_size = new_size

    async def send_to_discord(self, lines):
        for line in lines:
            if "<" in line and ">" in line:
                msg = line.split("> ")[-1].strip()
                pseudo = line.split("<")[1].split(">")[0]
                await self.channel.send(f"**{pseudo}** : {msg}")

# --- Link Discord -> Minecraft ---
async def send_to_minecraft(message):
	# Uses the tmux session referenced in the config file
    command = f'tmux send-keys -t {config["minecraft"]["tmux_session"]} "say \'{message}\'" ENTER'
    subprocess.run(command, shell=True)

@client.event
async def on_ready():
    print("""
        _                            __ _       ___ _                            _  
  /\/\ (_)_ __   ___  ___ _ __ __ _ / _| |_    / __\ |__   __ _ _ __  _ __   ___| | 
 /    \| | '_ \ / _ \/ __| '__/ _` | |_| __|  / /  | '_ \ / _` | '_ \| '_ \ / _ \ | 
/ /\/\ \ | | | |  __/ (__| | | (_| |  _| |_  / /___| | | | (_| | | | | | | |  __/ | 
\/    \/_|_| |_|\___|\___|_|  \__,_|_|  \__| \____/|_| |_|\__,_|_| |_|_| |_|\___|_|                                                                                                                                                       
    """)
    print(f"Connected as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    event_handler = LogHandler(channel)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(MINECRAFT_LOG), recursive=False)
    observer.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == CHANNEL_ID:
        print(message.content)
        await send_to_minecraft(f"[{message.author.name}] {message.content}")

client.run(TOKEN)