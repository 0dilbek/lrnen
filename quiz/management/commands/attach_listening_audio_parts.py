import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from quiz.models import Exercise


class Command(BaseCommand):
    help = 'Attach existing per-row coursebook audio tracks to listening exercises.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        changed = 0
        attached = 0

        for exercise in Exercise.objects.filter(type='listening').order_by('id'):
            content = dict(exercise.content or {})
            rows = (
                content.get('questions') or content.get('items') or
                content.get('sentences') or content.get('left') or []
            )
            if not rows or not exercise.audio_url:
                continue

            match = re.match(r'^(.*)_1(\.[^.]+)$', exercise.audio_url)
            if not match:
                continue
            prefix, extension = match.groups()
            example_count = content.get('example_count')
            if not isinstance(example_count, int):
                first = rows[0] if rows else None
                example_count = 1 if isinstance(first, dict) and first.get('is_example') else 0
                example_path = Path(settings.BASE_DIR) / f'{prefix}__eg{extension}'.lstrip('/')
                numbered_count = sum(
                    (Path(settings.BASE_DIR) / f'{prefix}_{number}{extension}'.lstrip('/')).is_file()
                    for number in range(1, len(rows) + 1)
                )
                if example_count == 0 and example_path.is_file() and numbered_count == len(rows) - 1:
                    example_count = 1

            urls = []
            for index in range(len(rows)):
                if index < example_count:
                    candidate_url = f'{prefix}__eg{extension}'
                else:
                    track_number = index - example_count + 1
                    candidate_url = f'{prefix}_{track_number}{extension}'
                candidate_path = Path(settings.BASE_DIR) / candidate_url.lstrip('/')
                urls.append(candidate_url if candidate_path.is_file() else '')

            if sum(bool(url) for url in urls) < 2:
                continue
            if content.get('audio_urls') == urls:
                continue
            content['audio_urls'] = urls
            exercise.content = content
            if not dry_run:
                exercise.save(update_fields=['content'])
            changed += 1
            attached += sum(bool(url) for url in urls)
            self.stdout.write(
                f'#{exercise.id}: {sum(bool(url) for url in urls)}/{len(rows)} audio parts'
            )

        if dry_run:
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f'Exercises changed: {changed}; audio parts attached: {attached}; dry_run={dry_run}'
        ))
