# Generated by Django 4.2.11 on 2024-05-30 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0016_add_entity_entity_list"),
    ]

    operations = [
        migrations.RunSQL(
            sql="WITH logger_entity_entity_list AS (SELECT logger_entity.id, logger_registrationform.entity_list_id FROM logger_entity INNER JOIN logger_registrationform ON logger_entity.registration_form_id = logger_registrationform.id WHERE logger_entity.entity_list_id IS NULL) UPDATE logger_entity SET entity_list_id = logger_entity_entity_list.entity_list_id FROM logger_entity_entity_list WHERE logger_entity.id = logger_entity_entity_list.id;",
            reverse_sql="UPDATE logger_entity SET entity_list_id = NULL WHERE entity_list_id IS NOT NULL;",
        )
    ]