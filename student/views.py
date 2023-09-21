import pandas as pd
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from auth_app.models import AdminModel
from .serializer import StudentModelSerializer


class StudentViewSets(viewsets.ViewSet):
    parser_class = (FileUploadParser,)

    @action(detail=False, methods=['post'])
    def addStudentByExcel(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        if not admin_user:
            return response_fun(0, "User Not Found")

        try:
            sectionId = int(request.data['section_id'])
            branchId = int(request.data['branch_id'])
        except Exception as e:
            return response_fun(0, str(e))

        try:
            branchInstance = admin_user.collageinfo_branchmodel_related.filter(id=branchId)
            if branchInstance.exists():
                branchInstance = branchInstance[0]
            else:
                response_fun(0, "Branch Not Found")

            sectionInstance = branchInstance.collageinfo_sectionmodel_related.filter(id=sectionId)

            if sectionInstance.exists():
                sectionInstance = sectionInstance[0]
            else:
                response_fun(0, "Section Not Found")

            file = request.FILES['file']
        except Exception as e:
            print(e)
            return response_fun(0, "Unprocessable Entity")

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

        serialize = StudentModelSerializer(data=students_data, many=True)
        if serialize.is_valid():
            serialize.save()
            return response_fun(1, "Students Added Successfully")
        else:
            return response_fun(0, serialize.errors)
