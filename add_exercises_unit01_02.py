import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'englishLMS.settings')
django.setup()

from courses.models import Lesson
from quiz.models import Quiz, Exercise

def get_lesson(unit_num):
    return Lesson.objects.get(title__startswith=f'Unit {unit_num:02d}')

# ============================================================
# UNIT 01 — Talking about yourself
# ============================================================
lesson01 = get_lesson(1)

# 1.1 Cross out the incorrect word (choose_correct)
quiz_data_01 = [
    ("Jack ___ 27 years old.", ["are", "is"], 1),
    ("They ___ the Walker family.", ["are", "is"], 0),
    ("You ___ a police officer.", ["am", "are"], 1),
    ("Eve ___ from Canada.", ["is", "are"], 0),
    ("I ___ a teacher.", ["is", "am"], 1),
    ("We ___ Australian.", ["are", "is"], 0),
    ("He ___ an artist.", ["am", "is"], 1),
]

for q, opts, correct in quiz_data_01:
    Quiz.objects.create(lesson=lesson01, question=q, options=opts, correct_option_index=correct)

# 1.2 Fill in the gaps with "am," "is," or "are"
Exercise.objects.create(
    lesson=lesson01,
    type='fill_blank',
    instruction='Fill in the gaps with "am," "is," or "are"',
    content={
        "items": [
            {"sentence": "We ___ Australian.", "answer": "are"},
            {"sentence": "They ___ doctors.", "answer": "are"},
            {"sentence": "I ___ from Canada.", "answer": "am"},
            {"sentence": "Elizabeth ___ British.", "answer": "is"},
            {"sentence": "You ___ a mechanic.", "answer": "are"},
            {"sentence": "Luke ___ an engineer.", "answer": "is"},
            {"sentence": "She ___ 35 years old.", "answer": "is"},
        ]
    },
    order=1
)

# 1.4 Fill in the gaps to make negative sentences
Exercise.objects.create(
    lesson=lesson01,
    type='fill_blank',
    instruction='Fill in the gaps to make negative sentences',
    content={
        "items": [
            {"sentence": "I ___ from Argentina.", "answer": "am not"},
            {"sentence": "John and Ellie ___ best friends.", "answer": "are not"},
            {"sentence": "Mr. Robbins ___ a teacher.", "answer": "is not"},
            {"sentence": "It ___ 2 o'clock.", "answer": "is not"},
            {"sentence": "You ___ my sister.", "answer": "are not"},
            {"sentence": "Annabelle ___ at school.", "answer": "is not"},
            {"sentence": "Ann and Ravi ___ students.", "answer": "are not"},
            {"sentence": "Ken ___ a mechanic.", "answer": "is not"},
            {"sentence": "We ___ doctors.", "answer": "are not"},
            {"sentence": "He ___ 45 years old.", "answer": "is not"},
            {"sentence": "They ___ my teachers.", "answer": "are not"},
            {"sentence": "She ___ from Ireland.", "answer": "is not"},
            {"sentence": "It ___ Martha's book.", "answer": "is not"},
        ]
    },
    order=2
)

# 1.5 Rewrite each sentence in its negative form
Exercise.objects.create(
    lesson=lesson01,
    type='fill_blank',
    instruction='Rewrite each sentence in its negative form',
    content={
        "items": [
            {"sentence": "Adam is a nurse.", "answer": "Adam is not a nurse."},
            {"sentence": "This is the bank.", "answer": "This is not the bank."},
            {"sentence": "You are a gardener.", "answer": "You are not a gardener."},
            {"sentence": "Selma is a teacher.", "answer": "Selma is not a teacher."},
            {"sentence": "We are from Spain.", "answer": "We are not from Spain."},
            {"sentence": "I am at home.", "answer": "I am not at home."},
            {"sentence": "They are 20 years old.", "answer": "They are not 20 years old."},
        ]
    },
    order=3
)

# 1.6 Say the questions out loud, filling in the gaps
Exercise.objects.create(
    lesson=lesson01,
    type='fill_blank',
    instruction='Fill in the gaps to complete the questions',
    content={
        "items": [
            {"sentence": "___ you from France?", "answer": "Are"},
            {"sentence": "___ they your dogs?", "answer": "Are"},
            {"sentence": "___ Jo your cousin?", "answer": "Is"},
            {"sentence": "___ it 10 o'clock?", "answer": "Is"},
            {"sentence": "___ I in your class?", "answer": "Am"},
            {"sentence": "___ you Canadian?", "answer": "Are"},
            {"sentence": "___ those your keys?", "answer": "Are"},
            {"sentence": "___ Martin at work today?", "answer": "Is"},
            {"sentence": "___ Elena 28 years old?", "answer": "Is"},
            {"sentence": "___ they nurses?", "answer": "Are"},
        ]
    },
    order=4
)

