# Generated by Django 4.2.5 on 2023-09-30 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seatingplan', '0007_alter_roomseatingmodel_session'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seatingplanmodel',
            name='room_number',
        ),
        migrations.AddField(
            model_name='seatingplanmodel',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='seatingplan.roomseatingmodel'),
        ),
    ]