from collections.abc import Awaitable
from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerInjector(BaseMiddleware):
    """Inject scheduler instance into handler context."""

    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        """Initilizer for SchedulerInjector."""

        super().__init__()
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Add scheduler to data context and proceed."""
        data['scheduler'] = self.scheduler
        return await handler(event, data)
