# Generated by Django 4.2.5 on 2023-09-17 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
        ('collageInfo', '0004_sectionmodel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='roommodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_related', to='auth_app.adminmodel'),
            preserve_default=False,
        ),
    ]
