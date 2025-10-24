# Discord ↔ Minecraft Bridge (tmux)

A minimal RAM bridge between a **Discord channel** and a **Minecraft server**, built with Python.  
No plugins, no HTTP servers, no RCON — just `tmux` and a few lightweight libraries.

---

## Features

- Real-time message relay between Minecraft and Discord  
- Works with any vanilla or Paper/Spigot server  
- No network ports required — fully local  
- Simple to set up and maintain  

---

## Requirements

- Python 3.10+  
- A running Minecraft server inside a `tmux` session  
- A Discord bot token  
- The following Python packages:

```bash
pip install -r requirements.txt