from .models import *

from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from .serializer import *


class SessionViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def createSession(self, request):
        admin_user = JWTAuthentication().authenticate_user(request)
        data = request.data

        if not admin_user:
            return response_fun(0, "User Not Found")

        return response_fun(1, "User Found")
