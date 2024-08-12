from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from bot.logger import logger
import asyncio

async def on_startup(bot: Bot):
    logger.info("Bot is running")

async def on_shutdown(bot: Bot):
    logger.info("Bot is turned off")

class Command(BaseCommand):
    help = "Start telegram bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        from bot.generate_session import bot, dp

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))
