import time
from collections.abc import Awaitable
from ssl import SSLError
from typing import Callable

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import TelegramObject, Update

from app.metrics import COMMAND_COUNT, NETWORK_ERRORS, REQUEST_COUNT, REQUEST_LATENCY, SSL_ERRORS


class MetricsCollector(BaseMiddleware):
    """Collect performance metrics and track system events."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Process incoming events with metrics tracking."""
        start_time = time.time()
        status = 'success'

        try:
            result = await handler(event, data)
            return result

        except SSLError:
            SSL_ERRORS.inc()
            raise

        except TelegramNetworkError:
            NETWORK_ERRORS.labels(error_type='TelegramNetworkError').inc()
            raise

        except Exception:
            status = 'error'
            raise

        finally:
            self._record_metrics(event, start_time, status)

    def _record_metrics(self, event: TelegramObject, start_time: float, status: str) -> None:
        """Record all metrics for the processed event."""
        latency = time.time() - start_time
        event_type = self._get_event_type(event)
        command = self._get_command(event)

        REQUEST_LATENCY.labels(handler=event_type).observe(latency)
        REQUEST_COUNT.labels(handler=event_type, status=status).inc()

        if command:
            COMMAND_COUNT.labels(command=command).inc()
            if command == 'dr_':
                REQUEST_LATENCY.labels(handler='dr_participate').observe(latency)

    @staticmethod
    def _get_event_type(event: TelegramObject) -> str:
        """Determine event type for metrics labeling."""
        if isinstance(event, Update):
            if event.message:
                return 'message'
            if event.callback_query:
                return 'callback_query'
            if event.edited_message:
                return 'edited_message'
            if event.channel_post:
                return 'channel_post'
        return 'unknown'

    @staticmethod
    def _get_command(event: TelegramObject) -> str | None:
        """Extract command from event data."""
        if isinstance(event, Update) and (msg := event.message) and msg.text and msg.text.startswith('/'):
            return msg.text.split()[0][1:]
        return None
