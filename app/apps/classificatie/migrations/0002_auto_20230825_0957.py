# Generated by Django 3.2.19 on 2023-08-25 07:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("classificatie", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="onderwerp",
            old_name="naam",
            new_name="name",
        ),
        migrations.RenameField(
            model_name="onderwerpgroep",
            old_name="naam",
            new_name="name",
        ),
    ]
