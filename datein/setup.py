import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
from discord.app_commands import Group


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        return await super().cog_unload()




async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
