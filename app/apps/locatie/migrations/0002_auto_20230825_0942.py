# Generated by Django 3.2.19 on 2023-08-25 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locatie", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="locatie",
            name="buurtnaam",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="locatie",
            name="wijknaam",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]