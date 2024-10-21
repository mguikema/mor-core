# Generated by Django 4.2.15 on 2024-10-20 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0010_auto_20240909_0946"),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW dwh_taken_taakopdracht;"),
        migrations.AlterField(
            model_name="taakopdracht",
            name="bericht",
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
        # dwh_taken_taakopdracht
        migrations.RunSQL(
            """CREATE OR REPLACE VIEW dwh_taken_taakopdracht
                AS SELECT
                    *
                FROM taken_taakopdracht
            ;"""
        ),
        migrations.RunSQL("GRANT SELECT ON TABLE dwh_taken_taakopdracht TO dwh;"),
    ]
