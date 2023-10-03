import concurrent.futures
from datetime import datetime

from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from collageInfo.serializer import RoomModelSerializer
from seatingplan.serializers import SeatingPlanSerializer, RoomSeatingSerializer
from student.serializer import StudentListSerializerSeatingPlan
from .serializers import SessionModelSerializer, SessionModelSerializerResponse


class SessionViewSet(viewsets.ViewSet):

    @staticmethod
    def get_student(admin_user, branch_id, section_years):
        filtered_students = admin_user.student_studentmodel_related.filter(
            branch_id=branch_id,
            section__present_year__in=section_years
        )
        serializer = StudentListSerializerSeatingPlan(filtered_students, many=True)
        return serializer.data

    @action(detail=False, methods=['post'])
    def createSession(self, request):
        """
        :param request:
        :return:
        [
            {
                branch: id,
                years = [1,2,3]
            },
        ]
        """
        try:
            with transaction.atomic():
                admin_user = JWTAuthentication().authenticate_user(request)
                req_data = request.data.get('branch_data', None)
                session_name = request.data.get('session_name', None)
                if not admin_user:
                    return response_fun(0, "User Not Found")

                if not req_data or not session_name:
                    return response_fun(0, "Unprocessable Entity")

                #  Validate that the data send is Correct
                for student_list in req_data:
                    branchObj = admin_user.collageinfo_branchmodel_related.filter(
                        id=student_list.get('branch_id', None)
                    ).first()

                    if not branchObj:
                        return response_fun(0, "Branch Id Not Found")

                    yr = branchObj.duration_of_course_year
                    years = student_list.get('years', None)
                    if not years or years == []:
                        return response_fun(0, "Branch Year Not Found")
                    min_yrs = min(years)
                    max_yrs = max(years)

                    if not (0 < min_yrs and max_yrs <= yr):
                        return response_fun(0, "Years Found Invalid")

                session_data = {
                    'user': admin_user.pk,
                    'session_name': session_name,
                    'branch_data': req_data,
                    'created_on': datetime.now()
                }

                sessionSerializer = SessionModelSerializer(data=session_data)
                if sessionSerializer.is_valid():
                    sessionSerializer.save()
                    session_pk = sessionSerializer.instance.pk
                else:
                    return response_fun(0, sessionSerializer.errors)

                students_list = []
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(self.get_student, admin_user, filter_data['branch_id'], filter_data['years'])
                        for filter_data in req_data
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        students_list.extend(future.result())

                for student in students_list:
                    student['session'] = session_pk

                serializer = SeatingPlanSerializer(data=students_list, many=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return response_fun(1, serializer.errors)

                rooms_obj = admin_user.collageinfo_roommodel_related.all()
                serializer = RoomModelSerializer(rooms_obj, many=True)
                room_data = serializer.data

                for room in room_data:
                    room['session'] = session_pk

                room_serializer = RoomSeatingSerializer(data=room_data, many=True)
                if room_serializer.is_valid():
                    room_serializer.save()
                else:
                    return response_fun(0, room_serializer.errors)

                return response_fun(1, "Session Created Successfully")
        except Exception as e:
            return response_fun(0, str(e))

    @action(detail=False, methods=['post'])
    def deleteSession(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        sessionId = request.data.get('session_id', None)

        if not sessionId:
            return response_fun(0, "SessionId Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.filter(
            id=sessionId
        ).first()

        if not session_obj:
            return response_fun(0, "Session Object Not Found")

        session_obj.delete()
        return response_fun(1, "Session Deleted Successfully")

    @action(detail=False, methods=['post'])
    def getSession(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.all()
        serializer = SessionModelSerializerResponse(session_obj, many=True)

        return response_fun(1, serializer.data)
