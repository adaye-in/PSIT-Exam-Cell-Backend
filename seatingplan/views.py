from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun


class seatingplanViewSets(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def create(self, request):
        pass
