import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime


#Logger erstellen
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8")
datum_format = "%Y-%m-%d %H-%M-%S"
formatieren = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", datum_format, style="{")
handler.setFormatter(formatieren)
logger.addHandler(handler)


async def send_embed(ctx: commands.Context , description: str, color: discord.Color, author: str, icon_url: str, footer: str):
    embed = discord.Embed(
            description=description,
            color=color,
            timestamp=datetime.now()
        )
    embed.set_author(name=author, icon_url=icon_url)
    embed.set_footer(text=footer)
    await ctx.reply(embed=embed, mention_author=True)

#Status Loop für Bot
@tasks.loop(minutes=30)
async def status_task(status_bot):
   await status_bot.change_presence(
      activity=discord.Activity(type=discord.ActivityType.watching, name=f"*Luca-Python* on GitHub"),
      status=discord.Status.online)



class dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        return await super().cog_unload()
    

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, only_guild: bool = False):

        if not only_guild:
            synced = await ctx.bot.tree.sync()
            await send_embed(ctx, f"Ich hab `{len(synced)} Befehle` erfolgreich synchronisiert.", discord.Color.green(), "✅ - Loaded", ctx.author.display_avatar.url, "https://github.com/NexoryOrg")

        else:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            await send_embed(ctx, f"Ich hab `{len(synced)} Befehle` erfolgreich auf `{ctx.guild}` synchronisiert.", discord.Color.green(), "✅ - Loaded", ctx.author.display_avatar.url, "https://github.com/NexoryOrg")

        status_task.start(self.bot)
        logger.info(f"Es wurden {len(synced)} Befehle synchronisiert. | Ausgeführt von {ctx.author}")

    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, datei_name: str):
        try:
            await self.bot.reload_extension(f"datein.{datei_name}")
            logger.info(f"Realoded `{datei_name}.py` | Ausgeführt von {ctx.author}({ctx.author.id})")
        except:
            await self.bot.load_extension(f"datein.{datei_name}")
            logger.info(f"Loaded `{datei_name}.py` | Ausgeführt von {ctx.author}({ctx.author.id})")
        
        await send_embed(ctx, f"Die Datei `{datei_name}.py` wurde erfolgreich neu geladen.", discord.Color.green(), "✅ - Reloaded", ctx.author.display_avatar.url, "https://github.com/NexoryOrg")



async def setup(bot: commands.bot) -> None:
   await bot.add_cog(dev(bot))
