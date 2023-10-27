import concurrent.futures
from datetime import datetime

import pandas as pd
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from collageInfo.serializer import RoomModelSerializer
from pdf_utils.CRUD_to_cloud import save_to_aws
from pdf_utils.converthtmltopdf import begin_pdf
from seatingplan.serializers import RoomSeatingSerializerResponse
from seatingplan.serializers import SeatingPlanSerializer, RoomSeatingSerializer
from seatingplan.serializers import SessionStudentSerializer
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
                    raise f"{serializer.errors}"

                rooms_obj = admin_user.collageinfo_roommodel_related.all()
                serializer = RoomModelSerializer(rooms_obj, many=True)
                room_data = serializer.data

                for room in room_data:
                    room['session'] = session_pk

                room_serializer = RoomSeatingSerializer(data=room_data, many=True)
                if room_serializer.is_valid():
                    room_serializer.save()
                else:
                    raise f"{serializer.errors}"

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

    @action(detail=False, methods=['post'])
    def generateDetainedExcel(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if not session_id:
            return response_fun(0, "session Id Not Found")

        if 'file' not in request.FILES:
            return response_fun(0, "File not found")

        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            return response_fun(0, "Only Excel files (.xlsx) are supported")

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return response_fun(0, str(e))

        alreadyDetained = set(admin_user.seatingplan_seatingplanmodel_related.filter(
            isDetained=True,
            session=session_id
        ).values_list('student_rn', flat=True))

        student_list = []

        for index, row in df.iterrows():
            roll_number = row.iloc[0]

            if pd.isna(roll_number) or roll_number == "":
                continue
            student_list.append(roll_number)

        student_set = set(student_list)

        toDetain = student_set - alreadyDetained
        toRemoveDetained = alreadyDetained - student_set

        roomData = admin_user.seatingplan_seatingplanmodel_related.filter(
            room__isnull=False,
            session=session_id
        ).values('room').distinct()

        rooms = []
        if roomData.exists():
            rooms = [i['room'] for i in roomData]

        rooms_query = admin_user.seatingplan_roomseatingmodel_related.filter(
            id__in=rooms,
            session=session_id
        )

        for room in rooms_query:
            sm = room.seating_map
            for row in range(len(sm)):
                for col in range(len(sm[row])):
                    if sm[row][col]['student_roll'] in toDetain:
                        sm[row][col]['isDetained'] = True
                    if sm[row][col]['student_roll'] in toRemoveDetained:
                        sm[row][col]['isDetained'] = False
            room.seating_map = sm

        try:
            with transaction.atomic():
                admin_user.seatingplan_roomseatingmodel_related.bulk_update(rooms_query, ['seating_map'])

                admin_user.seatingplan_seatingplanmodel_related.filter(
                    student_rn__in=toDetain,
                    session=session_id
                ).update(
                    isDetained=True
                )
                admin_user.seatingplan_seatingplanmodel_related.filter(
                    student_rn__in=toRemoveDetained,
                    session=session_id
                ).update(
                    isDetained=False
                )

                # Updating Pdf on AWS
                rooms_query = admin_user.seatingplan_roomseatingmodel_related.filter(
                    id__in=rooms,
                    session=session_id
                )

                data_s = RoomSeatingSerializerResponse(rooms_query, many=True, sm=1).data

                for data in data_s:
                    session_name = str(data['id']) + "".join(data['session_name'].split(" "))
                    pdf_obj_and_name = begin_pdf(data)
                    save_to_aws(pdf_obj_and_name[0], pdf_obj_and_name[1], session_name)

        except Exception as e:
            return response_fun(0, str(e))

        return response_fun(1, "Detained List Updated Successfully")

    @action(detail=False, methods=['post'])
    def getDetainedList(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if not session_id:
            return response_fun(0, "session Id Not Found")

        data = admin_user.seatingplan_seatingplanmodel_related.filter(
            isDetained=True,
            session=session_id
        ).order_by('id')

        serializer = SessionStudentSerializer(data, many=True)

        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def deleteDetainedStudent(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        roll_number = request.data.get('roll_number', None)

        if not session_id:
            return response_fun(0, "Session Id Not Found")
        elif not roll_number:
            return response_fun(0, "Roll Number Not Found")

        data = admin_user.seatingplan_seatingplanmodel_related.filter(
            student_rn=roll_number,
            session_id=session_id,
            isDetained=True
        ).first()

        if data is None:
            return response_fun(1, "Data Updated Successfully")

        room = data.room
        data.isDetained = False
        data.save()
        if room is None:
            return response_fun(1, "Data Updated Successfully")

        room_obj = admin_user.seatingplan_roomseatingmodel_related.filter(
            pk=room.id,
            session_id=session_id,
        ).first()

        sm = room_obj.seating_map
        for row in range(len(sm)):
            for col in range(len(sm[row])):
                if sm[row][col]['student_roll'] == roll_number:
                    sm[row][col]['isDetained'] = False
        room_obj.seating_map = sm
        room_obj.save()

        data = RoomSeatingSerializerResponse(room_obj, sm=1).data
        session_name = str(data['id']) + "".join(data['session_name'].split(" "))
        pdf_obj_and_name = begin_pdf(data)
        save_to_aws(pdf_obj_and_name[0], pdf_obj_and_name[1], session_name)

        return response_fun(1, "Data Updated Successfully")
