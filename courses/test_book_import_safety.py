import copy
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from courses.models import Category, Lesson, Vocabulary
from quiz.models import Exercise
from quiz.views import ExerciseAssetLibraryView


class BookImportSafetyTests(TestCase):
    def setUp(self):
        self.lesson = Lesson.objects.create(
            title='Protected lesson', category=Category.objects.create(name='Book 2 – Elementary'),
            description_uz='Original brief description', order=1,
        )
        self.definition = {
            'lesson_id': self.lesson.id, 'source_unit': 1,
            'description_uz': 'Yangi nazariy matn: I am ready.',
            'description_kaa': 'Jańa teoriyalıq tekst: I am ready.',
            'vocabulary': [{'word': 'ready', 'translation_uz': 'tayyor', 'translation_kaa': 'tayar'}],
            'exercises': [{
                'source_key': 'l2.course.1.1.safety', 'type': 'choose_correct',
                'instruction_uz': 'Javobni tanlang.', 'instruction_kaa': 'Juwaptı tańlań.',
                'content': {
                    'example_count': 0,
                    'questions': [{'question': 'I ___ ready.', 'options': ['am', 'is'], 'correct': 0}],
                    'provenance': {'level': 2, 'book': 'course', 'unit': 1, 'activity': '1.1', 'pages': [12]},
                },
            }],
        }

    def import_manifests(self, manifests, **kwargs):
        with tempfile.TemporaryDirectory(prefix='book-safety-') as directory:
            paths = []
            for index, manifest in enumerate(manifests):
                path = Path(directory) / f'manifest-{index}.json'
                path.write_text(json.dumps(manifest), encoding='utf-8')
                paths.append(str(path))
            call_command('import_book_enrichment', manifest=paths, stdout=StringIO(), **kwargs)

    def manifest(self):
        return {'level': 2, 'review_status': 'reviewed', 'lessons': [copy.deepcopy(self.definition)]}

    def assert_database_unchanged(self):
        self.assertEqual(Exercise.objects.count(), 0)
        self.assertEqual(Vocabulary.objects.count(), 0)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.description_uz, 'Original brief description')

    def test_failure_in_later_manifest_rolls_back_earlier_manifest(self):
        first = self.manifest()
        second = self.manifest()
        second['review_status'] = 'draft'
        with self.assertRaises(CommandError):
            self.import_manifests([first, second])
        self.assert_database_unchanged()

    def test_duplicate_activity_key_in_manifest_rejects_entire_batch(self):
        manifest = self.manifest()
        manifest['lessons'][0]['exercises'].append(copy.deepcopy(self.definition['exercises'][0]))
        with self.assertRaises(CommandError):
            self.import_manifests([manifest])
        self.assert_database_unchanged()

    def test_unchecked_assets_cannot_be_published(self):
        with self.assertRaises(CommandError):
            self.import_manifests([self.manifest()], skip_asset_check=True)
        self.assert_database_unchanged()

    def test_wrong_book_category_cannot_be_modified(self):
        manifest = self.manifest()
        manifest['level'] = 1
        with self.assertRaises(CommandError):
            self.import_manifests([manifest])
        self.assert_database_unchanged()

    def test_database_unique_activity_key_allows_blank_legacy_keys(self):
        attributes = {
            'lesson': self.lesson, 'type': 'choose_correct', 'instruction': 'Choose',
            'content': {'questions': []}, 'source': 'book_enrichment_v2',
        }
        Exercise.objects.create(**attributes)
        Exercise.objects.create(**attributes)
        Exercise.objects.create(**attributes, source_key='l2.course.1.1')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Exercise.objects.create(**attributes, source_key='l2.course.1.1')
        self.assertEqual(Exercise.objects.count(), 3)

    def test_database_unique_vocabulary_key_allows_blank_legacy_keys(self):
        attributes = {
            'lesson': self.lesson, 'word': 'ready', 'translation': 'tayar',
            'source': 'book_enrichment_v2',
        }
        Vocabulary.objects.create(**attributes)
        Vocabulary.objects.create(**attributes)
        Vocabulary.objects.create(**attributes, source_key='l2.word.ready')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vocabulary.objects.create(**attributes, source_key='l2.word.ready')
        self.assertEqual(Vocabulary.objects.count(), 3)

    def test_audio_library_isolates_identical_track_names_by_level_and_book(self):
        with tempfile.TemporaryDirectory(prefix='audio-namespace-') as directory:
            root = Path(directory)
            for level, book in ((1, 'course'), (1, 'practice'), (2, 'course')):
                path = root / f'static/audio/books/level{level}/{book}/23/23_2_1.mp3'
                path.parent.mkdir(parents=True)
                path.write_bytes(b'ID3 test audio')
            with override_settings(BASE_DIR=root):
                result = ExerciseAssetLibraryView._audio_files('', '23', '1', 'course')
                self.assertEqual(result['count'], 1)
                row = result['results'][0]
                self.assertEqual(row['url'], '/static/audio/books/level1/course/23/23_2_1.mp3')
                self.assertEqual(row['level'], 1)
                self.assertEqual(row['book'], 'course')
                self.assertTrue(row['preview_url'].startswith('/api/media/access/'))

    def test_same_question_with_different_audio_imports_as_two_activities(self):
        manifest = self.manifest()
        first = manifest['lessons'][0]['exercises'][0]
        first['type'] = 'listening'
        first['audio_url'] = '/static/audio/books/level2/course/1/1_1.mp3'
        second = copy.deepcopy(first)
        second['source_key'] = 'l2.course.1.2.safety'
        second['audio_url'] = '/static/audio/books/level2/course/1/1_2.mp3'
        second['content']['provenance']['activity'] = '1.2'
        manifest['lessons'][0]['exercises'].append(second)

        with tempfile.TemporaryDirectory(prefix='audio-activities-') as directory:
            root = Path(directory)
            for row in (first, second):
                path = root / row['audio_url'].lstrip('/')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'ID3 test audio')
            with override_settings(BASE_DIR=root):
                self.import_manifests([manifest])
                self.import_manifests([manifest])

        self.assertEqual(Exercise.objects.count(), 2)
        self.assertEqual(
            set(Exercise.objects.values_list('audio_url', flat=True)),
            {first['audio_url'], second['audio_url']},
        )
