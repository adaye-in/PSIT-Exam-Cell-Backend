from django.db import models

from adminsession.models import SessionModel
from auth_app.models import AdminModel


class SeatingPlanModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    session = models.ForeignKey(SessionModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    student_rn = models.PositiveBigIntegerField()
    student_name = models.CharField(max_length=32)
    branch_name = models.CharField(max_length=10)
    section_name = models.CharField(max_length=10)
    room_number = models.CharField(max_length=10)
    marked = models.BooleanField(default=False)
    report_link = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'seatingPlan'


class RoomSeatingModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    room_number = models.CharField(max_length=10)
    room_rows = models.PositiveIntegerField()
    room_columns = models.PositiveIntegerField()
    room_breakout = models.CharField(max_length=32)
    seating_map = models.JSONField(null=True)
    marked = models.BooleanField(default=False)

    class Meta:
        db_table = 'roomSeatingPlan'
