# Generated by Django 3.2.18 on 2023-04-24 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mor", "0011_auto_20230424_1115"),
    ]

    operations = [
        migrations.AddField(
            model_name="melding",
            name="onderwerpen",
            field=models.ManyToManyField(
                blank=True,
                related_name="meldingen_voor_onderwerpen",
                to="mor.OnderwerpAlias",
            ),
        ),
    ]
