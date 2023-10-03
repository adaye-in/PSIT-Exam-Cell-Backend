from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from collageInfo.models import BranchModel
from collageInfo.serializer import BranchModelSerializerResponse
from .serializers import *


class sessionDetailsViewSets(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def getSessionStudents(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        branch_id = request.data.get('branch_id', None)
        section_id = request.data.get('section_id', None)
        session_id = request.data.get('session_id', None)

        if not branch_id or not section_id or not session_id:
            return response_fun(0, "Branch/Section/Session Not Found")

        student_obj = admin_user.seatingplan_seatingplanmodel_related.filter(
            branch_id=branch_id,
            section_id=section_id,
            session_id=session_id,
            marked=False
        )

        student_obj = sorted(student_obj, key=lambda x: x.student_rn)

        serializer = SessionStudentSerializer(student_obj, many=True)
        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def getSessionBranch(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if not session_id:
            return response_fun(0, "Session Id Not Found")

        branch_obj = admin_user.seatingplan_seatingplanmodel_related.filter(
            session_id=session_id
        ).values('branch_id').distinct()

        branch_ids = [x['branch_id'] for x in list(branch_obj)]

        branch_obj = BranchModel.objects.filter(
            pk__in=branch_ids
        )
        serializer = BranchModelSerializerResponse(branch_obj, many=True)
        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def getSessionRooms(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)

        val_arr = [0, 1, '1', '0']
        sm = request.GET.get('sm', 0)  # sm=SeatingMap
        marked = request.GET.get('marked', 0)
        room_id = request.data.get('room_id', None)

        if sm not in val_arr and marked not in val_arr:
            return response_fun(0, "Invalid Get Params")

        sm = int(sm)
        marked = int(marked)

        if sm == 1 and not room_id:
            return response_fun(0, "RoomId Not Found")

        if marked == 0:
            marked = False
        elif marked == 1:
            marked = True

        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if not session_id:
            return response_fun(0, "Session Id Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.filter(
            pk=session_id
        ).first()

        if not session_obj:
            return response_fun(0, "Session Not Found")

        if sm == 1:
            session_room = admin_user.seatingplan_roomseatingmodel_related.filter(
                session=session_id,
                marked=True,
                pk=room_id
            )
        else:
            session_room = admin_user.seatingplan_roomseatingmodel_related.filter(
                session=session_id,
                marked=marked
            )

        serializer = RoomSeatingSerializerResponse(session_room, many=True, sm=sm)
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

        student_id_list = [student.get('student_id') for arr in seatingplan for student in arr if
                           student and student.get('student_id', None)]

        room_obj = admin_user.seatingplan_roomseatingmodel_related.filter(
            pk=room_id,
            session_id=session_id
        ).first()

        if not room_obj:
            return response_fun(0, "Room Not Found")

        if room_obj.marked:
            return response_fun(0, "Room Already Filled")

        try:
            with transaction.atomic():
                admin_user.seatingplan_roomseatingmodel_related.filter(
                    pk=room_id,
                    session_id=session_id
                ).update(
                    seating_map=seatingplan,
                    marked=True
                )

                admin_user.seatingplan_seatingplanmodel_related.filter(
                    pk__in=student_id_list,
                    session_id=session_id
                ).update(
                    marked=True,
                    room=room_id
                )
                return response_fun(1, "Seating Plan Updated Successfully")

        except Exception as e:
            return response_fun(0, str(e))

    @action(detail=False, methods=['post'])
    def clearRoom(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        room_id = request.data.get('room_id', None)

        if not session_id or not room_id:
            return response_fun(0, "Unprocessable Entity")

        room_obj = admin_user.seatingplan_roomseatingmodel_related.filter(
            pk=room_id,
            session_id=session_id
        ).first()

        if not room_obj:
            return response_fun(0, "Room Not Found")

        seating_map = room_obj.seating_map
        student_id_list = [student.get('student_id') for arr in seating_map for student in arr if
                           student and student.get('student_id', None)]

        try:
            with transaction.atomic():
                admin_user.seatingplan_roomseatingmodel_related.filter(
                    pk=room_id,
                    session_id=session_id
                ).update(
                    seating_map=None,
                    marked=False
                )

                admin_user.seatingplan_seatingplanmodel_related.filter(
                    pk__in=student_id_list,
                    session_id=session_id
                ).update(
                    marked=False,
                    room=None
                )
                return response_fun(1, "Room Updated Successfully")

        except Exception as e:
            return response_fun(0, str(e))
