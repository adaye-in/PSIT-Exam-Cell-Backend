from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from .serializers import *


class sessionRoomViewSets(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def getSessionRooms(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        sm = request.GET.get('sm', 0)  # sm=SeatingMap
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if not session_id:
            return response_fun(0, "Session Id Not Found")

        session_room = admin_user.seatingplan_roomseatingmodel_related.filter(
            session=session_id,
            marked=True
        )

        serializer = RoomSeatingSerializerResponse(session_room, many=True, sm=int(sm))
        return response_fun(1, serializer.data)


class seatingplanViewSets(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def createSP(self, request):
        pass
