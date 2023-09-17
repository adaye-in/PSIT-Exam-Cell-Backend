from django.db import models

from auth_app.models import AdminModel


class BranchModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    branch_name = models.CharField(max_length=32)
    duration_of_course_year = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collageBranches'


class SectionModel(models.Model):
    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    section_name = models.CharField(max_length=32)
    present_year = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collageSections'


class RoomModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    room_number = models.CharField(max_length=10)
    room_rows = models.PositiveIntegerField()
    room_columns = models.PositiveIntegerField()
    room_breakout = models.CharField(max_length=32)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collageRooms'
