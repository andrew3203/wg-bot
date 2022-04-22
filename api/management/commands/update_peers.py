from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Update peers list"

    def handle(self, *args, **options):
        pass