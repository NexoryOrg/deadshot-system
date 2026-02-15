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

        self.initial_extensions = None
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)


    async def setup_hook(self):
        geladene_cogs = 0
        for filename in os.listdir("datein"):
            if filename.endswith(".py"):
                geladene_cogs += 1
                await self.load_extension(f"datein.{filename[:-3]}")
        print(f"Erfolgreich geladen wurden {geladene_cogs} Datein.")

        loop = asyncio.get_event_loop()
        self.pool = await aiomysql.create_pool(host=host, port=3306, user=user, password=passwort, db=db_name, loop=loop, autocommit=True)

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("CREATE TABLE IF NOT EXISTS nexory_tasks(guildID BIGINT, title TEXT, des LONGTEXT, date DATE)")
        #        await cur.execute("CREATE TABLE IF NOT EXISTS nexory_setup(guildID BIGINT, server_log BIGINT, user_log BIGINT, prefix TEXT)")

    async def on_ready(self):
        print(f"Eingeloggt als {self.user}")


bot = MainDatei()


async def main():
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    done = asyncio.run(main())