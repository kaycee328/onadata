# Generated by Django 4.2.13 on 2024-07-04 11:26

from django.db import migrations, models
import onadata.apps.logger.models.instance


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0019_alter_project_options_and_more"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="instance",
            new_name="logger_inst_deleted_da31a3_idx",
            old_name="logger_inst_deleted_at_da31a3_idx",
        ),
        migrations.RenameIndex(
            model_name="instance",
            new_name="logger_inst_xform_i_504638_idx",
            old_name="logger_instance_id_xform_id_index",
        ),
        migrations.RenameIndex(
            model_name="instancehistory",
            new_name="logger_inst_checksu_05f7bf_idx",
            old_name="logger_inst_hist_checksum_05f7bf_idx",
        ),
        migrations.RenameIndex(
            model_name="instancehistory",
            new_name="logger_inst_uuid_f5ae42_idx",
            old_name="logger_inst_hist_uuid_f5ae42_idx",
        ),
        migrations.AlterField(
            model_name="instance",
            name="date_created",
            field=models.DateTimeField(
                blank=True,
                default=onadata.apps.logger.models.instance.now,
                editable=False,
            ),
        ),
        migrations.AlterField(
            model_name="instance",
            name="date_modified",
            field=models.DateTimeField(
                blank=True,
                default=onadata.apps.logger.models.instance.now,
                editable=False,
            ),
        ),
        migrations.AlterField(
            model_name="instancehistory",
            name="checksum",
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="instancehistory",
            name="uuid",
            field=models.CharField(db_index=True, default="", max_length=249),
        ),
    ]