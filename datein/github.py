import discord
from discord.ext import commands
from flask import Flask, request
import threading

CHANNEL_ID = 865259553464778773

class Github(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.app = Flask(__name__)

        @self.app.route("/github-webhook", methods=["POST"])
        def github_webhook():
            data = request.json

            if data and data.get("pull_request"):
                action = data.get("action")
                pr = data.get("pull_request")
                title = pr.get("title")
                url = pr.get("html_url")
                user = pr.get("user", {}).get("login")

                channel = self.bot.get_channel(CHANNEL_ID)

                if channel:
                    embed = discord.Embed(
                        title=title,
                        url=url,
                        description=f"👤 {user}\n📌 Action: {action}",
                        color=0x2ecc71
                    )

                    self.bot.loop.create_task(channel.send(embed=embed))

            return "", 200

        threading.Thread(target=self.run_flask).start()

    def run_flask(self):
        self.app.run(host="0.0.0.0", port=5000)

async def setup(bot: commands.Bot):
    await bot.add_cog(Github(bot))