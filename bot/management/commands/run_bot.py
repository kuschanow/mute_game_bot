import asyncio

from aiogram import Bot
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from bot.logger import logger


async def on_startup(bot: Bot):
    logger.info("Bot is running")

    for admin_id in settings.ADMINS:
        await bot.send_message(text=_("Bot is running"), chat_id=admin_id)

async def on_shutdown(bot: Bot):
    logger.info("Bot is turned off")

    for admin_id in settings.ADMINS:
        await bot.send_message(text=_("Bot is turned off"), chat_id=admin_id)

class Command(BaseCommand):
    help = "Start telegram bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        from bot.generate_session import bot, dp
        from bot.middlewares import set_middlewares
        from bot.handlers import handlers_router

        set_middlewares(dp)
        dp.include_router(handlers_router)

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))
