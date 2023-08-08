import uvicorn

from src.app.app import init_app
from src.core.logger import get_logger, log_config
from src.settings import settings

logger = get_logger(__name__)


def run(api=False, consume=False):
    app = init_app(api=api, consume=consume)
    try:
        uvicorn.run(
            app,
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            access_log=True,
            log_config=log_config
        )
    except Exception as ex:
        logger.exception("stop_app ex=%s", ex)
        raise
