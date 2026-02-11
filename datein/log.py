import discord
from discord.ext import commands
from discord import app_commands

class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
            name="test",
            description="test command"
    )
    async def hallo(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Test Nachricht für {interaction.user.id}")

async def setup(bot):
    await bot.add_cog(Log(bot))
