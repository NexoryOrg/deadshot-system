import discord
import logging
from discord.ext import commands
from discord import app_commands
from datetime import datetime

# Logger setup
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8")
datum_format = "%Y-%m-%d %H-%M-%S"
formatieren = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}",
    datum_format,
    style="{"
)
handler.setFormatter(formatieren)
logger.addHandler(handler)
                

async def send_error(interaction, error, embed_description: str,
                     embed_color: discord.Color,
                     embed_icon_url: str,
                     embed_author: str,
                     embed_footer: str):

    embed = discord.Embed(
        description=embed_description,
        color=embed_color,
        timestamp=datetime.now()
    )

    embed.set_author(name=embed_author, icon_url=embed_icon_url)
    embed.set_footer(text=embed_footer)

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

    logger.error(f"Unbekannter Fehler aufgetreten! {error}")


class CreateModal(discord.ui.Modal, title="⏰ - Create Task"):

    def __init__(self, table_type: str):
        super().__init__()
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
                        f"SELECT 1 FROM {table_name} WHERE {table_term}=%s AND title=%s",
                        (id_value, self.title_modal.value)
                    )

                    if await cur.fetchone():
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

        except Exception as e:
            await send_error(
                interaction,
                e,
                "Es ist ein unbekannter Fehler aufgetreten.",
                discord.Color.red(),
                interaction.user.display_avatar.url,
                "Fehlermeldung",
                "https://github.com/NexoryOrg"
            )


class TaskView(discord.ui.LayoutView):

    def __init__(self, table_type):
        super().__init__(timeout=None)
        self._build()
        self.table_type = table_type

    def _build(self):
        self.clear_items()

        container = discord.ui.Container(
            accent_color=discord.Color.dark_blue().value
        )

        # Header

        container.add_item(
                discord.ui.TextDisplay("# Manage Tasks")
        )

        container.add_item(discord.ui.Separator())

        # Create Section
        create_btn = discord.ui.Button(
            label="Create Task",
            style=discord.ButtonStyle.secondary,
            custom_id="create_task"
        )

        async def create_cb(interaction: discord.Interaction):
            await interaction.response.send_modal(
                CreateModal(self.table_type)
            )

        create_btn.callback = create_cb

        container.add_item(
            discord.ui.TextDisplay("### Create Task")
        )

        container.add_item(discord.ui.ActionRow(create_btn))


        # Edit Section
        container.add_item(
            discord.ui.TextDisplay("### Edit Task")
        )

        select_edit = discord.ui.Select(
            placeholder="Select a Task to edit",
            options=[discord.SelectOption(label="No tasks available", value="none")],
            custom_id="edit_task"
        )

        container.add_item(discord.ui.ActionRow(select_edit))


        # Delete Section
        container.add_item(
            discord.ui.TextDisplay("### Delete Task")
        )

        select_delete = discord.ui.Select(
            placeholder="Select a Task to delete",
            options=[discord.SelectOption(label="No tasks available", value="none")],
            custom_id="delete_task"
        )

        container.add_item(discord.ui.ActionRow(select_delete))

        self.add_item(container)


class tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    task = app_commands.Group(
        name="task",
        description="Command Group to create Tasks",
        guild_only=True
    )

    @task.command(name="user", description="Create a new User-Task")
    async def create_user(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=TaskView("user"))

    @task.command(name="guild", description="Create a new Guild-Task")
    async def create_guild(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=TaskView("guild"))


async def setup(bot: commands.Bot):
    await bot.add_cog(tasks(bot))