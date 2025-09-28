import logging
from datetime import datetime
from django.http import HttpResponseForbidden

# Configure logger for middleware
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """
    Middleware that logs each user’s requests with timestamp, user, and path
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to chat between 6PM and 9PM only.
    Outside that range, return 403 Forbidden.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current server time (hour in 24-hour format)
        current_hour = datetime.now().hour

        # Allowed window: between 18 (6PM) and 21 (9PM)
        if request.path.startswith("/chat"):  # restrict only chat endpoints
            if current_hour < 18 or current_hour >= 21:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1><p>Chat is only available between 6PM and 9PM.</p>"
                )

        return self.get_response(request)