from django.db import models

from auth_app.models import AdminModel


class SessionModel(models.Model):
    user = models.ForeignKey(AdminModel, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related')
    session_name = models.CharField(max_length=32, unique=True)
    branch_data = models.JSONField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adminSession'


