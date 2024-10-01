# Generated by Django 3.2.19 on 2024-09-09 07:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0009_auto_20240704_1221"),
    ]

    operations = [
        migrations.AddField(
            model_name="taakgebeurtenis",
            name="afgesloten_op",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="taakgebeurtenis",
            name="verwijderd_op",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="taakopdracht",
            name="verwijderd_op",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="taakstatus",
            name="naam",
            field=models.CharField(default="nieuw", max_length=50),
        ),
    ]
