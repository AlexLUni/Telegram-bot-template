import configparser
import logging
import os
from pathlib import Path
from typing import TypedDict


logger = logging.getLogger(__name__)


class BotConfig(TypedDict):
    """Bot configuration."""

    token: str


class DBConfig(TypedDict):
    """Database configuration."""

    url: str
    host: str
    port: str
    db: str
    user: str
    password: str


class ProxyConfig(TypedDict):
    """Proxy configuration."""

    host: str | None
    port: str | None


class AppConfig(TypedDict):
    """Application configuration."""

    bot: BotConfig
    database: DBConfig
    proxy: ProxyConfig


def init_config() -> AppConfig:
    """Load config from ini."""
    config = configparser.ConfigParser()
    resources_path = str(Path(__file__).parent / 'resources.ini')

    try:
        config.read(resources_path)
        logger.debug('Successfully loaded resources file')
    except Exception:
        logger.exception('Failed to read from resources file')
        raise

    try:
        token = os.getenv('TG_TOKEN') or config.get('file_bot', 'TG_TOKEN')
        logger.debug('Successfully read telegram token')

        db = os.getenv('POSTGRES_DB') or config.get('file_bot', 'POSTGRES_DB')
        user = os.getenv('POSTGRES_USER') or config.get('file_bot', 'POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD') or config.get('file_bot', 'POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST') or config.get('file_bot', 'POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT') or config.get('file_bot', 'POSTGRES_PORT')
        url = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'
        logger.debug('Successfully read db variables')

        proxy_host = os.getenv('PROXY_HOST') or config.get('file_bot', 'PROXY_HOST', fallback='') or ''
        proxy_port = os.getenv('PROXY_PORT') or config.get('file_bot', 'PROXY_PORT', fallback='') or ''
        logger.debug('Successfully read proxy variables')

        return {
            'bot': {'token': token},
            'database': {
                'url': url,
                'host': host,
                'port': port,
                'db': db,
                'user': user,
                'password': password,
            },
            'proxy': {
                'host': proxy_host,
                'port': proxy_port,
            },
        }
    except Exception:
        logger.exception('Error while extracting config in init_config')
        raise


try:
    config = init_config()
    logger.info('Application configuration initialized successfully')
except Exception as e:
    logger.critical('Failed to initialize application configuration: %s', e)
    raise
