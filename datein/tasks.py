import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord.app_commands import Group
    

class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


   tasks = Group(name="tasks", description="Command Group to creat Tasks", guild_only=True

   @tasks.command(name="create", description="Create an new Task")
   async def create(self, interaction: discord.Interaction)
        #hier modal senden mit title, description und datum
                 

async def setup(bot):
    await bot.add_cog(tasks(bot))
