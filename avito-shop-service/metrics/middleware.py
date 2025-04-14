import logging
import time

from fastapi import Request
from metrics.metrics import REQUEST_COUNT, REQUEST_LATENCY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    method = request.method
    endpoint = request.url.path
    status_code = str(response.status_code)

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

    return response
