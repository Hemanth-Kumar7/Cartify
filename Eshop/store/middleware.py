'''
from django.http import HttpResponse

class AppMaintenanceMiddleware(object):
    def __init__(self, get_response):
        print('Init method Executed')
        self.get_response = get_response

    def __call__(self, request):
        print('Call method Executed')
        response = self.get_response(request)
        return response '''