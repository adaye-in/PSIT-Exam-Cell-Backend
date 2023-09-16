from django.db import models


class AdminModel(models.Model):
    """
    Model for storing the UserName and Password of Admin for login
    """
    email_address = models.CharField(max_length=64, null=False, blank=False, unique=True)
    password = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_users'
