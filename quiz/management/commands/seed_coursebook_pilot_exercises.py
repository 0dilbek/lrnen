from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from courses.models import Category, Lesson
from quiz.models import Exercise


SOURCE = 'course_book_pilot_v1'


def page(level, number):
    return {
        'url': f'/static/coursebooks/{level}/page-{number:03d}.jpg',
        'page_number': number,
    }


PILOTS = [
    {
        'category': 'Book 1 – Beginner',
        'lesson_order': 15,
        'source_unit': 15,
        'exercises': [
            {
                'type': 'word_order',
                'instruction_kaa': 'Sózlerdi durıs tártipke keltirip, bolımsız gáplerdi dúziń.',
                'instruction_uz': 'So‘zlarni to‘g‘ri tartibga keltirib, inkor gaplarni tuzing.',
                'content': {
                    'pages': [page('level1', 55)],
                    'items': [
                        {'tokens': ['Jack', 'is', 'not', 'a', 'gardener.'], 'answer': 'Jack is not a gardener.'},
                        {'tokens': ['She', 'is', 'not', 'my', 'sister.'], 'answer': 'She is not my sister.'},
                        {'tokens': ['That', 'is', 'not', 'her', 'car.'], 'answer': 'That is not her car.'},
                        {'tokens': ['I', 'am', 'not', '35', 'years', 'old.'], 'answer': 'I am not 35 years old.'},
                        {'tokens': ['We', 'are', 'not', 'Spanish.'], 'answer': 'We are not Spanish.'},
                        {'tokens': ['Chad', 'is', 'not', 'a', 'vet.'], 'answer': 'Chad is not a vet.'},
                    ],
                },
            },
            {
                'type': 'written_answer',
                'instruction_kaa': 'Qátelerdi dúzetip, gáplerdi tolıq qayta jazıń.',
                'instruction_uz': 'Xatolarni tuzatib, gaplarni to‘liq qayta yozing.',
                'content': {
                    'pages': [page('level1', 56)],
                    'questions': [
                        {'prompt': "Louis aren’t Hayley’s uncle.", 'answer': "Louis isn't Hayley's uncle."},
                        {'prompt': "It am not 10 o'clock in the morning.", 'answer': "It is not 10 o'clock in the morning.", 'alternatives': ["It isn't 10 o'clock in the morning."]},
                        {'prompt': "You isn’t 35 years old.", 'answer': "You aren't 35 years old.", 'alternatives': ['You are not 35 years old.']},
                        {'prompt': "I aren’t Australian.", 'answer': "I am not Australian.", 'alternatives': ["I'm not Australian."]},
                        {'prompt': "My brother aren’t married.", 'answer': "My brother isn't married.", 'alternatives': ['My brother is not married.']},
                        {'prompt': "Tom and Angela isn’t construction workers.", 'answer': "Tom and Angela aren't construction workers.", 'alternatives': ['Tom and Angela are not construction workers.']},
                    ],
                },
            },
        ],
    },
    {
        'category': 'Book 2 – Elementary',
        'lesson_order': 36,
        'source_unit': 36,
        'exercises': [
            {
                'type': 'written_answer',
                'instruction_kaa': 'Jaktıń rejesin oqıp, “going to” menen tolıq gáplerdi jazıń.',
                'instruction_uz': 'Jackning rejalarini o‘qib, “going to” bilan to‘liq gaplar yozing.',
                'content': {
                    'pages': [page('level2', 120)],
                    'questions': [
                        {'prompt': 'Tidy my house by the weekend.', 'answer': 'He is going to tidy his house by the weekend.'},
                        {'prompt': 'Paint my bedroom by the end of this month.', 'answer': 'He is going to paint his bedroom by the end of this month.'},
                        {'prompt': 'Join a gym by this time next month.', 'answer': 'He is going to join a gym by this time next month.'},
                        {'prompt': 'Book a vacation by the end of March.', 'answer': 'He is going to book a vacation by the end of March.'},
                        {'prompt': 'Get fit by the summer.', 'answer': 'He is going to get fit by the summer.'},
                        {'prompt': 'Buy a new car by December.', 'answer': 'He is going to buy a new car by December.'},
                    ],
                },
            },
            {
                'type': 'word_order',
                'instruction_kaa': 'Sózlerdi durıs tártipke keltirip, keleshek rejeler haqqında gápler dúziń.',
                'instruction_uz': 'So‘zlarni to‘g‘ri tartibga keltirib, kelajak rejalari haqida gaplar tuzing.',
                'content': {
                    'pages': [page('level2', 121)],
                    'items': [
                        {'tokens': ['Aziz', 'and', 'Julie', 'are', 'going', 'to', 'get', 'married', 'by', 'the', 'end', 'of', 'next', 'year.'], 'answer': 'Aziz and Julie are going to get married by the end of next year.'},
                        {'tokens': ['Tim', 'is', 'going', 'to', 'buy', 'a', 'new', 'boat', 'by', 'October.'], 'answer': 'Tim is going to buy a new boat by October.'},
                        {'tokens': ['Sally', 'and', 'Jane', 'are', 'going', 'to', 'go', 'on', 'vacation', 'on', 'the', 'weekend.'], 'answer': 'Sally and Jane are going to go on vacation on the weekend.'},
                        {'tokens': ['I', 'am', 'going', 'to', 'write', 'a', 'book', 'by', 'this', 'time', 'next', 'year.'], 'answer': 'I am going to write a book by this time next year.'},
                        {'tokens': ['We', 'are', 'going', 'to', 'run', 'a', 'marathon', 'tomorrow.'], 'answer': 'We are going to run a marathon tomorrow.'},
                    ],
                },
            },
        ],
    },
    {
        'category': 'Book 3 – Intermediate',
        'lesson_order': 49,
        'source_unit': 63,
        'exercises': [
            {
                'type': 'written_answer',
                'instruction_kaa': 'Gáplerdi past simple active túrinen passive túrine ózgertip jazıń.',
                'instruction_uz': 'Gaplarni past simple active shaklidan passive shakliga o‘zgartirib yozing.',
                'content': {
                    'pages': [page('level3', 217)],
                    'questions': [
                        {'prompt': 'Someone burned down the building.', 'answer': 'The building was burned down.'},
                        {'prompt': 'Something destroyed the factory.', 'answer': 'The factory was destroyed.'},
                        {'prompt': 'Someone spilled oil into the ocean.', 'answer': 'The oil was spilled into the ocean.'},
                        {'prompt': 'Something polluted the lake.', 'answer': 'The lake was polluted.'},
                        {'prompt': 'Someone hurt the animals.', 'answer': 'The animals were hurt.'},
                        {'prompt': "Something damaged many people's homes.", 'answer': "Many people's homes were damaged."},
                    ],
                },
            },
            {
                'type': 'written_answer',
                'instruction_kaa': 'Maqalanı oqıp, sorawlarǵa tolıq gápler menen juwap beriń.',
                'instruction_uz': 'Maqolani o‘qib, savollarga to‘liq gaplar bilan javob bering.',
                'content': {
                    'pages': [page('level3', 218)],
                    'questions': [
                        {'prompt': 'What happened to the chemicals last night?', 'answer': 'The chemicals were released into the air.'},
                        {'prompt': 'What happened to Lake Bander?', 'answer': 'Lake Bander was turned red by the chemicals.'},
                        {'prompt': 'How did the chemicals get into the lake?', 'answer': "The chemicals were carried into the lake by last night's rain."},
                        {'prompt': 'What happened to thousands of fish?', 'answer': 'Thousands of fish were killed.'},
                        {'prompt': "What happened to local farmers' crops?", 'answer': "Local farmers' crops were destroyed."},
                        {'prompt': 'What happened to the Bander area?', 'answer': 'The Bander area was declared a disaster area.'},
                        {'prompt': "What happened to John Hawkins's business?", 'answer': "John Hawkins's business was ruined.", 'alternatives': ["John Hawkins' business was ruined."]},
                    ],
                },
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Uchta Course Book pilot darsiga xilma-xil, alohida mashqlar qo‘shadi.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--replace', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['replace']:
            deleted, _ = Exercise.objects.filter(source=SOURCE).delete()
            self.stdout.write(f'Oldingi pilot yozuvlari: {deleted} ta o‘chirildi.')

        created = []
        for pilot in PILOTS:
            try:
                category = Category.objects.get(name=pilot['category'])
                lesson = Lesson.objects.get(category=category, order=pilot['lesson_order'])
            except (Category.DoesNotExist, Lesson.DoesNotExist) as error:
                raise CommandError(
                    f"Dars topilmadi: {pilot['category']} / {pilot['lesson_order']}"
                ) from error

            next_order = (lesson.exercises.aggregate(value=Max('order'))['value'] or 0) + 1
            for offset, definition in enumerate(pilot['exercises']):
                instruction_kaa = definition['instruction_kaa']
                exercise = Exercise.objects.create(
                    lesson=lesson,
                    type=definition['type'],
                    instruction=instruction_kaa,
                    instruction_kaa=instruction_kaa,
                    instruction_uz=definition['instruction_uz'],
                    content=definition['content'],
                    order=next_order + offset,
                    source=SOURCE,
                    source_unit=pilot['source_unit'],
                )
                created.append(exercise)

        self.stdout.write(self.style.SUCCESS(
            f'{len(created)} ta mustaqil pilot mashq tayyorlandi: '
            f'{sum(item.type == "word_order" for item in created)} ta word_order, '
            f'{sum(item.type == "written_answer" for item in created)} ta written_answer.'
        ))
        if options['dry_run']:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING('Dry-run: bazaga yozilmadi.'))
