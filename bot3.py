import discord
from discord import app_commands
import psutil
import subprocess
import time
import os
import requests
from discord.ext import commands, tasks
from datetime import datetime
import json

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

sending_pins = False
    
with open("/etc/discord_bot_pinterest/settings.json", "r") as f:
    settings = json.load(f)

@bot.event
async def on_ready():
  await tree.sync()
  print("dolboeb")


def search_pins(query, limit=5):
    url = "https://api.pinterest.com/v5/search/pins"
    headers = {
        "Authorization": f"Bearer {settings['pinterest_token']}"
    }
    params = {
        "query": query,
        "page_size": limit
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print("Error:", response.json())
        return []

@tasks.loop(minutes=1.5)
async def send_pins():
    global sending_pins
    if not sending_pins:
        return

    channel = bot.get_channel(int(settings["channel_id"]))
    if not channel:
        print("Канал не найден.")
        return

    pins = search_pins("furry", limit=3)
    if not pins:
        await channel.send("Картинки не найдены.")
        return

    for pin in pins:
        image_url = pin.get("media", {}).get("url", "")
        if image_url:
            await channel.send(image_url)

@tree.command(name="start", description="Запускает автоматическую отправку картинок каждые 5 минут.")
async def start(ctx: discord.Interaction):
    global sending_pins
    if sending_pins:
        await ctx.response.send_message("Автоматическая отправка уже запущена!")
        return

    sending_pins = True
    send_pins.start()
    await ctx.response.send_message("Автоматическая отправка картинок запущена!")

@tree.command(name="stop", description="Останавливает автоматическую отправку картинок.")
async def stop(ctx: discord.Interaction):
    global sending_pins
    if not sending_pins:
        await ctx.response.send_message("Автоматическая отправка уже остановлена.")
        return

    sending_pins = False
    send_pins.stop()
    await ctx.response.send_message("Автоматическая отправка картинок остановлена.")

bot.run(settings["token"])
