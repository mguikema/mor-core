# Generated by Django 3.2.19 on 2023-06-02 13:06

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aliassen", "0002_auto_20230505_2034"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("meldingen", "0022_auto_20230601_1935"),
        ("applicaties", "0004_taakapplicatie_taaktypes"),
    ]

    operations = [
        migrations.CreateModel(
            name="Applicatie",
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
                ("naam", models.CharField(default="Applicatie", max_length=100)),
                ("basis_url", models.URLField(blank=True, null=True)),
                ("taaktypes", models.JSONField(blank=True, default=list, null=True)),
                (
                    "gebruiker",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="applicaties_voor_gebruiker",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "melding_context",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="applicatie_voor_melding_context",
                        to="meldingen.meldingcontext",
                    ),
                ),
                (
                    "onderwerpen",
                    models.ManyToManyField(
                        blank=True,
                        related_name="applicaties_voor_onderwerpen",
                        to="aliassen.OnderwerpAlias",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
