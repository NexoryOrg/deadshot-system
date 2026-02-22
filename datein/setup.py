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


    setup_group = Group(name="setup", description="Setup commands for server configuration.")

    @setup_group.command(name="start", description="Start the setup process for server configuration.")
    @app_commands.describe()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setup_start(self, interaction: discord.Interaction, log_channel: discord.TextChannel, task_remindme: bool):
        print(1)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
