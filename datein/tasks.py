import discord
import logging
from discord.ext import commands
from discord import app_commands
from datetime import datetime

#Logger setup
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8")
datum_format = "%Y-%m-%d %H-%M-%S"
formatieren = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", datum_format, style="{")
handler.setFormatter(formatieren)
logger.addHandler(handler)


#error embed function
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
    logger.error(f"Unbekannter Fehler aufgetreten! {error}")


#Create Modal
class CreateModal(discord.ui.Modal, title="⏰ - Create Task"):
    def __init__(self, table_type: str):
        super().__init__()
        self.timeout = 30
        self.table_type = table_type

        self.title_modal = discord.ui.TextInput(
            label="Task Title",
            placeholder="e.g. program a Discord bot",
            max_length=50
        )
        self.des = discord.ui.TextInput(
            label="Task Description",
            placeholder="e.g. programm a Discord bot für NexoryOrg (moderation and logging)",
            max_length=500
        )
        self.time = discord.ui.TextInput(
            label="Finish date",
            placeholder="YYYY-MM-DD",
            max_length=10
        )

        self.add_item(self.title_modal)
        self.add_item(self.des)
        self.add_item(self.time)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            date = datetime.strptime(self.time.value, "%Y-%m-%d").date()
            today = datetime.now().date()
            if date <= today:
                return await interaction.response.send_message(
                    "⛔ - The date must be in the future! Please enter a future date.",
                    ephemeral=True
                )

            async with interaction.client.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if self.table_type == "user":
                        table_name = "nexory_user_tasks"
                        table_term = "userID"
                        id_value = interaction.user.id
                    else:
                        table_name = "nexory_guild_tasks"
                        table_term = "guildID"
                        id_value = interaction.guild.id

                    await cur.execute(
                        f"SELECT 1 FROM {table_name} WHERE {table_term} = %s AND title = %s",
                        (id_value, self.title_modal.value)
                    )
                    db_daten = await cur.fetchone()
                    if db_daten:
                        return await interaction.response.send_message(
                            "⛔ - Please don't create the same task twice.",
                            ephemeral=True
                        )

                    await cur.execute(
                        f"INSERT INTO {table_name} ({table_term}, title, des, date) VALUES (%s, %s, %s, %s)",
                        (id_value, self.title_modal.value, self.des.value, date)
                    )
                    await conn.commit()

            embed = discord.Embed(
                color=discord.Color.dark_blue(),
                timestamp=datetime.now()
            )
            embed.set_author(
                name="✅ - Created Task",
                icon_url=interaction.user.display_avatar.url
            )
            embed.add_field(name="Title", value=self.title_modal.value, inline=False)
            embed.add_field(name="Description", value=self.des.value, inline=False)
            embed.add_field(name="Finish date", value=str(date), inline=False)
            embed.set_footer(text="https://github.com/NexoryOrg")

            await interaction.response.send_message(embed=embed)

        except ValueError:
            return await interaction.response.send_message(
                "⛔ - Invalid date! Please enter it in the format YYYY-MM-DD.",
                ephemeral=True
            )

        except Exception as e:
            await send_error(
                interaction,
                e,
                "Es ist ein unbekannter Fehler aufgetreten ([Support Server](https://discord.gg/wGFzPk45hr))",
                discord.Color.red(),
                interaction.user.display_avatar.url,
                "Fehlermeldung",
                "https://github.com/NexoryOrg"
            )


# Cog
class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    task = app_commands.Group(
        name="task",
        description="Command Group to create Tasks",
        guild_only=True
    )

    #
    #User Tasks
    #

    user =  app_commands.Group(
        name="user",
        description="Subcommand Group for User Tasks",
        guild_only=True
    )

    task.add_command(user)

    @user.command(name="create", description="Create a new User-Task")
    async def create_user(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CreateModal("user"))

    
    @user.command(name="delete", description="Delete a User-Task by its title")
    async def delete_user(self, interaction: discord.Interaction, title: str):
        async with interaction.client.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM nexory_user_tasks WHERE userID = %s AND title = %s",
                    (interaction.user.id, title)
                )
                await conn.commit()
        await interaction.response.send_message(f"✅ - The task with the title `{title}` has been deleted.", ephemeral=True)


    @user.command(name="list", description="List all User-Tasks")
    async def list_guild(self, interaction: discord.Interaction):
        async with interaction.client.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT title, des, date FROM nexory_user_tasks WHERE userID = %s",
                    (interaction.user.id,)
                )
                db_daten = await cur.fetchall()

        if not db_daten:
            return await interaction.response.send_message("There are currently no tasks for this user.", ephemeral=True)

        embed = discord.Embed(
            color=discord.Color.dark_blue(),
            timestamp=datetime.now()
        )
        embed.set_author(
            name="📋 - User Tasks",
            icon_url=interaction.user.display_avatar.url
        )

        for title, des, date in db_daten:
            embed.add_field(name=f"Title: {title}", value=f"Description: {des}\nFinish date: {date}", inline=False)

        embed.set_footer(text="https://github.com/NexoryOrg")  
        await interaction.response.send_message(embed=embed)


    #
    #Guild Tasks
    #

    guild = app_commands.Group(
        name="guild",
        description="Subcommand Group for Guild Tasks",
        guild_only=True
    )

    task.add_command(guild)

    @guild.command(name="create", description="Create a new Guild-Task")
    async def create_guild(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CreateModal("guild"))

    
    @guild.command(name="delete", description="Delete a Guild-Task by its title")
    async def delete_guild(self, interaction: discord.Interaction, title: str):
        async with interaction.client.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM nexory_user_tasks WHERE userID = %s AND title = %s",
                    (interaction.user.id, title)
                )
                await conn.commit()
        await interaction.response.send_message(f"✅ - The task with the title `{title}` has been deleted.", ephemeral=True)


    @guild.command(name="list", description="List all Guild-Tasks")
    async def list_guild(self, interaction: discord.Interaction):
        async with interaction.client.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT title, des, date FROM nexory_guild_tasks WHERE guildID = %s",
                    (interaction.guild.id,)
                )
                db_daten = await cur.fetchall()

        if not db_daten:
            return await interaction.response.send_message("There are currently no tasks for this server.", ephemeral=True)

        embed = discord.Embed(
            color=discord.Color.dark_blue(),
            timestamp=datetime.now()
        )
        embed.set_author(
            name="📋 - Guild Tasks",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        for title, des, date in db_daten:
            embed.add_field(name=f"Title: {title}", value=f"Description: {des}\nFinish date: {date}", inline=False)

        embed.set_footer(text="https://github.com/NexoryOrg")  
        await interaction.response.send_message(embed=embed)


# Setup
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tasks(bot))