print(f"Unit 01: {Quiz.objects.filter(lesson=lesson01).count()} quizzes, {Exercise.objects.filter(lesson=lesson01).count()} exercises")

# ============================================================
# UNIT 02 — Talking about routines
# ============================================================
lesson02 = get_lesson(2)

# 2.1 Cross out the incorrect word
quiz_data_02 = [
    ("Eddie ___ in Canada.", ["live", "lives"], 1),
    ("They ___ pizza for dinner.", ["cook", "cooks"], 0),
    ("Your friend ___ a microwave.", ["has", "have"], 0),
    ("She ___ at the gym.", ["work", "works"], 1),
    ("I ___ TV every day.", ["watch", "watches"], 0),
    ("We ___ work at 5pm.", ["leaves", "leave"], 1),
    ("Mark ___ a skateboard.", ["has", "have"], 0),
    ("They ___ school at 9am.", ["start", "starts"], 0),
    ("You ___ soccer.", ["hates", "hate"], 1),
    ("Tara ___ breakfast at 7:15am.", ["eat", "eats"], 1),
    ("I ___ to the park after work.", ["go", "goes"], 0),
    ("We ___ up at 7am.", ["wakes", "wake"], 1),
    ("He ___ dinner at 8pm.", ["cook", "cooks"], 1),
    ("My son ___ to school.", ["walks", "walk"], 0),
]

for q, opts, correct in quiz_data_02:
    Quiz.objects.create(lesson=lesson02, question=q, options=opts, correct_option_index=correct)

# 2.2 Fill in the gaps using the words in the panel
Exercise.objects.create(
    lesson=lesson02,
    type='fill_blank',
    instruction='Fill in the gaps using the correct verb',
    content={
        "items": [
            {"sentence": "We ___ in New York.", "answer": "live"},
            {"sentence": "Laura ___ TV all day.", "answer": "watches"},
            {"sentence": "You ___ at 7am.", "answer": "wake up"},
            {"sentence": "I ___ work at 6pm.", "answer": "leave"},
            {"sentence": "My cousins ___ to the gym.", "answer": "go"},
            {"sentence": "She ___ a laptop.", "answer": "has"},
            {"sentence": "James ___ in a bank.", "answer": "works"},
            {"sentence": "They ___ lunch at 1:30pm.", "answer": "eat"},
        ]
    },
    order=1
)

# 2.3 Fill in the gaps with correct verb form
Exercise.objects.create(
    lesson=lesson02,
    type='fill_blank',
    instruction='Fill in the gaps by putting the verb in the correct form',
    content={
        "items": [
            {"sentence": "Omar ___ (work) in an office.", "answer": "works"},
            {"sentence": "They ___ (eat) pizza for lunch.", "answer": "eat"},
            {"sentence": "Mia ___ (get up) late on Saturdays.", "answer": "gets up"},
            {"sentence": "You ___ (go) to work early.", "answer": "go"},
            {"sentence": "We ___ (cook) dinner at 7:30pm.", "answer": "cook"},
            {"sentence": "Paul ___ (finish) work at 6pm.", "answer": "finishes"},
            {"sentence": "Lily ___ (watch) TV every day.", "answer": "watches"},
            {"sentence": "They ___ (start) work at 10am.", "answer": "start"},
            {"sentence": "Robert ___ (have) a car.", "answer": "has"},
            {"sentence": "I ___ (wake up) at 6:45am.", "answer": "wake up"},
            {"sentence": "Jay ___ (study) science every day.", "answer": "studies"},
            {"sentence": "Karen ___ (like) tennis.", "answer": "likes"},
            {"sentence": "He ___ (work) in a school.", "answer": "works"},
            {"sentence": "Jess ___ (go) to bed at 10pm.", "answer": "goes"},
        ]
    },
    order=2
)

# 2.6 Match the beginnings of the sentences to the correct endings
Exercise.objects.create(
    lesson=lesson02,
    type='matching',
    instruction='Match the beginnings of the sentences to the correct endings',
    content={
        "pairs": [
            {"left": "They go to", "right": "the gym after work."},
            {"left": "We eat lunch", "right": "at 1:30 every day."},
            {"left": "Katia wakes up at", "right": "6:30 every morning."},
            {"left": "My parents have", "right": "two cats and a dog."},
            {"left": "Dave watches", "right": "TV in the evening."},
            {"left": "I walk to work", "right": "every day."},
            {"left": "You work in", "right": "an office in town."},
        ]
    },
    order=3
)

print(f"Unit 02: {Quiz.objects.filter(lesson=lesson02).count()} quizzes, {Exercise.objects.filter(lesson=lesson02).count()} exercises")

print("\nDone! Unit 01 va 02 topshiriqlari qo'shildi.")
