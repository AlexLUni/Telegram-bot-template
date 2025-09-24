
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .metrics_collector import MetricsCollector
from .scheduler_injector import SchedulerInjector
from .user_data_middleware import UserDataMiddleware


user_data = UserDataMiddleware()
metrics_collector = MetricsCollector()


def init_scheduler_injector(scheduler: AsyncIOScheduler) -> SchedulerInjector:
    """Return an instance of AsyncIOScheduler."""
    return SchedulerInjector(scheduler)
