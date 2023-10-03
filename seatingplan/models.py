from django.db import models

from adminsession.models import SessionModel
from auth_app.models import AdminModel
from collageInfo.models import BranchModel, SectionModel


class RoomSeatingModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    session = models.ForeignKey(SessionModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    room_number = models.CharField(max_length=128)
    room_rows = models.PositiveIntegerField()
    room_columns = models.PositiveIntegerField()
    room_breakout = models.CharField(max_length=128)
    room_type = models.CharField(max_length=128, null=True, blank=True)
    room_remark = models.IntegerField(default=0)
    seating_map = models.JSONField(null=True)
    marked = models.BooleanField(default=False)

    class Meta:
        db_table = 'roomSeatingPlan'


class SeatingPlanModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    session = models.ForeignKey(SessionModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    branch = models.ForeignKey(BranchModel, on_delete=models.SET_NULL, related_name='%(app_label)s_%(class)s_related',
                               null=True)
    section = models.ForeignKey(SectionModel, on_delete=models.SET_NULL, related_name='%(app_label)s_%(class)s_related',
                                null=True)
    student_rn = models.PositiveBigIntegerField()  # student RollNumber
    student_name = models.CharField(max_length=128)
    branch_name = models.CharField(max_length=128)
    section_name = models.CharField(max_length=128)
    room = models.ForeignKey(RoomSeatingModel, on_delete=models.DO_NOTHING, null=True)
    marked = models.BooleanField(default=False)

    class Meta:
        db_table = 'seatingPlan'
