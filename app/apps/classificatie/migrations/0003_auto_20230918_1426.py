# Generated by Django 3.2.19 on 2023-09-18 12:26

import django_extensions.db.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("classificatie", "0002_auto_20230825_0957"),
    ]

    operations = [
        migrations.AlterField(
            model_name="onderwerp",
            name="slug",
            field=django_extensions.db.fields.AutoSlugField(
                blank=True, editable=False, populate_from=("name",)
            ),
        ),
        migrations.AlterField(
            model_name="onderwerpgroep",
            name="slug",
            field=django_extensions.db.fields.AutoSlugField(
                blank=True, editable=False, populate_from=("name",)
            ),
        ),
    ]
