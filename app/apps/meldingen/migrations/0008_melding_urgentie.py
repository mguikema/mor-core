# Generated by Django 3.2.19 on 2024-02-19 14:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meldingen", "0007_datawarehouse"),
    ]

    operations = [
        migrations.AddField(
            model_name="melding",
            name="urgentie",
            field=models.FloatField(default=0.2),
        ),
    ]
