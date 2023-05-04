# Generated by Django 3.2.18 on 2023-04-21 16:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meldingen", "0009_alter_meldingcontext_slug"),
        ("locatie", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="locatie",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="locatie",
            name="object_id",
        ),
        migrations.AddField(
            model_name="locatie",
            name="melding",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="locaties_voor_melding",
                to="meldingen.melding",
            ),
            preserve_default=False,
        ),
    ]
