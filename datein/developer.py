import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime
import aiomysql

# Logger erstellen
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8")
datum_format = "%Y-%m-%d %H-%M-%S"
formatieren = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", datum_format, style="{")
handler.setFormatter(formatieren)
logger.addHandler(handler)

# Embed-Sender
async def send_embed(ctx: commands.Context, description: str, color: discord.Color, author: str, icon_url: str, footer: str):
    embed = discord.Embed(
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_author(name=author, icon_url=icon_url)
    embed.set_footer(text=footer)
    await ctx.reply(embed=embed, mention_author=True)


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.status_task.start()
        self.pool = None

    # Status Loop als Cog-Methode
    @tasks.loop(minutes=30)
    async def status_task(self):
        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name="*Luca-Python* on GitHub"),
                status=discord.Status.online
            )
            logger.info("Status erfolgreich gesetzt.")
        except Exception as e:
            logger.error(f"Fehler beim Setzen des Status: {e}")

    @status_task.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()
        logger.info("Status-Task startet...")

    # Cog unload
    async def cog_unload(self) -> None:
        self.status_task.cancel()
        return await super().cog_unload()

    # Sync Command
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, only_guild: bool = False):
        try:
            if not only_guild:
                synced = await ctx.bot.tree.sync()
                await send_embed(ctx, f"Ich hab `{len(synced)} Befehle` erfolgreich synchronisiert.",
                                 discord.Color.green(), "✅ - Loaded", ctx.author.display_avatar.url,
                                 "https://github.com/NexoryOrg")
            else:
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
                await send_embed(ctx, f"Ich hab `{len(synced)} Befehle` erfolgreich auf `{ctx.guild}` synchronisiert.",
                                 discord.Color.green(), "✅ - Loaded", ctx.author.display_avatar.url,
                                 "https://github.com/NexoryOrg")

            logger.info(f"Es wurden {len(synced)} Befehle synchronisiert. | Ausgeführt von {ctx.author}")

        except Exception as e:
            logger.error(f"Fehler beim Syncen: {e}")
            await ctx.send("❌ Fehler beim Synchronisieren der Commands")

    # Reload Command
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, datei_name: str):
        try:
            try:
                await self.bot.reload_extension(f"datein.{datei_name}")
                logger.info(f"Reloaded `{datei_name}.py` | Ausgeführt von {ctx.author}({ctx.author.id})")
            except commands.ExtensionNotLoaded:
                await self.bot.load_extension(f"datein.{datei_name}")
                logger.info(f"Loaded `{datei_name}.py` | Ausgeführt von {ctx.author}({ctx.author.id})")

            await send_embed(ctx, f"Die Datei `{datei_name}.py` wurde erfolgreich neu geladen.",
                             discord.Color.green(), "✅ - Reloaded", ctx.author.display_avatar.url,
                             "https://github.com/NexoryOrg")
        except Exception as e:
            logger.error(f"Fehler beim Reload von {datei_name}: {e}")
            await ctx.send(f"❌ Fehler beim Reload der Datei `{datei_name}.py`")


# Setup
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dev(bot))
    logger.info("Cog 'Dev' erfolgreich geladen.")