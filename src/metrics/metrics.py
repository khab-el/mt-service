import prometheus_client as pc

from src.settings import settings


requests = pc.Counter(
    documentation="api requests total",
    name="requests_total",
    namespace=settings.APP_NAME,
    labelnames=["path", "method"],
)

responses = pc.Counter(
    documentation="api response status codes",
    name="responses_total",
    namespace=settings.APP_NAME,
    labelnames=["path", "method", "status"],
)

timings = pc.Histogram(
    documentation="api successfull responsees",
    name="response_duration",
    unit="seconds",
    namespace=settings.APP_NAME,
    labelnames=["path", "method"],
    buckets=(
        0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0,
        1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 10.0,
        pc.utils.INF,
    )
)
