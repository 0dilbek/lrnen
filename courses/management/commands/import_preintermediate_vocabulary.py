"""Import the supplied Pre-Intermediate vocabulary document without network calls.

The DOCX follows the 76-entry Level 3 Course Book contents, while the project
merges standalone vocabulary spreads into 61 teaching lessons. SOURCE_TO_LESSON
is that reviewed semantic mapping.
"""

import re
from collections import defaultdict
from pathlib import Path

import docx
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from courses.management.commands.backfill_localized_content import KAA_WORDS
from courses.models import Category, Lesson, Level, Vocabulary


SOURCE = 'pre_intermediate_vocabulary_docx'
DEFAULT_PATH = Path(settings.BASE_DIR) / 'books' / 'VOCABULARY.docx'

# Source Course Book unit -> the project's consolidated Book 3 lesson order.
SOURCE_TO_LESSON = {
    1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8,
    10: 9, 11: 9, 12: 10, 13: 10, 14: 11, 15: 11, 16: 12,
    17: 13, 18: 14, 19: 15, 20: 15, 21: 16, 22: 16, 23: 17,
    24: 17, 25: 18, 26: 19, 27: 20, 28: 21, 29: 22, 30: 23,
    31: 24, 32: 24, 33: 25, 34: 26, 35: 26, 36: 27, 37: 28,
    38: 29, 39: 29, 40: 30, 41: 31, 42: 31, 43: 32, 44: 33,
    45: 34, 46: 35, 47: 36, 48: 36, 49: 37, 50: 38, 51: 39,
    52: 40, 53: 41, 54: 42, 55: 42, 56: 43, 57: 44, 58: 45,
    59: 46, 60: 47, 61: 47, 62: 48, 63: 49, 64: 50, 65: 51,
    66: 52, 67: 52, 68: 53, 69: 54, 70: 55, 71: 56, 72: 57,
    73: 58, 74: 59, 75: 60, 76: 61,
}

MALFORMED_ENTRIES = {
    "• make things worse battar yomonlashtirmoq, vaziyatni og'irlashtirmoq": (
        'make things worse', "battar yomonlashtirmoq, vaziyatni og'irlashtirmoq"
    ),
    '• receive qabul qilmoq, olmoq': ('receive', 'qabul qilmoq, olmoq'),
    "• fund jamg'arma, fond, mablag' ajratmoq": (
        'fund', "jamg'arma, fond, mablag' ajratmoq"
    ),
}

