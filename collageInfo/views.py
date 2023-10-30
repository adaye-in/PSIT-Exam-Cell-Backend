from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.JWTMiddleware import JWTAuthentication
from PSITExamCellBackend.utils import response_fun
from .serializer import *


class BranchViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def addBranch(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        data = request.data
        admin_pk = jwt_obj['user_id']

        # Check if the user with the provided user_id exists
        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        branches = data.get('branch_name').split(';')
        duration = data.get('duration_of_course_year')
        branches = [i for i in branches if i != '']
        data_arr = []

        for branch in branches:
            data_arr.append(
                {
                    "branch_name": branch,
                    "duration_of_course_year": duration,
                    'user': admin_user.pk,
                    'created_on': datetime.now()
                }
            )
        # Set the 'user' field with the AdminModel instance
        # data.update({
        #     'user': admin_user.pk,
        #     'created_on': datetime.now()
        # })
        serializer = BranchModelSerializer(data=data_arr, many=True)

        if serializer.is_valid():
            serializer.save()
            return response_fun(1, {"message": "Branch created successfully"})
        else:
            return response_fun(0, {"message": "Invalid data", "errors": serializer.errors})

    @action(detail=False, methods=['post'])
    def getBranches(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        # make sure that related field is in lowercase
        branches = admin_user.collageinfo_branchmodel_related.all()
        serializer = BranchModelSerializerResponse(branches, many=True)
        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def deleteBranch(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        data = request.data['branch_id']
        branchInstance = None
        try:
            branchInstance = BranchModel.objects.get(pk=data)
        except BranchModel.DoesNotExist:
            response_fun(0, "Branch Does Not Exists")

        if not branchInstance:
            return response_fun(0, 'Instance Not Found')

        if branchInstance.user_id == admin_user.pk:
            branchInstance.delete()
        else:
            response_fun(0, "Unauthorised to Delete")
        return response_fun(1, "Branch Deleted Successfully")


class SectionViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def addSection(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        data = request.data
        admin_pk = jwt_obj['user_id']

        # Check if the user with the provided user_id exists
        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
            if admin_user is None:
                return response_fun(0, {"message": "User does not exist."})
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        try:
            branch_instance = BranchModel.objects.get(pk=request.data['branch_id'])
            if branch_instance is None:
                return response_fun(0, {"message": "Branch does not exist."})
        except BranchModel.DoesNotExist:
            return response_fun(0, {"message": "Branch does not exist."})

        sections = data.get('section_name').split(';')
        sections = [i for i in sections if i != '']
        present_yr = data.get('present_year')
        data_arr = []
        for section in sections:
            data_arr.append(
                {
                    "branch": branch_instance.pk,
                    "section_name": section,
                    "present_year": present_yr,
                    'user': admin_user.pk,
                    'created_on': datetime.now()
                }
            )
        # Set the 'user' field with the AdminModel instance
        # data.update({
        #     'user': admin_user.pk,
        #     'created_on': datetime.now(),
        #     'branch': branch_instance.pk
        # })

        serializer = SectionModelSerializer(data=data_arr, many=True)

        if serializer.is_valid():
            serializer.save()
            return response_fun(1, {"message": "Section created successfully"})
        else:
            return response_fun(0, {"message": "Invalid data", "errors": serializer.errors})

    @action(detail=False, methods=['post'])
    def getAllSections(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        if not admin_user:
            return response_fun(0, "User Not Found")

        # make sure that related field is in lowercase
        sections = admin_user.collageinfo_sectionmodel_related.all()
        serializer = SectionModelSerializerResponse(sections, many=True)
        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def deleteSections(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        data = request.data['section_id']
        sectionInstance = None
        try:
            sectionInstance = SectionModel.objects.get(pk=data)
        except SectionModel.DoesNotExist:
            response_fun(0, "Branch Does Not Exists")

        if not sectionInstance:
            return response_fun(0, 'Instance Not Found')

        if sectionInstance.user_id == admin_user.pk:
            sectionInstance.delete()
        else:
            response_fun(0, "Unauthorised to Delete")
        return response_fun(1, "Branch Deleted Successfully")

    @action(detail=False, methods=['post'])
    def getBranchSection(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        if not admin_user:
            return response_fun(0, "User Not Found")

        branchId = request.data['branch_id']
        sectionsOfBranch = admin_user.collageinfo_sectionmodel_related.filter(branch_id=branchId)
        serializer = SectionModelSerializerResponse(sectionsOfBranch, many=True)
        return response_fun(1, serializer.data)


class RoomViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def createRoom(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        if not admin_user:
            return response_fun(0, "User Not Found")

        data = request.data

        room_remark = data.get('room_remark', None)
        if not room_remark:
            room_remark = '0'

        data.update({
            'created_on': datetime.now(),
            'user': admin_user.pk,
            'room_remark': room_remark
        })

        serializer = RoomModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return response_fun(1, {"message": "Room created successfully"})
        else:
            return response_fun(0, {"message": "Invalid data", "errors": serializer.errors})

    @action(detail=False, methods=['post'])
    def getRooms(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        if not admin_user:
            return response_fun(0, "User Not Found")

        rooms = admin_user.collageinfo_roommodel_related.all()
        serializer = RoomModelSerializerResponse(rooms, many=True)
        return response_fun(1, serializer.data)

    @action(detail=False, methods=['post'])
    def deleteRoom(self, request):
        jwt_obj = JWTAuthentication().authenticate(request)
        admin_pk = jwt_obj['user_id']

        try:
            admin_user = AdminModel.objects.get(pk=admin_pk)
        except AdminModel.DoesNotExist:
            return response_fun(0, {"message": "User does not exist."})

        roomId = request.data['room_id']
        roomInstance = admin_user.collageinfo_roommodel_related.filter(id=roomId)

        if not roomInstance:
            return response_fun(0, "No Room Found")

        roomInstance.delete()

        return response_fun(1, "Room Deleted Successfully")
