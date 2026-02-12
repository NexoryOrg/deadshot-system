import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
from discord.app_commands import Group

class ButtonView(discord.ui.View):
    def __init__(self, bot, server_log, user_log, prefix):
        super().__init__(timeout=60)
        self.bot = bot
        self.server_log = server_log
        self.user_log = user_log
        self.prefix = prefix

    @discord.ui.button(label="Bestätigen", style=discord.ButtonStyle.blurple, row=0)
    async def bestätigt(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE nexory_setup SET server_log = %s, user_log = %s, prefix = %s WHERE guildID = %s",
                    (self.server_log, self.user_log, self.prefix, interaction.guild.id)
                )

                server_log1 = self.bot.get_channel(self.server_log)
                user_log1 = self.bot.get_channel(self.user_log)
                
                embed = discord.Embed(
                    description=f"Für `{interaction.guild.name}` wurden die Server Setup Daten überschrieben.",
                    color=discord.Color.dark_blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Server Log Kanal", value=server_log1.mention, inline=False)
                embed.add_field(name="User Log Kanal", value=user_log1.mention, inline=False)
                embed.add_field(name="Bot Prefix", value=self.prefix, inline=False)
                embed.set_author(name="✅ - Datenänderung war erfolgreich", icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text="https://github.com/NexoryOrg")

                for child in self.children:
                    child.disabled = True

                await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, row=0)
    async def abgebrochen(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description=f"Die Server Setup Daten wurden nicht überschrieben!",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_author(name="Abgebrochen", icon_url=interaction.user.display_avatar.url)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        return await super().cog_unload()

    setup = Group(name="setup", description="Server Setup Befehle", guild_only=True)

    @setup.command(name="start", description="Starte das Server-Setup für Nexory. [Server-Owner]")
    @app_commands.describe(
        server_log="Textkanal für alle Server Aktivitäten.",
        user_log="Textkanal für alle User Aktivitäten.",
        prefix='Bot Prefix ändern von Standart ("!")'
    )
    async def start(
        self,
        interaction: discord.Interaction,
        server_log: discord.TextChannel,
        user_log: discord.TextChannel,
        prefix: str
    ):
        if interaction.user.id != interaction.guild.owner.id:
            return await interaction.response.send_message(
                "`❌` | Nur der **Server Owner** kann diesen Befehl ausführen",
                ephemeral=True
            )

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM nexory_setup WHERE guildID = %s", (interaction.guild.id,))
                db_daten = await cur.fetchone()

                if db_daten is None:
                    await cur.execute(
                        "INSERT INTO nexory_setup (guildID, server_log, user_log, prefix) VALUES (%s, %s, %s, %s)",
                        (interaction.guild.id, server_log.id, user_log.id, prefix)
                    )

                    embed = discord.Embed(
                        description="Das Server Setup wurde erfolgreich erledigt.",
                        color=discord.Color.dark_blue(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Server Log Kanal", value=server_log.mention, inline=False)
                    embed.add_field(name="User Log Kanal", value=user_log.mention, inline=False)
                    embed.add_field(name="Bot Prefix", value=prefix, inline=False)
                    embed.set_author(name="✅ - Server Setup erledigt", icon_url=interaction.user.display_avatar.url)
                    embed.set_footer(text="https://github.com/NexoryOrg")
                    await interaction.response.send_message(embed=embed)

                else:
                    embed = discord.Embed(
                        description=f"Für `{interaction.guild.name}` gibt es schon ein Server Setup.\nMöchtest du das aktuelle Server Setup überschreiben?",
                        color=discord.Color.orange(),
                        timestamp=datetime.now()
                    )
                    embed.set_author(name="Warnhinweis", icon_url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(
                        embed=embed,
                        view=ButtonView(self.bot, server_log.id, user_log.id, prefix)
                    )

    @setup.command(name="löschen", description="Lösche das Server Setup. [Server-Owner]")
    async def löschen(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.guild.owner.id:
            return await interaction.response.send_message(
                "`❌` | Nur der **Server Owner** kann diesen Command ausführen",
                ephemeral=True
            )

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM nexory_setup WHERE guildID = %s", (interaction.guild.id,))
                db_daten = await cur.fetchone()

                if db_daten:
                    await cur.execute("DELETE FROM nexory_setup WHERE guildID = %s", (interaction.guild.id,))
                    embed = discord.Embed(
                        description=f"Server Setup Daten für `{interaction.guild.name}` erfolgreich **gelöscht**.",
                        color=discord.Color.dark_blue(),
                        timestamp=datetime.now()
                    )
                    embed.set_author(name="✅ - Server Setup Daten gelöscht", icon_url=interaction.user.display_avatar.url)
                    embed.set_footer(text="https://github.com/NexoryOrg")
                    await interaction.response.send_message(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f"Für `{interaction.guild.name}` sind keine Server Setup Daten vorhanden!",
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.set_author(name="Fehlermeldung", icon_url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
