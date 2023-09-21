from django.db import models

from auth_app.models import AdminModel
from collageInfo.models import SectionModel, BranchModel


class StudentModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    section = models.ForeignKey(SectionModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    roll_number = models.PositiveBigIntegerField(null=False, blank=False)
    name = models.CharField(max_length=32, null=False, blank=False)

    class Meta:
        db_table = 'studentDetail'



