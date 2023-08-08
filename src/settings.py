import os
from pydantic import BaseSettings


current_dir = os.path.dirname(__file__)


class Settings(BaseSettings):
    APP_NAME: str = 'trading_bot_api'
    SERVER_HOST: str = '0.0.0.0'
    SERVER_PORT: int = 8000

    # k8s vars
    POD_NAME: str = None

    ENV: str = "dev" if not POD_NAME else "qa" if "-qa-" in POD_NAME else "prod" if "-prod-" in POD_NAME else "dev"
    GIT_TAG_NAME: str = "0.0.0"
    GIT_COMMIT_ID: str = "none"

    # KEYCLOAK
    KEYCLOAK_URL: str = "https://keycloak.tradebot.shop/auth/realms/trade-bot/protocol/openid-connect/token"

    # admin role
    ADMIN_ROLE: str = "web_admin"

    # DATABSE
    DATABASE_URL: str = "postgresql://postgres:postgres@178.154.223.5:5432/postgres"
    DB_MAX_CONNECTIONS: int = 10
    DC_POOL_RECYCLE: int = 60

    # n threads
    N_WORKERS = 2

    # miliseconds
    SOCKET_TIMEOUT = 500

    # META TRADER
    MAX_TRIES: int = 5


    # CELERY
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # k8s
    config_path: str = current_dir + "/config_dec.yml"
    namespace: str = "trade-bot-client"
    k8s_name: str = "server"
    image: str = "northamerica-northeast1-docker.pkg.dev/spheric-algebra-331409/trading-bot/mt5:0.1.1"
    compiler_image: str = "cr.yandex/crp11o4i1hlgiik650c5/compiler:0.2.1"

    # blob
    BUCKET_KEY: str = 'YCOep8FeknGyD8RvT9sltUHOQ-hjw7BGAxZjfk_1'
    BUCKET_NAME: str = 'trade-bot-strategy'
    AWS_ACCESS_KEY_ID:str = 'YCAJEO8rSWqHkT01hPF3mUOks'
    AWS_BUCKET_ENDPOINT: str = 'https://storage.yandexcloud.net'

    # mail
    SMTP_SERVER: str = 'smtp.yandex.ru'
    SMTP_PORT: int = 465
    SMTP_FROM: str = 'support@tradebot.shop'
    SMTP_FROM_PASSWORD: str = 'nvslvvejhpzyfzqe'

    # logging
    LOG_LEVEL: str = "DEBUG"
    LOG_LEVEL_ROOT: str = "DEBUG"
    LOG_LEVEL_ASYNCIO: str = "DEBUG"


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
