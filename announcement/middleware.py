from django.db import connection
from django.db.utils import OperationalError

class DBConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            connection.ensure_connection()
        except OperationalError:
            connection.close()
            connection.ensure_connection()
            
        response = self.get_response(request)
        return response 