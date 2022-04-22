from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Updates the traffic"

    def handle(self, *args, **options):
        pass