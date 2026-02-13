import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

async def send_server_log(guildID, id, title, description, color):

    kanal = guild.get_channel(db_kanal)
    
    embed= discord.Embed(
        description = description,
        color = color,
        timestamp = datetime.now()
    )
    embed.set_author(name=title, icon_url=guildID.get_user(id))
    embed.set_footer(text="https://github.com/NexoryOrg/Nexory")
    await kanal.send(embed=embed)


async def send_user_log(guildID, id, title, description, color):

    kanal = guild.get_channel(db_kanal)
    
    embed= discord.Embed(
        description = description,
        color = color,
        timestamp = datetime.now()
    )
    embed.set_author(name=title, icon_url=guildID.get_user(id))
    embed.set_footer(text="https://github.com/NexoryOrg/Nexory")
    await kanal.send(embed=embed)


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(member):
        await send_log(member.guild, member.id, f"{member.name} hat den Server betretten.", discord.Color.green())
        

async def setup(bot):
    await bot.add_cog(Log(bot))
