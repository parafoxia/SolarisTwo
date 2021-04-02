import logging
from pathlib import Path

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pytz import utc

import solaris
from solaris import Config


class Bot(commands.Bot):
    __slots__ = ("_extensions", "scheduler")

    def __init__(self) -> None:
        self._extensions = [p.stem for p in Path(".").glob("./solaris/bot/extensions/*.py")]
        logging.debug(f"Extensions found: {self._extensions}")

        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

        super().__init__(
            command_prefix=Config.DEFAULT_PREFIX,
            status=discord.Status.online,
            intents=discord.Intents.all(),
        )

    def setup(self) -> None:
        for ext in self._extensions:
            self.load_extension(f"solaris.bot.extensions.{ext}")
            logging.info(f"`{ext}` extension loaded")

    def run(self) -> None:
        self.setup()
        super().run(Config.TOKEN, reconnect=True)

    async def close(self) -> None:
        self.scheduler.shutdown()
        await self.get_cog("Hub").on_shutdown()
        await super().close()

    async def on_connect(self) -> None:
        logging.info(f"Connected. DWSP latency: {self.latency * 1000:,.0f} ms")

    async def on_disconnect(self) -> None:
        logging.warning("Disconnected.")

    async def on_ready(self) -> None:
        self.scheduler.start()
        logging.info(f"{len(self.scheduler.get_jobs())} jobs scheduled.")
        logging.info("Ready!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        await self.process_commands(message)

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message, cls=commands.Context)

        if ctx.command is None:
            return

        logging.debug(f"Invoking command `{ctx.command.name}`")
        await self.invoke(ctx)

    async def grab_user(self, arg):
        try:
            return self.get_user(arg) or await self.fetch_user(arg)
        except (ValueError, discord.NotFound):
            return None

    async def grab_channel(self, arg):
        try:
            return self.get_channel(arg) or await self.fetch_channel(arg)
        except (ValueError, discord.NotFound):
            return None

    async def grab_guild(self, arg):
        try:
            return self.get_guild(arg) or await self.fetch_guild(arg)
        except (ValueError, discord.NotFound):
            return None
