import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import aiomysql

load_dotenv()
token = os.getenv("TOKEN")
host = os.getenv("HOST")
user = os.getenv("USER")
passwort = os.getenv("PASSWORT")
db_name = os.getenv("DB_NAME")


class MainDatei(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        geladene_cogs = 0
        cog_files = [f for f in os.listdir("datein") if f.endswith(".py")]
        print(f"Gefundene Cogs: {len(cog_files)}")
        for filename in cog_files:
            await self.load_extension(f"datein.{filename[:-3]}")
            geladene_cogs += 1
            print(f"Cog geladen: {filename} ({geladene_cogs}/{len(cog_files)})")

        print("Verbindung zur Datenbank wird aufgebaut...")
        try:
            print(host, user, db_name)
            self.pool = await aiomysql.create_pool(
        #        host=host,
        #        port=3306,
        #        user=user,
        #        password=passwort,
        #        db=db_name,
            )
            print("✅ Datenbank verbunden!")
        except Exception as e:
            print(f"❌ Fehler bei der Datenbankverbindung: {e}")
            return

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DROP TABLE IF EXISTS nexory_user_tasks")
                await cur.execute("DROP TABLE IF EXISTS nexory_guild_tasks")
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS nexory_user_tasks(userID BIGINT, title TEXT, des LONGTEXT, date DATE, remindme BOOLEAN DEFASULT FALSE)"
                )
                print("Tabelle nexory_user_tasks überprüft/erstellt.")
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS nexory_guild_tasks(guildID BIGINT, title TEXT, des LONGTEXT, date DATE, remindme BOOLEAN DEFASULT FALSE)"
                )
                print("Tabelle nexory_guild_tasks überprüft/erstellt.")
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS nexory_setup(guildID BIGINT, server_log BIGINT, user_log BIGINT, prefix TEXT)"
                )
                print("Tabelle nexory_setup überprüft/erstellt.")

    async def on_ready(self):
        print(f"✅ Eingeloggt als {self.user}")


bot = MainDatei()


async def main():
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
