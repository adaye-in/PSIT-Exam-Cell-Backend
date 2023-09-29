import concurrent.futures
from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from student.serializer import StudentListSerializerSeatingPlan
from .serializers import SessionModelSerializer


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
                branch_name = CSE,
                years = [1,2,3]
            },
        ]
        """
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
            student['session_name'] = session_pk
        return response_fun(1, students_list)
