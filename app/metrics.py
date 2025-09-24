import logging

import psutil
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest, start_http_server


logger = logging.getLogger(__name__)

metrics_registry = CollectorRegistry()

COMMAND_COUNT = Counter(
    'bot_commands_total',
    'Total number of commands',
    ['command'],
    registry=metrics_registry,
)

SSL_ERRORS = Counter(
    'bot_ssl_errors_total',
    'Total SSL-related errors',
    ['error_code'],
    registry=metrics_registry,
)

REQUEST_COUNT = Counter(
    'bot_requests_total',
    'Total number of requests',
    ['handler', 'status'],
    registry=metrics_registry,
)

NETWORK_ERRORS = Counter(
    'bot_network_errors_total',
    'Total network errors',
    ['error_type'],
    registry=metrics_registry,
)

REQUEST_LATENCY = Histogram(
    'bot_request_latency_seconds',
    'Request latency in seconds',
    ['handler'],
    registry=metrics_registry,
)

MEMORY_USAGE = Gauge(
    'bot_memory_usage_bytes',
    'Memory usage in bytes',
    registry=metrics_registry,
)


def get_metrics() -> str:
    """Export all metrics in Prometheus text format."""
    try:
        return generate_latest(metrics_registry).decode('utf-8')
    except Exception:
        logger.exception('Metrics export failed')
        return '# ERROR: Metrics generation failed\n'


def update_memory_metric() -> None:
    """Update memory usage gauge with current process stats."""
    try:
        MEMORY_USAGE.set(psutil.Process().memory_info().rss)
    except Exception:
        logger.warning('Memory metrics update failed')


def start_metrics_exporter(port: int = 8000) -> None:
    """Start HTTP server for Prometheus metrics scraping."""
    start_http_server(port, registry=metrics_registry)
