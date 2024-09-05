from apps.locatie.tasks import update_locatie_zoek_field_task
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Updates the locatie_zoek_field for all Locatie objects"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of objects to process in each batch",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        result = update_locatie_zoek_field_task.delay(batch_size=batch_size)
        self.stdout.write(
            self.style.SUCCESS(
                f"Task has been queued with batch size {batch_size}. Task ID: {result.id}"
            )
        )
