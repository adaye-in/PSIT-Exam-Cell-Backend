import concurrent.futures
from datetime import datetime
from io import BytesIO

import boto3
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from django.db import transaction
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, BUCKET_NAME
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
                    # raise f"{serializer.errors}"
                    return response_fun(0, serializer.errors)

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

        session_obj = admin_user.adminsession_sessionmodel_related.all().order_by('created_on')
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
                    session_name = str(data['session']) + "".join(data['session_name'].split(" "))
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
        session_name = str(data['session']) + "".join(data['session_name'].split(" "))
        pdf_obj_and_name = begin_pdf(data)
        save_to_aws(pdf_obj_and_name[0], pdf_obj_and_name[1], session_name)

        return response_fun(1, "Data Updated Successfully")


class ReportViewSet(viewsets.ViewSet):

    @staticmethod
    def checkDifferentStudent(students):
        students = list(map(str, students))
        if len(students[0]) != 13:
            return True

        curr_yr = students[0][:2]
        branch_code = students[0][6:9]

        for student in students:
            if len(student) != 13 or student[:2] != curr_yr or student[6:9] != branch_code:
                return True

        return None

    @staticmethod
    def getStudentCount(admin_user, session_id, section_name, room_number):
        # No use for now
        student_rn_count = admin_user.seatingplan_seatingplanmodel_related.filter(
            section__section_name=section_name,
            room__room_number=room_number,
            session_id=session_id,
            user=admin_user
        ).count()
        return student_rn_count

    @staticmethod
    def getStudent_Min_Max(admin_user, session_id, section_name, room_number):
        # No use for now
        student_rn_values = admin_user.seatingplan_seatingplanmodel_related.filter(
            section__section_name=section_name,
            room__room_number=room_number,
            session_id=session_id,
            user=admin_user
        ).values_list('student_rn', flat=True)

        sorted_numbers = sorted(student_rn_values, key=lambda x: str(x)[:2], reverse=True)

        # Creating partitions
        partitions = {}
        for num in sorted_numbers:
            key = int(str(num)[:2])
            if key in partitions:
                partitions[key].append(num)
            else:
                partitions[key] = [num]

        # Finding minimum from the first partition and maximum from the last partition
        first_partition = partitions[max(partitions.keys())]
        last_partition = partitions[min(partitions.keys())]

        minimum_first_partition = min(first_partition)
        maximum_last_partition = max(last_partition)

        return minimum_first_partition, maximum_last_partition

    @staticmethod
    def get_student_first_last(section_name, seatingMap):
        student = []
        for rows in range(len(seatingMap[0])):
            for cols in range(len(seatingMap)):
                obj = seatingMap[cols][rows]
                if obj and obj.get("section_name") == section_name:
                    student.append(obj["student_roll"])
        if not student:
            return None, None, 0
        diff_rn = ReportViewSet.checkDifferentStudent(student)
        return student[0], student[-1], len(student), diff_rn

    @action(detail=False, methods=['get', 'post'])
    def getStudentReport(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")
        output_buffer = BytesIO()
        session_id = request.data.get('session_id', None)
        if session_id is None:
            return response_fun(0, "Session Id Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.filter(
            pk=session_id
        ).first()

        if session_obj is None:
            return response_fun(0, "Session Does Not Exists")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name='ap-south-2'
        )
        session_name = str(session_obj.id) + "".join(session_obj.session_name.split(" "))
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f'PSIT/{session_name}')

        pdf_writer = PdfWriter()

        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('.pdf'):
                pdf_file = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                pdf_data = pdf_file['Body'].read()

                pdf_reader = PdfReader(BytesIO(pdf_data))

                for page in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page])

        pdf_writer.write(output_buffer)
        output_buffer.seek(0)

        response = HttpResponse(output_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_seating_{session_obj.session_name}.pdf"'
        return response

    @action(detail=False, methods=['get', 'post'])
    def getBranchWiseReport(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if session_id is None:
            return response_fun(0, "Session Id Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.filter(
            pk=session_id
        ).first()

        if session_obj is None:
            return response_fun(0, "Session Does Not Exists")

        report_data = admin_user.seatingplan_seatingplanmodel_related.filter(
            session_id=session_id, user=admin_user, room__isnull=False
        ).values_list('section__section_name', 'room__room_number', 'section__present_year',
                      'branch__branch_name', 'room__seating_map').distinct(
            'section__section_name', 'room__room_number'
        ).order_by('section__section_name')

        final_data = {}
        for item in report_data:
            section_name, room_number, yr, branch_name, sm = item[0], item[1], item[2], item[3], item[4]
            if yr not in final_data:
                final_data[yr] = {}
            if branch_name not in final_data[yr]:
                final_data[yr][branch_name] = {}
            if section_name not in final_data[yr][branch_name]:
                # min_rn, max_rn = ReportViewSet.getStudent_Min_Max(admin_user, session_id, section_name, room_number)
                min_rn, max_rn, count, isdiff = ReportViewSet.get_student_first_last(section_name, sm)
                final_data[yr][branch_name][section_name] = [[room_number, min_rn, max_rn, isdiff]]
            else:
                min_rn, max_rn, count, isdiff = ReportViewSet.get_student_first_last(section_name, sm)
                temp_data = [room_number, min_rn, max_rn, isdiff]
                final_data[yr][branch_name][section_name].append(temp_data)

        def generate_excel(data):
            excel_data = []
            for key, value in data.items():
                for inner_key, inner_value in value.items():
                    excel_data.append([key, inner_key, None, None, None, None, None])
                    for sub_key, sub_value in inner_value.items():
                        excel_data.append([None, None, sub_key, None, None, None, None])
                        for sub_list in sub_value:
                            #     first = str(sub_list[-2])[:2]
                            #     last = str(sub_list[-1])[:2]
                            #     isDifferent = None
                            #     if first != last:
                            #         isDifferent = True
                            excel_data.append([None, None, None, *sub_list])

            # Create a pandas DataFrame from the data
            df = pd.DataFrame(excel_data, columns=["Year", "Branch", "Section", "Room_Number", "From", "To", "verify"])
            excel_buffer = BytesIO()
            # Write DataFrame to an Excel file
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, merge_cells=True)
                excel_buffer.seek(0)
            return excel_buffer

        excel_buffer_final = generate_excel(final_data)
        response = HttpResponse(excel_buffer_final.getvalue(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=output_data.xlsx'
        return response
        # return response_fun(1, final_data)

    @action(detail=False, methods=['get', 'post'])
    def getRoomWiseReport(self, request):
        admin_user = JWTAuthentication.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        session_id = request.data.get('session_id', None)
        if session_id is None:
            return response_fun(0, "Session Id Not Found")

        session_obj = admin_user.adminsession_sessionmodel_related.filter(
            pk=session_id
        ).first()

        if session_obj is None:
            return response_fun(0, "Session Does Not Exists")

        report_data = admin_user.seatingplan_seatingplanmodel_related.filter(
            session_id=session_id, user=admin_user, room__isnull=False
        ).values_list('section__section_name', 'room__room_number', 'section__present_year',
                      'branch__branch_name', 'room__seating_map').distinct(
            'section__section_name', 'room__room_number'
        ).order_by('room__room_number')

        final_data = {}

        for item in report_data:
            # print(item)
            section_name, room_number, yr, branch_name, sm = item[0], item[1], item[2], item[3], item[4]
            if room_number in final_data:
                min_rn, max_rn, count, isdiff = ReportViewSet.get_student_first_last(section_name, sm)
                final_data[room_number].append([min_rn, max_rn, section_name, count, isdiff])
            else:
                min_rn, max_rn, count, isdiff = ReportViewSet.get_student_first_last(section_name, sm)
                final_data[room_number] = [[min_rn, max_rn, section_name, count, isdiff]]

        def generate_excel(data):
            excel_data = []
            for key, value in data.items():
                excel_data.append([key, None, None, None, None, None])
                for room_item in value:
                    # first = str(room_item[0])[:2]
                    # last = str(room_item[1])[:2]
                    # isDifferent = None
                    # if first != last:
                    #     isDifferent = True
                    excel_data.append([None, *room_item])

            # Create a pandas DataFrame from the data
            df = pd.DataFrame(excel_data, columns=["ROOM", "FROM", "TO", "SECTION", "COUNT", "VERIFY"])
            excel_buffer = BytesIO()
            # Write DataFrame to an Excel file
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, merge_cells=True)
                excel_buffer.seek(0)

            return excel_buffer

        excel_buffer_final = generate_excel(final_data)
        response = HttpResponse(excel_buffer_final.getvalue(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=output_data.xlsx'
        return response