# Reviewed high-frequency Uzbek -> Qaraqalpaq substitutions. Existing bilingual
# database entries take priority; these rules cover new definitions offline.
KAA_REPLACEMENTS = [
    ('Amerika Qo‘shma Shtatlari', 'Amerika Qurama Shtatları'),
    ('Birlashgan Arab Amirliklari', 'Birlesken Arab Ámirlikleri'),
    ('Janubiy Afrika Respublikasi', 'Qubla Afrika Respublikası'),
    ('elektron pochta manzili', 'elektron pochta mánzili'),
    ('o‘zini yomon his qilmoq', 'ózin jaman seziw'),
    ('qaror qabul qilmoq', 'qarar qabıl etiw'),
    ('e’tibor bermoq', 'itibar beriw'),
    ('amalga oshirmoq', 'ámelge asırıw'),
    ('yordam bermoq', 'járdem beriw'),
    ('javob bermoq', 'juwap beriw'),
    ('savol bermoq', 'soraw beriw'),
    ('taklif qilmoq', 'usınıs etiw'),
    ('tashkil qilmoq', 'shólkemlestiriw'),
    ('davom ettirmoq', 'dawam ettiriw'),
    ('ishlab chiqarish', 'islep shıǵarıw'),
    ('atrof-muhit', 'qorshaǵan ortalıq'),
    ('bo‘sh vaqt', 'bos waqıt'),
    ('ish vaqti', 'jumıs waqıtı'),
    ('dam olish', 'dem alıw'),
    ('o‘z vaqtida', 'óz waqtında'),
    ('shu jumladan', 'sonıń ishinde'),
    ('bundan tashqari', 'bunnan tısqarı'),
    ('bir-biriga', 'bir-birine'),
    ('bir nechta', 'birneshe'),
    ('juda yaxshi', 'júdá jaqsı'),
    ('juda yomon', 'júdá jaman'),
    ('har doim', 'hár dayım'),
    ('hech qachon', 'hesh qashan'),
    ('tez-tez', 'tez-tez'),
    ('vaqti-vaqti bilan', 'waqıt-waqtı menen'),
    ('qila olmoq', 'isley alıw'),
    ('qila olmaslik', 'isley almaw'),
    ('bo‘lishi mumkin', 'bolıwı múmkin'),
    ('ishonch hosil qilmoq', 'isenim payda etiw'),
    ('qilmoq', 'qılıw'), ('bo‘lmoq', 'bolıw'), ('bermoq', 'beriw'),
    ('olmoq', 'alıw'), ('kelmoq', 'keliw'), ('bormoq', 'barıw'),
    ('aytmoq', 'aytıw'), ('gapirmoq', 'sóylew'), ('yozmoq', 'jazıw'),
    ('o‘qimoq', 'oqıw'), ('tinglamoq', 'tıńlaw'), ('ko‘rmoq', 'kóriw'),
    ('ko‘rsatmoq', 'kórsetiw'), ('so‘ramoq', 'soraw'), ('ishlamoq', 'islew'),
    ('boshlamoq', 'baslaw'), ('tugatmoq', 'juwmaqlaw'),
    ('o‘zgartirmoq', 'ózgertiw'), ('qo‘shmoq', 'qosıw'),
    ('chiqmoq', 'shıǵıw'), ('kirmoq', 'kiriw'), ('yurmoq', 'júriw'),
    ('turmoq', 'turıw'), ('o‘tirmoq', 'otırıw'), ('ochmoq', 'ashıw'),
    ('yopmoq', 'jabıw'), ('kiymoq', 'kiyiw'), ('ichmoq', 'ishiw'),
    ('yemoq', 'jew'), ('pishirmoq', 'pisiriw'), ('kutmoq', 'kútiw'),
    ('xohlamoq', 'qálew'), ('o‘ylamoq', 'oylaw'), ('tushunmoq', 'túsiniw'),
    ('eslamoq', 'eslew'), ('unutmoq', 'umıtıw'), ('tanlamoq', 'tańlaw'),
    ('belgilamoq', 'belgilew'), ('saqlamoq', 'saqlaw'),
    ('ishlatmoq', 'isletiw'), ('tayyorlamoq', 'tayarlaw'),
    ('o‘rganmoq', 'úyreniw'), ('o‘rgatmoq', 'úyretiw'),
    ('qidirmoq', 'izlew'), ('topmoq', 'tabıw'), ('uchrashmoq', 'ushırasıw'),
    ('yaxshilamoq', 'jaqsılaw'), ('kamaytirmoq', 'azaytıw'),
    ('oshirmoq', 'arttırıw'), ('to‘lamoq', 'tólew'), ('sotmoq', 'satıw'),
    ('sotib olmoq', 'satıp alıw'), ('yutmoq', 'utıw'),
    ('yo‘qotmoq', 'joǵaltıw'), ('o‘rnatmoq', 'ornatıw'),
    ('tuzatmoq', 'dúzetiw'), ('tozalamoq', 'tazalaw'),
    ('mamlakat', 'mámleket'), ('davlat', 'mámleket'), ('shahar', 'qala'),
    ('shaharcha', 'kishi qala'), ('qishloq', 'awıl'), ('ko‘cha', 'kóshe'),
    ('yo‘l', 'jol'), ('manzil', 'mánzil'), ('bino', 'imarat'),
    ('xona', 'bólme'), ('uy', 'úy'), ('ish', 'jumıs'), ('ishchi', 'jumısshı'),
    ('xodim', 'xızmetker'), ('odam', 'adam'), ('kishi', 'adam'),
    ('bola', 'bala'), ('oila', 'shańaraq'), ('do‘st', 'dos'),
    ('o‘qituvchi', 'oqıtıwshı'), ('o‘quvchi', 'oqıwshı'),
    ('maktab', 'mektep'), ('kitob', 'kitap'), ('so‘z', 'sóz'),
    ('gap', 'gáp'), ('savol', 'soraw'), ('javob', 'juwap'),
    ('til', 'til'), ('vaqt', 'waqıt'), ('kun', 'kún'), ('hafta', 'hápte'),
    ('oy', 'ay'), ('yil', 'jıl'), ('bugun', 'búgin'), ('ertaga', 'erteń'),
    ('kecha', 'keshe'), ('ertalab', 'azanda'), ('kechqurun', 'keshte'),
    ('dengiz', 'teńiz'), ('qirg‘oq', 'jaǵa'), ('sohil', 'jaǵa'),
    ('orol', 'ataw'), ('tog‘', 'taw'), ('o‘rmon', 'toǵay'),
    ('daryo', 'dárya'), ('suv', 'suw'), ('havo', 'hawa'), ('ob-havo', 'hawa rayı'),
    ('ovqat', 'awqat'), ('ichimlik', 'ishimlik'), ('go‘sht', 'gósh'),
    ('meva', 'miywe'), ('sabzavot', 'palız ónimi'), ('non', 'nan'),
    ('kiyim', 'kiyim'), ('bosh', 'bas'), ('ko‘z', 'kóz'), ('quloq', 'qulaq'),
    ('qo‘l', 'qol'), ('oyoq', 'ayaq'), ('yurak', 'júrek'), ('tana', 'dene'),
    ('kasal', 'nawqas'), ('sog‘lom', 'salamat'), ('shifokor', 'shıpaker'),
    ('yaxshi', 'jaqsı'), ('yomon', 'jaman'), ('katta', 'úlken'),
    ('kichik', 'kishi'), ('uzun', 'uzın'), ('qisqa', 'qısqa'),
    ('yangi', 'jańa'), ('eski', 'eski'), ('chiroyli', 'sulıw'),
    ('qiziqarli', 'qızıqlı'), ('muhim', 'áhmiyetli'), ('to‘g‘ri', 'durıs'),
    ('noto‘g‘ri', 'nadurıs'), ('oson', 'ańsat'), ('qiyin', 'qıyın'),
    ('issiq', 'ıssı'), ('sovuq', 'suwıq'), ('tez', 'tez'), ('sekin', 'áste'),
    ('yuqori', 'joqarı'), ('past', 'tómen'), ('yaqin', 'jaqın'), ('uzoq', 'uzaq'),
    ('chap', 'shep'), ('o‘ng', 'oń'), ('oldida', 'aldında'), ('orqasida', 'artında'),
    ('ichida', 'ishinde'), ('tashqarida', 'sırtında'), ('bilan', 'menen'),
    ('uchun', 'ushın'), ('haqida', 'haqqında'), ('orqali', 'arqalı'),
    ('keyin', 'keyin'), ('oldin', 'aldın'), ('hozir', 'házir'),
    ('har', 'hár'), ('barcha', 'barlıq'), ('ba’zan', 'geyde'),
    ('deyarli', 'derlik'), ('faqat', 'tek'), ('yana', 'jáne'),
    ('yoki', 'yamasa'), ('va', 'hám'), ('ammo', 'biraq'), ('lekin', 'biraq'),
    ('chunki', 'sebebi'), ('agar', 'eger'), ('mumkin', 'múmkin'),
]


