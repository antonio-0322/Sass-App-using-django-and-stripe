from django.core.management.base import BaseCommand

from apps.user.models import UserResume
from apps.user.services import ResumeParserService


class Command(BaseCommand):
    help = "Parsed user resumes and save the parsed data to the database"

    def handle(self, *args, **options):
        self.stdout.write('Starting resume  data...')
        for r in UserResume.objects.all():
            self.stdout.write(f'Parsing resume: {r.file.name} ...')
            try:
                ResumeParserService(r).save_parsed_data()
            except FileNotFoundError:
                self.stdout.write(f'File not found: {r.file.name}')
        self.stdout.write('done.')

