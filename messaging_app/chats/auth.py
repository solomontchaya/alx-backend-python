from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Extend JWTAuthentication if you need extra checks or logging.
    Currently, this just inherits the default behavior.
    """

    def authenticate(self, request):
        # You can hook in custom logic here (logging, IP checks, etc.)
        return super().authenticate(request)