def normalize_text(value):
    return re.sub(r'\s+', ' ', value.replace('`', '‘').replace("'", '‘')).strip()


def parse_entry(line):
    line = line.strip()
    if line in MALFORMED_ENTRIES:
        return MALFORMED_ENTRIES[line]
    # Unit 43 in the supplied document is the only section whose rows do not
    # have bullet characters, so the bullet is intentionally optional.
    match = re.match(r'^•?\s*(.+?)\s*(?:—|–)\s*(.+?)\s*$', line)
    if not match:
        match = re.match(r'^•?\s*(.+?)\s+-\s+(.+?)\s*$', line)
    if not match:
        return None
    return normalize_text(match.group(1)), normalize_text(match.group(2))


def parse_docx(path):
    document = docx.Document(path)
    units = defaultdict(list)
    current_unit = None
    malformed = []
    for paragraph in document.paragraphs:
        for raw_line in paragraph.text.splitlines():
            line = raw_line.strip()
            unit_match = re.fullmatch(r'Unit\s+(\d+)\s*', line, re.IGNORECASE)
            if unit_match:
                current_unit = int(unit_match.group(1))
                continue
            if not line:
                continue
            entry = parse_entry(line)
            if entry and current_unit:
                units[current_unit].append(entry)
            elif line.startswith('•'):
                malformed.append((current_unit, line))
    return dict(units), malformed


def replace_whole(text, source, target):
    return re.sub(
        rf"(?<![\w‘’']){re.escape(source)}(?![\w‘’'])",
        target,
        text,
        flags=re.IGNORECASE,
    )


def offline_uzbek_to_kaa(value):
    result = normalize_text(value)
    replacements = KAA_REPLACEMENTS + list(KAA_WORDS)
    for source, target in sorted(replacements, key=lambda item: -len(item[0])):
        result = replace_whole(result, source, target)
    return normalize_text(result)


