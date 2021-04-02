import logging

import discord
from discord.ext import commands

import solaris
from solaris import Config


class Hub(commands.Cog):
    __slots__ = ("bot", "guild", "commands", "stdout")

    def __init__(self, bot: solaris.bot.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.guild = self.bot.get_guild(Config.HUB_GUILD_ID)
        if self.guild:
            logging.debug(f"The hub guild was set to {self.guild!r}")
            self.commands = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
            self.stdout = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)
            if self.stdout:
                await self.stdout.send(f"Solaris v{solaris.__version__} is online!")
        else:
            logging.warning("The hub guild was not set")
            self.commands = None
            self.stdout = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.bot.user in message.mentions or "all" in message.content:
            if message.channel == self.commands:
                if message.content.lower().startswith("shutdown"):
                    await self.bot.close()

    async def on_shutdown(self) -> None:
        if self.stdout:
            await self.stdout.send(f"Solaris v{solaris.__version__} is shutting down.")


def setup(bot: solaris.bot.Bot) -> None:
    bot.add_cog(Hub(bot))
