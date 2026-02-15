import discord
import logging
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord.app_commands import Group


#Logger erstellen
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8")
datum_format = "%Y-%m-%d %H-%M-%S"
formatieren = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", datum_format, style="{")
handler.setFormatter(formatieren)
logger.addHandler(handler)


#Embeds
async def send_error(interaction, error, embed_description: str, embed_color: discord.Color, 
                     embed_icon_url: str, embed_author: str, embed_footer: str):
    embed = discord.Embed(
            description=embed_description,
            color=embed_color,
            timestamp=datetime.now()
        )
    embed.set_author(name=embed_author, icon_url=embed_icon_url)
    embed.set_footer(text=embed_footer)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    logger.error(f"Unbekannter Fehler aufgetretten! {error}")

async def embed_send(interaction, embed_description: str, embed_color: discord.Color, 
                     embed_icon_url: str, embed_author: str, embed_footer: str):
    embed = discord.Embed(
        description=embed_description,
        color=embed_color,
        timestamp=datetime.now()
    )
    embed.set_author(name=embed_author, icon_url=embed_icon_url)
    embed.set_footer(text=embed_footer)

    await interaction.response.send_message(embed=embed)


# Modal
class CreateModal(discord.ui.Modal, title="⏰ - Create Task"):
    def __init__(self):
        super().__init__()
        self.timeout = 30
    title_modal = discord.ui.TextInput(
        label="Task Title",
        placeholder="e.g. program a Discord bot",
        max_length=50
    )
    des = discord.ui.TextInput(
        label="Task Description",
        placeholder="e.g. programm a Discord bot für NexoryOrg (moderation and logging)",
        max_length=500
    )
    time = discord.ui.TextInput(
        label="Finish date",
        placeholder="YYYY-MM-DD",
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            date = datetime.strptime(self.time.value, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if date <= today:
                return await interaction.response.send_message("⛔ - The date must be in the future! Please enter a future date.", ephemeral=True)

            if date > today:

                async with interaction.client.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT task_title FROM nexory_tasks WHERE guildID = (%s)", int(interaction.guild.id))
                        db_daten = await cur.fetchone()
                        if db_daten[0] != self.title.value:

                            try:
                                await cur.executecur.execute("INSERT INTO nexory_tasks (guildID, title, des, date) VALUES (%s, %s, %s, %s)",
                                                            (interaction.guild.id, self.title.value, self.des.value, date))
                            
                            except:
                                return await send_error(interaction, "Datenbank Fehler", "Es ist ein unbekannter Fehler aufgetretten ([Support Server](https://discord.gg/wGFzPk45hr))",
                                                    discord.Color.red(), interaction.user.display_avatar.url, "Fehlermeldung", "https://github.com/NexoryOrg")

                            embed = discord.Embed(
                                color=discord.Color.dark_blue(),
                                timestamp=datetime.now()
                            )
                            embed.set_author(name="✅ - Created Task", icon_url=interaction.user.display_avatar.url)
                            embed.add_field(name="Title", value=self.title_modal.value, inline=False)
                            embed.add_field(name="Description", value=self.des.value, inline=False)
                            embed.add_field(name="Finish date", value=date, inline=False)
                            embed.set_footer(text="https://github.com/NexoryOrg")
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                        
                        if db_daten[0] == self.title.value:
                            return await interaction.response.send_message("⛔ - Please don't create the same task twice.", ephemeral=True)

                        else:
                            await send_error(interaction, "Datenbank Fehler", "Es ist ein unbekannter Fehler aufgetretten ([Support Server](https://discord.gg/wGFzPk45hr))",
                            discord.Color.red(), interaction.user.display_avatar.url, "Fehlermeldung", "https://github.com/NexoryOrg")
            
            else:
                await send_error(interaction, "Datum Fehler", "Es ist ein unbekannter Fehler aufgetretten ([Support Server](https://discord.gg/wGFzPk45hr))",
                         discord.Color.red(), interaction.user.display_avatar.url, "Fehlermeldung", "https://github.com/NexoryOrg")

        except ValueError:
            return await interaction.response.send_message("⛔ - Invalid date! Please enter it in the format YYYY-MM-DD.", ephemeral=True)
    
    async def on_error(self, interaction, error: Exception):
        await send_error(interaction, error, "Es ist ein unbekannter Fehler aufgetretten ([Support Server](https://discord.gg/wGFzPk45hr))",
                         discord.Color.red(), interaction.user.display_avatar.url, "Fehlermeldung", "https://github.com/NexoryOrg")
        
    async def on_timeout(self):
        return await super().on_timeout()


class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        return await super().cog_unload()


    tasks_group = app_commands.Group(name="tasks", description="Command Group to creat Tasks", guild_only=True)

    @tasks_group.command(name="create", description="Create an new Task")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CreateModal())
                 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tasks(bot))