import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}")

async def load_extensions():
    for filename in os.listdir("datein"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"datein.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

import asyncio
asyncio.run(main())
