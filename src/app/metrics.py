# """Prometheus exporter."""

from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter("loads_total", "Successful blob loads")
LATENCY_HISTO = Histogram(
    "load_seconds", "Latency per blob", buckets=(1, 2, 5, 10, 20, 30, 60, 120)
)

# Expose /metrics on a sidecar port 8000
start_http_server(8000)