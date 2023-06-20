# Generated by Django 3.2.18 on 2023-04-27 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0001_pre-django-3-upgrade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='export_type',
            field=models.CharField(choices=[('xlsx', 'Excel'), ('csv', 'CSV'), ('zip', 'ZIP'), ('kml', 'kml'), ('csv_zip', 'CSV ZIP'), ('sav_zip', 'SAV ZIP'), ('sav', 'SAV'), ('external', 'Excel'), ('osm', 'osm'), ('gsheets', 'Google Sheets'), ('geojson', 'geojson')], default='xlsx', max_length=10),
        ),
    ]