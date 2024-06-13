import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import Logger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host
        client_ip = request.headers.get('x-real-ip', 'unknown')
        user_agent = request.headers.get('user-agent', 'unknown')
        host = request.headers.get('host', 'unknown')

        self.logger.log_request(
            client_host,
            client_ip,
            user_agent,
            host,
            request.method,
            str(request.url)
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            self.logger.log_exception(
                client_host,
                client_ip,
                user_agent,
                host,
                exc
            )

            return Response(
                content=json.dumps({"detail": "Internal Server Error"}),
                status_code=500,
                media_type="application/json"
            )

        self.logger.log_response(
            client_host,
            client_ip,
            user_agent,
            host,
            request.method,
            str(request.url),
            response.status_code
        )

        return response
