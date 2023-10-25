# Generated by Django 3.2.19 on 2023-06-29 14:01

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applicaties", "0001_initial"),
        ("meldingen", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Taakopdracht",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("aangemaakt_op", models.DateTimeField(auto_now_add=True)),
                ("aangepast_op", models.DateTimeField(auto_now=True)),
                ("afgesloten_op", models.DateTimeField(blank=True, null=True)),
                ("taaktype", models.CharField(max_length=200)),
                ("titel", models.CharField(max_length=100)),
                ("bericht", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "resolutie",
                    models.CharField(
                        choices=[
                            ("opgelost", "Opgelost"),
                            ("niet_opgelost", "Niet opgelost"),
                        ],
                        default="niet_opgelost",
                        max_length=50,
                    ),
                ),
                ("additionele_informatie", models.JSONField(default=dict)),
                ("taak_url", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "applicatie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="taakopdrachten_voor_applicatie",
                        to="applicaties.applicatie",
                    ),
                ),
                (
                    "melding",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="taakopdrachten_voor_melding",
                        to="meldingen.melding",
                    ),
                ),
            ],
            options={
                "verbose_name": "Taakopdracht",
                "verbose_name_plural": "Taakopdrachten",
                "ordering": ("-aangemaakt_op",),
            },
        ),
        migrations.CreateModel(
            name="Taakstatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("aangemaakt_op", models.DateTimeField(auto_now_add=True)),
                ("aangepast_op", models.DateTimeField(auto_now=True)),
                (
                    "naam",
                    models.CharField(
                        choices=[
                            ("nieuw", "Nieuw"),
                            ("bezig", "Bezig"),
                            ("voltooid", "Voltooid"),
                        ],
                        default="nieuw",
                        max_length=50,
                    ),
                ),
                (
                    "taakopdracht",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="taakstatussen_voor_taakopdracht",
                        to="taken.taakopdracht",
                    ),
                ),
            ],
            options={
                "ordering": ("-aangemaakt_op",),
            },
        ),
        migrations.AddField(
            model_name="taakopdracht",
            name="status",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="taakopdrachten_voor_taakstatus",
                to="taken.taakstatus",
            ),
        ),
        migrations.CreateModel(
            name="Taakgebeurtenis",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("aangemaakt_op", models.DateTimeField(auto_now_add=True)),
                ("aangepast_op", models.DateTimeField(auto_now=True)),
                (
                    "omschrijving_intern",
                    models.CharField(blank=True, max_length=5000, null=True),
                ),
                ("gebruiker", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "taakopdracht",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="taakgebeurtenissen_voor_taakopdracht",
                        to="taken.taakopdracht",
                    ),
                ),
                (
                    "taakstatus",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="taakgebeurtenissen_voor_taakstatus",
                        to="taken.taakstatus",
                    ),
                ),
            ],
            options={
                "verbose_name": "Taakgebeurtenis",
                "verbose_name_plural": "Taakgebeurtenissen",
                "ordering": ("-aangemaakt_op",),
            },
        ),
    ]
