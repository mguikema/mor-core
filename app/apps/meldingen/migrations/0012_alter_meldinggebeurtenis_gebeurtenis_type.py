# Generated by Django 3.2.19 on 2024-02-28 11:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meldingen", "0011_auto_20240227_1006"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meldinggebeurtenis",
            name="gebeurtenis_type",
            field=models.CharField(
                choices=[
                    ("standaard", "Standaard"),
                    ("status_wijziging", "Status wijziging"),
                    ("melding_aangemaakt", "Melding aangemaakt"),
                    ("taakopdracht_aangemaakt", "Taakopdracht aangemaakt"),
                    ("taakopdracht_status_wijziging", "Taakopdracht status wijziging"),
                    ("locatie_aangemaakt", "Locatie aangemaakt"),
                    ("signaal_toegevoegd", "Signaal toegevoegd"),
                    ("urgentie_aangepast", "Urgentie aangepast"),
                    ("melding_heropend", "Melding heropend"),
                ],
                default="standaard",
                max_length=40,
            ),
        ),
    ]