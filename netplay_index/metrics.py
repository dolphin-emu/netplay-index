"""Provides metrics via prometheus_client"""

from tornado.web import RequestHandler

import prometheus_client

API_REQUEST_COUNT = prometheus_client.Counter(
    "api_request_count", "Number of requests sent to the API"
)
API_SESSION_COUNT = prometheus_client.Counter(
    "api_session_count", "Number of sessions added to the index"
)
API_ACTIVE_SESSION_COUNT = prometheus_client.Gauge(
    "api_active_session_count", "Number of sessions currently on the index"
)
API_SESSION_DETAILS_COUNT = prometheus_client.Counter(
    "api_session_details_count",
    "Details on sessions added to the index",
    ["game", "password", "method", "version"],
)


class MetricsHandler(RequestHandler):
    def get(self):
        self.write(prometheus_client.generate_latest())
        self.set_header("Content-Type", prometheus_client.CONTENT_TYPE_LATEST)
