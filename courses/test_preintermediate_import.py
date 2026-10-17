from django.test import SimpleTestCase

from courses.management.commands.import_preintermediate_vocabulary import (
    SOURCE_TO_LESSON,
    offline_uzbek_to_kaa,
    parse_entry,
)


class PreIntermediateVocabularyImportTests(SimpleTestCase):
    def test_source_map_covers_all_course_book_units(self):
        self.assertEqual(set(SOURCE_TO_LESSON), set(range(1, 77)))
        self.assertEqual(set(SOURCE_TO_LESSON.values()), set(range(1, 62)))

    def test_regular_and_compact_dash_entries_are_parsed(self):
        self.assertEqual(parse_entry('• sea — dengiz'), ('sea', 'dengiz'))
        self.assertEqual(
            parse_entry("• check out —tekshirib ko'rmoq"),
            ('check out', 'tekshirib ko‘rmoq'),
        )
        self.assertEqual(
            parse_entry('swollen — shishgan'),
            ('swollen', 'shishgan'),
        )

    def test_known_malformed_entry_is_repaired(self):
        self.assertEqual(
            parse_entry('• receive qabul qilmoq, olmoq'),
            ('receive', 'qabul qilmoq, olmoq'),
        )

    def test_offline_karakalpak_translation_uses_reviewed_terms(self):
        self.assertEqual(offline_uzbek_to_kaa('dengiz va qirg‘oq'), 'teńiz hám jaǵa')
        self.assertEqual(offline_uzbek_to_kaa('yordam bermoq'), 'járdem beriw')
