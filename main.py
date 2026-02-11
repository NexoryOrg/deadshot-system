import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}")


@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx, guild: int = None):
    if guild:
        guild_obj = discord.Object(id=guild)
        await bot.tree.sync(guild=guild_obj)
        await ctx.send(f"Commands für Guild {guild} synchronisiert!")
    else:
        await bot.tree.sync()
        await ctx.send("Globale Commands synchronisiert")

@bot.command(name="reload")
@commands.is_owner()
async def reload(ctx, name):
    try:
        await bot.reload_extension(f"datein.{name}")
    except commands.ExtensionNotLoaded:
        await bot.load_extension(f"datein.{name}")
    await ctx.send(f"Die Datei {name}.py wurde neu geladen!")


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
