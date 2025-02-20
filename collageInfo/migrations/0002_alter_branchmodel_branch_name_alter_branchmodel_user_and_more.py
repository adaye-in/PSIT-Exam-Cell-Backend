# Generated by Django 4.2.5 on 2023-09-17 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
        ('collageInfo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branchmodel',
            name='branch_name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='branchmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_related', to='auth_app.adminmodel'),
        ),
        migrations.AlterField(
            model_name='sectionmodel',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_related', to='collageInfo.branchmodel'),
        ),
        migrations.AlterField(
            model_name='sectionmodel',
            name='section_name',
            field=models.CharField(max_length=32),
        ),
    ]
