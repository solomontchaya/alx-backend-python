# messaging_app/middleware.py
from datetime import datetime
import logging
from django.http import HttpResponseForbidden

# Configure logging to write to a file
logging.basicConfig(
    filename='request.logs',  # File where logs will be saved
    level=logging.INFO,
    format='%(message)s'
)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_message)

        response = self.get_response(request)
        return response
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Deny access outside the allowed hours:
        Allowed window = 6PM (18:00) to 9PM (21:00)
        """
        now = datetime.now().time()
        start = datetime.strptime("18:00", "%H:%M").time()  # 6 PM
        end   = datetime.strptime("21:00", "%H:%M").time()  # 9 PM

        if not (start <= now <= end):
            return HttpResponseForbidden(
                "Access to the messaging app is only allowed between 6 PM and 9 PM."
            )

        return self.get_response(request)