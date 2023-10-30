from django.db import models

from auth_app.models import AdminModel


class SessionModel(models.Model, object):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    session_name = models.CharField(max_length=32)
    branch_data = models.JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    report_link = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'adminSession'
