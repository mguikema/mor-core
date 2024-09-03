# Generated by Django 3.2.19 on 2024-07-04 10:21

from django.db import migrations, models


def move_resolutie_to_taakgebeurtenis(apps, schema_editor):
    Taakopdracht = apps.get_model("taken", "Taakopdracht")
    Taakgebeurtenis = apps.get_model("taken", "Taakgebeurtenis")
    for taakopdracht in Taakopdracht.objects.exclude(resolutie__isnull=True):
        taakgebeurtenis = Taakgebeurtenis.objects.filter(
            taakopdracht=taakopdracht, taakstatus__naam="voltooid"
        ).first()
        if taakgebeurtenis:
            taakgebeurtenis.resolutie = taakopdracht.resolutie
            taakgebeurtenis.save()


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0008_taakopdracht_afhandeltijd"),
    ]

    operations = [
        migrations.AddField(
            model_name="taakgebeurtenis",
            name="resolutie",
            field=models.CharField(
                blank=True,
                choices=[
                    ("opgelost", "Opgelost"),
                    ("niet_opgelost", "Niet opgelost"),
                    ("geannuleerd", "Geannuleerd"),
                    ("niet_gevonden", "Niets aangetroffen"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="taakstatus",
            name="naam",
            field=models.CharField(
                choices=[
                    ("nieuw", "Nieuw"),
                    ("toegewezen", "Toegewezen"),
                    ("openstaand", "Openstaand"),
                    ("voltooid", "Voltooid"),
                    ("voltooid_met_feedback", "Voltooid met feedback"),
                ],
                default="nieuw",
                max_length=50,
            ),
        ),
    ]
