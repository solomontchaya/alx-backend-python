import time
from django.http import JsonResponse

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store message counts and timestamps per IP
        self.ip_message_log = {}

    def __call__(self, request):
        # Only limit POST requests to chat message endpoints
        if request.method == 'POST' and request.path.startswith('/api/conversations/'):
            ip = self.get_client_ip(request)
            now = time.time()
            window = 60  # 1 minute window
            max_messages = 5
            # Clean up old entries
            if ip not in self.ip_message_log:
                self.ip_message_log[ip] = []
            # Remove timestamps older than 1 minute
            self.ip_message_log[ip] = [t for t in self.ip_message_log[ip] if now - t < window]
            if len(self.ip_message_log[ip]) >= max_messages:
                return JsonResponse({'error': 'Message limit exceeded. Max 5 messages per minute.'}, status=429)
            self.ip_message_log[ip].append(now)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
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