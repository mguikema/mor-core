# Generated by Django 3.2.19 on 2023-06-29 13:48

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notificatie",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "actie",
                    models.CharField(
                        choices=[
                            ("aangemaakt", "Aangemaakt"),
                            ("gewijzigd", "Gewijzigd"),
                            ("verwijderd", "Verwijderd"),
                        ],
                        max_length=100,
                    ),
                ),
                ("additionele_informatie", models.JSONField(default=dict)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificatie",
                "verbose_name_plural": "Notificaties",
                "ordering": ("-aangemaakt_op",),
            },
        ),
    ]
