# Generated by Django 4.2.5 on 2023-11-21 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminsession', '0003_alter_sessionmodel_session_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionmodel',
            name='session_name',
            field=models.CharField(max_length=255),
        ),
    ]