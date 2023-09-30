from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from .serializers import *
from .models import SeatingPlanModel


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
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        room_id = request.data.get('room_id', None)
        seatingplan = request.data.get('seatingplan', [])

        if not session_id or not room_id or seatingplan == []:
            return response_fun(0, "Unprocessable Entity")

        student_id_list = []
        for arr in seatingplan:
            for oneStudent in arr:
                student_id_list.append(oneStudent['student_id'])

        obj = SeatingPlanModel.objects.filter(
            pk__in=student_id_list
        )
        print(obj)
        return response_fun(1, "ok")
