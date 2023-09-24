import pandas as pd
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from auth_app.models import AdminModel
from .models import StudentModel
from .serializer import StudentModelSerializer


class StudentViewSets(viewsets.ViewSet):
    parser_class = (FileUploadParser,)

    @staticmethod
    def authenticate_user(request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return None  # Return None to indicate user not found
        return admin_user

    @staticmethod
    def get_section_and_branch(admin_user, branch_id, section_id):
        """
        :param admin_user: Object of Admin Model
        :param branch_id:
        :param section_id:
        :return branch_instance, section_instance, Error
        """
        try:
            branch_instance = admin_user.collageinfo_branchmodel_related.filter(id=branch_id)
            if branch_instance.exists():
                branch_instance = branch_instance[0]
            else:
                return None, None, True

            section_instance = branch_instance.collageinfo_sectionmodel_related.filter(id=section_id)

            if section_instance.exists():
                section_instance = section_instance[0]
            else:
                return None, None, True

            return branch_instance, section_instance, False

        except Exception as e:
            print(e)
            return None, None, True

    @action(detail=False, methods=['post'])
    def addStudentByExcel(self, request):

        admin_user = self.authenticate_user(request)

        if not admin_user:
            return response_fun(0, "User Not Found")

        try:
            sectionId = int(request.data['section_id'])
            branchId = int(request.data['branch_id'])
        except Exception as e:
            return response_fun(0, str(e))

        branchInstance, sectionInstance, Error = self.get_section_and_branch(admin_user, branchId, sectionId)
        if Error:
            response_fun(0, "Branch/Section Not Found")

        if 'file' not in request.FILES:
            return response_fun(0, "File not found")
        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            return response_fun(0, "Only Excel files (.xlsx) are supported")

        try:
            df = pd.read_excel(file)
        except Exception as e:
            print(e)
            return response_fun(0, str(e))

        if df.isnull().values.any():
            return response_fun(0, "Excel file contains missing values (null or NaN).")

        students_data = []
        for index, row in df.iterrows():
            roll_number = row.iloc[0]
            name = row.iloc[1]

            if pd.isna(name) or name == "":
                return response_fun(0, "Excel file contains rows with missing names.")
            student_data = {
                'roll_number': roll_number,
                'name': name,
                'section': sectionInstance.pk,
                'user': admin_user.pk,
                'branch': branchInstance.pk
            }
            students_data.append(student_data)

        serializer = StudentModelSerializer(data=students_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return response_fun(1, "Students Added Successfully")
        else:
            return response_fun(0, serializer.errors)

    @action(detail=False, methods=['post'])
    def createStudent(self, request):
        admin_user = self.authenticate_user(request)
        if not admin_user:
            return response_fun(0, "User Not Found")

        sectionId = request.data.get('section_id', None)
        branchId = request.data.get('branch_id', None)

        if not sectionId or not branchId:
            return response_fun(0, "Section/Branch Id Not Found")

        branchInstance, sectionInstance, Error = self.get_section_and_branch(admin_user, branchId, sectionId)
        if Error:
            response_fun(0, "Branch/Section Not Found")

        roll_number = request.data.get('roll_number', None)
        name = request.data.get('name', None)

        if not (roll_number or name):
            return response_fun(0, "RollNumber or Name not Found")

        student_data = {
            'roll_number': roll_number,
            'name': name,
            'section': sectionInstance.pk,
            'user': admin_user.pk,
            'branch': branchInstance.pk
        }

        serializer = StudentModelSerializer(data=student_data)
        if serializer.is_valid():
            serializer.save()
            return response_fun(1, "Students Added Successfully")
        else:
            return response_fun(0, serializer.errors)

    @action(detail=False, methods=['post'])
    def deleteStudent(self, request):
        admin_user = self.authenticate_user(request)
        if admin_user is None:
            return response_fun(0, "User Not Found")

        studentId = request.data.get('studentId', None)
        if not studentId:
            return response_fun(0, "Student Id Not Found")

        try:
            studentInstance = admin_user.student_studentmodel_related.get(id=studentId)
        except StudentModel.DoesNotExist:
            return response_fun(0, "Student Not Found")

        studentInstance.delete()
        return response_fun(1, "Student Deleted Successfully")
