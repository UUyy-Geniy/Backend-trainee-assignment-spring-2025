from prometheus_client import Counter, Histogram, REGISTRY

# Технические метрики
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
    registry=REGISTRY
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    registry=REGISTRY
)

# Бизнес-метрики
PVZ_CREATED = Counter(
    "pvz_created_total",
    "Total number of PVZ created",
    registry=REGISTRY
)
RECEPTIONS_CREATED = Counter(
    "receptions_created_total",
    "Total number of receptions created",
    registry=REGISTRY
)
PRODUCTS_ADDED = Counter(
    "products_added_total",
    "Total number of products added",
    registry=REGISTRY
)