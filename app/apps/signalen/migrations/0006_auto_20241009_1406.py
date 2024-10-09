# Generated by Django 3.2.19 on 2024-10-09 12:06

import utils.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("signalen", "0005_auto_20240327_1425"),
    ]

    operations = [
        migrations.AlterField(
            model_name="signaal",
            name="aanvullende_vragen",
            field=utils.fields.ListJSONField(default=list),
        ),
        migrations.AlterField(
            model_name="signaal",
            name="signaal_data",
            field=utils.fields.DictJSONField(default=dict),
        ),
    ]