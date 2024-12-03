# Generated by Django 4.2.15 on 2024-12-02 13:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0011_alter_taakopdracht_bericht"),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW dwh_taken_taakopdracht;"),
        migrations.AlterField(
            model_name="taakopdracht",
            name="titel",
            field=models.CharField(max_length=200),
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
