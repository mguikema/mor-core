# Generated by Django 3.2.18 on 2023-03-14 13:58

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Onderwerp",
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
                ("naam", models.CharField(max_length=100)),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True, editable=False, populate_from=("naam",)
                    ),
                ),
            ],
            options={
                "verbose_name": "Onderwerp",
                "verbose_name_plural": "Onderwerpen",
            },
        ),
    ]
