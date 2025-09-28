# messaging_app/middleware.py
from datetime import datetime
import logging
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')       # creates requests.log in project root
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        return self.get_response(request)
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Deny access outside the allowed hours:
        Allowed window = 4PM (16:00) to 9PM (21:00)
        """
        now = datetime.now().time()
        start = datetime.strptime("16:00", "%H:%M").time()  # 6 PM
        end   = datetime.strptime("21:00", "%H:%M").time()  # 9 PM

        if not (start <= now <= end):
            return HttpResponseForbidden(
                "Access to the messaging app is only allowed between 6 PM and 9 PM."
            )

        return self.get_response(request)