# Generated by Django 4.2.5 on 2023-09-23 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seatingplan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomseatingmodel',
            name='seating_map',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
    ]
