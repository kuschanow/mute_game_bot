from aiogram import Router

from .skip import skip_router
from .warnings import warnings_router

unhandled_router = Router()

unhandled_router.include_routers(skip_router, warnings_router)