class Command(BaseCommand):
    help = 'VOCABULARY.docx lug‘atini Book 3 B1/Pre-Intermediate darslariga offline import qiladi.'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH))
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument(
            '--replace', action='store_true',
            help='Faqat oldingi pre-intermediate DOCX import yozuvlarini almashtiradi.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options['path']).expanduser().resolve()
        if not path.exists():
            raise CommandError(f'DOCX topilmadi: {path}')

        units, malformed = parse_docx(path)
        if malformed:
            sample = malformed[0][1]
            raise CommandError(f'{len(malformed)} ta lug‘at qatori ajratilmadi. Namuna: {sample}')
        missing = sorted(set(range(1, 77)) - set(units))
        if missing:
            raise CommandError(f'DOCX unitlari yetishmaydi: {missing}')
        raw_count = sum(len(rows) for rows in units.values())
        if raw_count < 3500:
            raise CommandError(f'Juda kam lug‘at qatori topildi: {raw_count}')

        try:
            category = Category.objects.get(name='Book 3 – Intermediate')
        except Category.DoesNotExist as error:
            raise CommandError('Book 3 – Intermediate kategoriyasi topilmadi.') from error
        b1 = Level.objects.get(slug='b1')
        lessons = {
            lesson.order: lesson
            for lesson in Lesson.objects.filter(category=category).prefetch_related('levels')
        }
        missing_lessons = sorted(set(SOURCE_TO_LESSON.values()) - set(lessons))
        if missing_lessons:
            raise CommandError(f'Book 3 darslari yetishmaydi: {missing_lessons}')
        for lesson in lessons.values():
            if not lesson.levels.filter(pk=b1.pk).exists():
                lesson.levels.add(b1)

        if options['replace']:
            deleted, _ = Vocabulary.objects.filter(source=SOURCE).delete()
        else:
            deleted = 0

        memory = {}
        for word, translation in Vocabulary.objects.exclude(translation_kaa='').values_list(
            'word', 'translation_kaa'
        ):
            memory.setdefault(normalize_text(word).casefold(), normalize_text(translation))

        grouped = defaultdict(list)
        duplicate_count = 0
        seen_by_lesson = defaultdict(set)
        for source_unit in sorted(units):
            lesson_order = SOURCE_TO_LESSON[source_unit]
            for word, translation_uz in units[source_unit]:
                key = normalize_text(word).casefold()
                if key in seen_by_lesson[lesson_order]:
                    duplicate_count += 1
                    continue
                seen_by_lesson[lesson_order].add(key)
                grouped[lesson_order].append((source_unit, word, translation_uz))

        created = updated = preserved = memory_count = offline_count = 0
        for lesson_order in sorted(grouped):
            lesson = lessons[lesson_order]
            existing = {
                normalize_text(item.word).casefold(): item
                for item in Vocabulary.objects.filter(lesson=lesson)
            }
            next_order = (Vocabulary.objects.filter(lesson=lesson).aggregate(
                value=Max('order')
            )['value'] or 0) + 1
            for source_unit, word, translation_uz in grouped[lesson_order]:
                key = normalize_text(word).casefold()
                row = existing.get(key)
                translation_kaa = memory.get(key)
                if translation_kaa:
                    memory_count += 1
                else:
                    translation_kaa = offline_uzbek_to_kaa(translation_uz)
                    offline_count += 1

                if row and row.source != SOURCE:
                    preserved += 1
                    continue
                if row:
                    row.word = word
                    row.translation = translation_kaa
                    row.translation_kaa = translation_kaa
                    row.translation_uz = translation_uz
                    row.source_unit = source_unit
                    row.save(update_fields=[
                        'word', 'translation', 'translation_kaa', 'translation_uz', 'source_unit'
                    ])
                    updated += 1
                else:
                    row = Vocabulary.objects.create(
                        lesson=lesson,
                        word=word,
                        translation=translation_kaa,
                        translation_kaa=translation_kaa,
                        translation_uz=translation_uz,
                        order=next_order,
                        source=SOURCE,
                        source_unit=source_unit,
                    )
                    existing[key] = row
                    next_order += 1
                    created += 1

        if options['dry_run']:
            transaction.set_rollback(True)

        action = 'DRY RUN' if options['dry_run'] else 'IMPORT'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: {raw_count} manba qatori; {created} yaratildi, {updated} yangilandi, '
            f'{preserved} mavjud yozuv saqlandi, {duplicate_count} dublikat birlashtirildi, '
            f'{deleted} eski import o‘chirildi. QAA: {memory_count} translation memory, '
            f'{offline_count} offline qoida.'
        ))
