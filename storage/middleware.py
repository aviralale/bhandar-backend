from django.utils.deprecation import MiddlewareMixin
from .models import ActivityLog


class ActivityLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.activity_data = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
        }
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMMOTE_ADDR')