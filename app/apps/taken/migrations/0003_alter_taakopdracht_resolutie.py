# Generated by Django 3.2.19 on 2023-10-24 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0002_alter_taakopdracht_resolutie"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taakopdracht",
            name="resolutie",
            field=models.CharField(
                blank=True,
                choices=[
                    ("opgelost", "Opgelost"),
                    ("niet_opgelost", "Niet opgelost"),
                    ("geannuleerd", "Geannuleerd"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
