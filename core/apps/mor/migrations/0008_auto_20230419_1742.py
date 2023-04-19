# Generated by Django 3.2.18 on 2023-04-19 15:42

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mor", "0007_auto_20230419_1331"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="meldingcontext",
            options={
                "verbose_name": "Melding context",
                "verbose_name_plural": "Melding contexten",
            },
        ),
        migrations.AddField(
            model_name="meldingcontext",
            name="slug",
            field=django_extensions.db.fields.AutoSlugField(
                blank=True, editable=False, populate_from=("naam",), unique=True
            ),
        ),
        migrations.AlterField(
            model_name="meldingcontext",
            name="naam",
            field=models.CharField(default="Context", max_length=100),
            preserve_default=False,
        ),
    ]
