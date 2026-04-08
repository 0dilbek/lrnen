"""
DK English for Everyone Level 2 — Unit 01-04+09 exercises + vocabulary seed command.
Usage: python manage.py seed_book
"""
from django.core.management.base import BaseCommand
from courses.models import Category, Lesson, Vocabulary
from quiz.models import Exercise


DATA = {
    "categories": [
        {"id": 1, "name": "Present Simple",      "description": "Using 'to be' and present simple tense"},
        {"id": 2, "name": "Present Continuous",   "description": "Talking about ongoing actions"},
        {"id": 3, "name": "Feelings & Emotions",  "description": "Expressing emotions and feelings"},
    ],
    "lessons": [
        {
            "id": 1,
            "title": "Unit 01 – Talking about yourself",
            "description": "Learn to use 'to be' (am/is/are) to talk about yourself, your family and job.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": 1,
            "order": 1,
        },
        {
            "id": 2,
            "title": "Unit 02 – Talking about routines",
            "description": "Use present simple to describe daily routines, pastimes and possessions.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": 1,
            "order": 2,
        },
        {
            "id": 3,
            "title": "Unit 03 – Today I'm wearing…",
            "description": "Use present continuous to describe what is happening right now.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": 2,
            "order": 1,
        },
        {
            "id": 4,
            "title": "Unit 04 – What's happening?",
            "description": "Ask questions using present continuous.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": 2,
            "order": 2,
        },
        {
            "id": 5,
            "title": "Unit 09 – Routines and exceptions",
            "description": "Contrast present simple (routines) with present continuous (exceptions).",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": 2,
            "order": 3,
        },
    ],
    "vocabulary": [
        # ──────────────────────────────────────────────
        # UNIT 01 — Talking about yourself (professions, nationalities, to be)
        # ──────────────────────────────────────────────
        {"lesson_id": 1, "order": 1,  "word": "teacher",        "translation": "o'qituvchi",      "example": "She is a teacher at the local school."},
        {"lesson_id": 1, "order": 2,  "word": "doctor",         "translation": "shifokor",         "example": "My father is a doctor."},
        {"lesson_id": 1, "order": 3,  "word": "engineer",       "translation": "muhandis",         "example": "Luke is an engineer."},
        {"lesson_id": 1, "order": 4,  "word": "artist",         "translation": "rassom / san'atkor","example": "He is an artist."},
        {"lesson_id": 1, "order": 5,  "word": "mechanic",       "translation": "mexanik / usta",   "example": "You are a mechanic."},
        {"lesson_id": 1, "order": 6,  "word": "police officer", "translation": "politsiyachi",     "example": "You are a police officer."},
        {"lesson_id": 1, "order": 7,  "word": "Australian",     "translation": "avstraliyalik",    "example": "We are Australian."},
        {"lesson_id": 1, "order": 8,  "word": "British",        "translation": "britaniyalik",     "example": "Elizabeth is British."},
        {"lesson_id": 1, "order": 9,  "word": "Canadian",       "translation": "kanadalik",        "example": "Eve is from Canada."},
        {"lesson_id": 1, "order": 10, "word": "family",         "translation": "oila",             "example": "They are the Walker family."},
        {"lesson_id": 1, "order": 11, "word": "years old",      "translation": "yoshda",           "example": "Jack is 27 years old."},
        {"lesson_id": 1, "order": 12, "word": "introduce",      "translation": "tanishtirmoq",     "example": "Let me introduce myself."},

        # ──────────────────────────────────────────────
        # UNIT 02 — Daily routines (present simple verbs)
        # ──────────────────────────────────────────────
        {"lesson_id": 2, "order": 1,  "word": "wake up",        "translation": "uyg'onmoq",        "example": "I wake up at 6:45 am."},
        {"lesson_id": 2, "order": 2,  "word": "get up",         "translation": "o'rnidan turmoq",  "example": "Mia gets up late on Saturdays."},
        {"lesson_id": 2, "order": 3,  "word": "go to work",     "translation": "ishga bormoq",     "example": "You go to work early."},
        {"lesson_id": 2, "order": 4,  "word": "leave",          "translation": "ketmoq / chiqib ketmoq","example": "I leave work at 6pm."},
        {"lesson_id": 2, "order": 5,  "word": "finish",         "translation": "tugatmoq",         "example": "Paul finishes work at 6pm."},
        {"lesson_id": 2, "order": 6,  "word": "cook",           "translation": "pishirmoq",        "example": "We cook dinner at 7:30pm."},
        {"lesson_id": 2, "order": 7,  "word": "study",          "translation": "o'qimoq / o'rganmoq","example": "Jay studies science every day."},
        {"lesson_id": 2, "order": 8,  "word": "routine",        "translation": "kundalik tartib",  "example": "Tell me about your daily routine."},
        {"lesson_id": 2, "order": 9,  "word": "gym",            "translation": "sport zal",        "example": "She works at the gym."},
        {"lesson_id": 2, "order": 10, "word": "skateboard",     "translation": "skeytbord",        "example": "Mark has a skateboard."},
        {"lesson_id": 2, "order": 11, "word": "microwave",      "translation": "mikroto'lqinli pech","example": "Your friend has a microwave."},
        {"lesson_id": 2, "order": 12, "word": "breakfast",      "translation": "nonushta",         "example": "Tara eats breakfast at 7:15am."},

        # ──────────────────────────────────────────────
        # UNIT 03 — Today I'm wearing… (clothes, present continuous)
        # ──────────────────────────────────────────────
        {"lesson_id": 3, "order": 1,  "word": "wear",           "translation": "kiymoq",           "example": "She is wearing a bright red dress."},
        {"lesson_id": 3, "order": 2,  "word": "dress",          "translation": "ko'ylak / libos",  "example": "Julie doesn't usually wear dresses."},
        {"lesson_id": 3, "order": 3,  "word": "suit",           "translation": "kostyum",          "example": "Peter and Frank are wearing suits."},
        {"lesson_id": 3, "order": 4,  "word": "sweater",        "translation": "sviter",           "example": "Roberta is wearing a sweater."},
        {"lesson_id": 3, "order": 5,  "word": "pants",          "translation": "shim",             "example": "You usually wear pants."},
        {"lesson_id": 3, "order": 6,  "word": "skirt",          "translation": "yubka",            "example": "But today you're wearing a skirt."},
        {"lesson_id": 3, "order": 7,  "word": "casual",         "translation": "oddiy (kiyim)",    "example": "Ravi usually wears casual clothes."},
        {"lesson_id": 3, "order": 8,  "word": "painting",       "translation": "bo'yamoq / rasm chizmoq","example": "James is painting the kitchen."},
        {"lesson_id": 3, "order": 9,  "word": "traveling",      "translation": "sayohat qilmoq",   "example": "We are traveling around China."},
        {"lesson_id": 3, "order": 10, "word": "newspaper",      "translation": "gazeta",           "example": "Doug is reading a newspaper."},
        {"lesson_id": 3, "order": 11, "word": "currently",      "translation": "hozirda / ayni paytda","example": "I am currently working from home."},
        {"lesson_id": 3, "order": 12, "word": "instead",        "translation": "o'rniga",          "example": "Today she's watching a movie instead."},

        # ──────────────────────────────────────────────
        # UNIT 04 — What's happening? (question words, activities)
        # ──────────────────────────────────────────────
        {"lesson_id": 4, "order": 1,  "word": "briefcase",      "translation": "portfel",          "example": "Jack is carrying a briefcase."},
        {"lesson_id": 4, "order": 2,  "word": "tie",            "translation": "galstuk",          "example": "Lenny is wearing a tie today."},
        {"lesson_id": 4, "order": 3,  "word": "driving",        "translation": "haydamoq",         "example": "Sarah is driving home."},
        {"lesson_id": 4, "order": 4,  "word": "running",        "translation": "yugurishmoq",      "example": "Frank is running in the park."},
        {"lesson_id": 4, "order": 5,  "word": "carrying",       "translation": "ko'tarmoq / olib yurmoq","example": "Jack is carrying a heavy bag."},
        {"lesson_id": 4, "order": 6,  "word": "shouting",       "translation": "qichqirmoq",       "example": "Why is she shouting?"},
        {"lesson_id": 4, "order": 7,  "word": "library",        "translation": "kutubxona",        "example": "Where are you going? To the library."},
        {"lesson_id": 4, "order": 8,  "word": "sandwich",       "translation": "sendvich",         "example": "What are you eating? A sandwich."},
        {"lesson_id": 4, "order": 9,  "word": "nut and bolt",   "translation": "gayka va bolt",    "example": "He is wearing a nut and bolt."},
        {"lesson_id": 4, "order": 10, "word": "question",       "translation": "savol",            "example": "Ask a question using 'what', 'where', 'who'."},
        {"lesson_id": 4, "order": 11, "word": "answer",         "translation": "javob",            "example": "Give a short answer."},
        {"lesson_id": 4, "order": 12, "word": "at the moment",  "translation": "hozir / ayni damda","example": "What are you doing at the moment?"},

        # ──────────────────────────────────────────────
        # UNIT 09 — Routines and exceptions
        # ──────────────────────────────────────────────
        {"lesson_id": 5, "order": 1,  "word": "usually",        "translation": "odatda / ko'pincha","example": "I usually wake up at 7am."},
        {"lesson_id": 5, "order": 2,  "word": "often",          "translation": "tez-tez / ko'pincha","example": "Tony often goes for a swim."},
        {"lesson_id": 5, "order": 3,  "word": "normally",       "translation": "odatda / normada", "example": "He normally goes on vacation to Peru."},
        {"lesson_id": 5, "order": 4,  "word": "exception",      "translation": "istisno",          "example": "Today is an exception to my routine."},
        {"lesson_id": 5, "order": 5,  "word": "vacation",       "translation": "ta'til / sayohat", "example": "He normally goes on vacation to Peru."},
        {"lesson_id": 5, "order": 6,  "word": "contrast",       "translation": "farq / ziddiyat",  "example": "We use 'but' to show contrast."},
        {"lesson_id": 5, "order": 7,  "word": "cereal",         "translation": "don mahsuloti (nonushta)","example": "Tim usually has cereal for breakfast."},
        {"lesson_id": 5, "order": 8,  "word": "rest",           "translation": "dam olmoq",        "example": "But today she is resting."},
        {"lesson_id": 5, "order": 9,  "word": "shopping",       "translation": "xarid qilmoq",     "example": "But today they are shopping."},
        {"lesson_id": 5, "order": 10, "word": "at home",        "translation": "uyda",             "example": "But today Doug is cooking at home."},
        {"lesson_id": 5, "order": 11, "word": "this week",      "translation": "shu hafta",        "example": "This week I'm working late every day."},
        {"lesson_id": 5, "order": 12, "word": "habit",          "translation": "odat",             "example": "Going to the gym is a good habit."},
    ],
    "exercises": [
        # ──────────────────────────────────────────────
        # UNIT 01 — Talking about yourself
        # ──────────────────────────────────────────────
        {
            "lesson_id": 1,
            "type": "choose_correct",
            "instruction": "To'g'ri so'zni tanlang (Cross out the incorrect word)",
            "order": 1,
            "content": {
                "sentences": [
                    {"before": "Jack ",            "options": ["are", "is"],  "after": " 27 years old.",        "correct": 1},
                    {"before": "They ",            "options": ["are", "is"],  "after": " the Walker family.",   "correct": 0},
                    {"before": "You ",             "options": ["am", "are"],  "after": " a police officer.",    "correct": 1},
                    {"before": "Eve ",             "options": ["is", "are"],  "after": " from Canada.",         "correct": 0},
                    {"before": "I ",               "options": ["is", "am"],   "after": " a teacher.",           "correct": 1},
                    {"before": "We ",              "options": ["are", "is"],  "after": " Australian.",          "correct": 0},
                    {"before": "He ",              "options": ["am", "is"],   "after": " an artist.",           "correct": 1},
                ]
            },
        },
        {
            "lesson_id": 1,
            "type": "fill_blank",
            "instruction": "Bo'sh joylarni 'am', 'is' yoki 'are' bilan to'ldiring",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "We ___ Australian.",        "answer": "are"},
                    {"text": "They ___ doctors.",         "answer": "are"},
                    {"text": "I ___ from Canada.",        "answer": "am"},
                    {"text": "Elizabeth ___ British.",    "answer": "is"},
                    {"text": "You ___ a mechanic.",       "answer": "are"},
                    {"text": "Luke ___ an engineer.",     "answer": "is"},
                    {"text": "She ___ 35 years old.",     "answer": "is"},
                ],
                "word_panel": ["am", "is", "are"],
            },
        },
        {
            "lesson_id": 1,
            "type": "fill_blank",
            "instruction": "Salbiy shaklda bo'sh joylarni to'ldiring (Make negative sentences)",
            "order": 3,
            "content": {
                "sentences": [
                    {"text": "I ___ from Argentina.",          "answer": "am not"},
                    {"text": "John and Ellie ___ best friends.","answer": "are not"},
                    {"text": "Mr. Robbins ___ a teacher.",     "answer": "is not"},
                    {"text": "You ___ my sister.",             "answer": "are not"},
                    {"text": "Annabelle ___ at school.",       "answer": "is not"},
                    {"text": "Ann and Rae ___ students.",      "answer": "are not"},
                    {"text": "Ken ___ a mechanic.",            "answer": "is not"},
                    {"text": "We ___ doctors.",               "answer": "are not"},
                ],
                "word_panel": ["am not", "is not", "are not"],
            },
        },

        # ──────────────────────────────────────────────
        # UNIT 02 — Talking about routines
        # ──────────────────────────────────────────────
        {
            "lesson_id": 2,
            "type": "choose_correct",
            "instruction": "To'g'ri fe'l shaklini tanlang",
            "order": 1,
            "content": {
                "sentences": [
                    {"before": "Eddie ",       "options": ["live", "lives"],       "after": " in Canada.",             "correct": 1},
                    {"before": "They ",        "options": ["cook", "cooks"],       "after": " pizza for dinner.",      "correct": 0},
                    {"before": "Your friend ", "options": ["has", "have"],         "after": " a microwave.",           "correct": 0},
                    {"before": "She ",         "options": ["work", "works"],       "after": " at the gym.",            "correct": 1},
                    {"before": "I ",           "options": ["watch", "watches"],    "after": " TV every day.",          "correct": 0},
                    {"before": "We ",          "options": ["leaves", "leave"],     "after": " work at 5pm.",           "correct": 1},
                    {"before": "Mark ",        "options": ["has", "have"],         "after": " a skateboard.",          "correct": 0},
                    {"before": "They ",        "options": ["start", "starts"],     "after": " school at 9am.",         "correct": 0},
                    {"before": "You ",         "options": ["hates", "hate"],       "after": " soccer.",                "correct": 1},
                    {"before": "Tara ",        "options": ["eat", "eats"],         "after": " breakfast at 7:15am.",   "correct": 1},
                    {"before": "I ",           "options": ["go", "goes"],          "after": " to the park after work.","correct": 0},
                    {"before": "We ",          "options": ["wakes up", "wake up"], "after": " at 7am.",                "correct": 1},
                    {"before": "He ",          "options": ["cook", "cooks"],       "after": " dinner at 8pm.",         "correct": 1},
                    {"before": "My son ",      "options": ["walks", "walk"],       "after": " to school.",             "correct": 0},
                ]
            },
        },
        {
            "lesson_id": 2,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri so'zni tanlang va bo'sh joyni to'ldiring",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "We ___ in New York.",          "answer": "live"},
                    {"text": "Laura ___ TV all day.",         "answer": "watches"},
                    {"text": "You ___ at 7am.",              "answer": "wake up"},
                    {"text": "I ___ work at 6pm.",           "answer": "leave"},
                    {"text": "My cousins ___ to the gym.",   "answer": "go"},
                    {"text": "She ___ a laptop.",            "answer": "has"},
                    {"text": "James ___ in a bank.",         "answer": "works"},
                    {"text": "They ___ lunch at 1:30pm.",    "answer": "eat"},
                ],
                "word_panel": ["has", "live", "go", "wake up", "watches", "leave", "eat", "works"],
            },
        },
        {
            "lesson_id": 2,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi fe'lni to'g'ri shaklga soling",
            "order": 3,
            "content": {
                "sentences": [
                    {"text": "Omar ___ (work) in an office.",          "answer": "works"},
                    {"text": "They ___ (start) work at 10am.",         "answer": "start"},
                    {"text": "Robert ___ (have) a car.",               "answer": "has"},
                    {"text": "I ___ (wake up) at 6:45am.",             "answer": "wake up"},
                    {"text": "Jay ___ (study) science every day.",     "answer": "studies"},
                    {"text": "Karen ___ (like) tennis.",               "answer": "likes"},
                    {"text": "He ___ (work) in a school.",             "answer": "works"},
                    {"text": "Jess ___ (go) to bed at 10pm.",          "answer": "goes"},
                    {"text": "Mia ___ (get up) late on Saturdays.",    "answer": "gets up"},
                    {"text": "You ___ (go) to work early.",            "answer": "go"},
                    {"text": "We ___ (cook) dinner at 7:30pm.",        "answer": "cook"},
                    {"text": "Paul ___ (finish) work at 6pm.",         "answer": "finishes"},
                    {"text": "Lily ___ (watch) TV every day.",         "answer": "watches"},
                ],
            },
        },

        # ──────────────────────────────────────────────
        # UNIT 03 — Today I'm wearing…
        # ──────────────────────────────────────────────
        {
            "lesson_id": 3,
            "type": "choose_correct",
            "instruction": "To'g'ri so'zni tanlang: 'is' yoki 'are'",
            "order": 1,
            "content": {
                "sentences": [
                    {"before": "Sandra ",          "options": ["is", "are"], "after": " having her dinner.",                "correct": 0},
                    {"before": "Glen ",            "options": ["is", "are"], "after": " cleaning his car.",                 "correct": 0},
                    {"before": "April ",           "options": ["is", "are"], "after": " watching a film.",                  "correct": 0},
                    {"before": "Peter and Frank ", "options": ["is", "are"], "after": " wearing suits.",                    "correct": 1},
                    {"before": "James ",           "options": ["is", "are"], "after": " painting the kitchen.",             "correct": 0},
                    {"before": "We ",              "options": ["is", "are"], "after": " traveling around China.",           "correct": 1},
                    {"before": "You ",             "options": ["is", "are"], "after": " listening to an interesting song.", "correct": 1},
                    {"before": "Doug ",            "options": ["is", "are"], "after": " reading a newspaper.",              "correct": 0},
                ]
            },
        },
        {
            "lesson_id": 3,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi fe'lni Present Continuous shaklida yozing",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "Mario ___ (walk) his dog in the park.",    "answer": "is walking"},
                    {"text": "Anne ___ (wait) for her brother.",         "answer": "is waiting"},
                    {"text": "Pedro ___ (cook) pizza for dinner.",       "answer": "is cooking"},
                    {"text": "Mike ___ (mow) the lawn.",                 "answer": "is mowing"},
                    {"text": "Cynthia ___ (lie) on the sofa.",          "answer": "is lying"},
                    {"text": "Jane ___ (go) to the theater.",            "answer": "is going"},
                    {"text": "I ___ (work) at the moment.",             "answer": "am working"},
                    {"text": "Colin ___ (listen) to some music.",        "answer": "is listening"},
                    {"text": "Our children ___ (play) in a band.",       "answer": "are playing"},
                    {"text": "We ___ (drink) lemonade.",                "answer": "are drinking"},
                    {"text": "Stefan ___ (come) to our party.",          "answer": "is coming"},
                    {"text": "They ___ (eat) pasta for dinner.",         "answer": "are eating"},
                    {"text": "Roberta ___ (wear) a sweater.",            "answer": "is wearing"},
                    {"text": "You ___ (play) tennis with John.",         "answer": "are playing"},
                ],
            },
        },
        {
            "lesson_id": 3,
            "type": "matching",
            "instruction": "Gaplarning davomlarini toping va ulang",
            "order": 3,
            "content": {
                "left": [
                    "Julie doesn't usually wear dresses,",
                    "Paula doesn't often watch TV,",
                    "Sven usually cooks at home,",
                    "I often go to bed at 11pm,",
                    "Janet is working at home today,",
                    "Ravi usually wears casual clothes,",
                    "Tim usually has cereal for breakfast,",
                    "We usually go on vacation to Greece,",
                    "I almost always drive to work,",
                    "Nelson is drinking wine today,",
                    "You usually wear pants,",
                ],
                "right": [
                    "but tonight she's watching a good movie.",
                    "but this evening I'm going to bed early.",
                    "but today he's eating at a restaurant.",
                    "but today she's wearing a bright red dress.",
                    "but today you're wearing a skirt.",
                    "but he normally drinks beer.",
                    "but today I'm walking as my car won't start.",
                    "but this morning he's having eggs.",
                    "but this year we're visiting Italy.",
                    "but today he's wearing a business suit.",
                    "but she usually works in an office.",
                ],
                "pairs": [3, 0, 2, 1, 10, 9, 7, 8, 6, 5, 4],
            },
        },

        # ──────────────────────────────────────────────
        # UNIT 04 — What's happening?
        # ──────────────────────────────────────────────
        {
            "lesson_id": 4,
            "type": "matching",
            "instruction": "Savollarga mos javoblarni toping",
            "order": 1,
            "content": {
                "left": [
                    "What are you eating?",
                    "What is he reading?",
                    "Where are you going?",
                    "Who is talking?",
                    "Why is she shouting?",
                    "What is he wearing?",
                    "What are the children doing?",
                ],
                "right": [
                    "She's angry.",
                    "Computer games.",
                    "A book.",
                    "A sandwich.",
                    "A nut and bolt.",
                    "To the library.",
                    "Sue and Johnny.",
                ],
                "pairs": [3, 2, 5, 6, 0, 4, 1],
            },
        },
        {
            "lesson_id": 4,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri so'zni tanlang",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "Jack is ___ a briefcase.",      "answer": "carrying"},
                    {"text": "Lenny is ___ a tie today.",     "answer": "wearing"},
                    {"text": "Sarah is ___ home.",            "answer": "driving"},
                    {"text": "Frank is ___ in the park.",     "answer": "running"},
                    {"text": "Jane is ___ the dog.",          "answer": "walking"},
                    {"text": "Simon is ___ to music.",        "answer": "listening"},
                    {"text": "Pat is ___ to work.",           "answer": "walking"},
                    {"text": "Gavin is ___ breakfast.",       "answer": "eating"},
                ],
                "word_panel": ["carrying", "listening", "walking", "eating", "wearing", "driving", "running", "cooking"],
            },
        },

        # ──────────────────────────────────────────────
        # UNIT 09 — Routines and exceptions
        # ──────────────────────────────────────────────
        {
            "lesson_id": 5,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi fe'lni to'g'ri zamon shaklida yozing (Present Simple)",
            "order": 1,
            "content": {
                "sentences": [
                    {"text": "Doug usually ___ (order) a pizza on Fridays.",          "answer": "orders"},
                    {"text": "Tony often ___ (go) for a swim in the evening.",        "answer": "goes"},
                    {"text": "Today Baz ___ (have) eggs for breakfast.",              "answer": "has"},
                    {"text": "John's sister usually ___ (drive) to work.",            "answer": "drives"},
                    {"text": "Clara usually ___ (sleep) in the afternoon.",           "answer": "sleeps"},
                    {"text": "My cousins often ___ (play) soccer together.",          "answer": "play"},
                    {"text": "He normally ___ (go) on vacation to Peru.",             "answer": "goes"},
                    {"text": "Jenny usually ___ (watch) TV in the evening.",          "answer": "watches"},
                    {"text": "Abe often ___ (play) soccer on Fridays.",               "answer": "plays"},
                    {"text": "Tonight our dog ___ (sleep) in the kitchen.",           "answer": "sleeps"},
                    {"text": "Liza usually ___ (go) to the gym after work.",          "answer": "goes"},
                    {"text": "They often ___ (go) running on Saturdays.",             "answer": "go"},
                ],
            },
        },
        {
            "lesson_id": 5,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi fe'lni Present Continuous shaklida yozing (exceptions)",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "But today Doug ___ (cook) at home.",                    "answer": "is cooking"},
                    {"text": "But today he ___ (visit) a friend.",                    "answer": "is visiting"},
                    {"text": "But he mostly ___ (eat) cereal for breakfast.",         "answer": "is eating"},
                    {"text": "But today she ___ (walk) to work.",                     "answer": "is walking"},
                    {"text": "But today she ___ (go) for a walk.",                    "answer": "is going"},
                    {"text": "But today they ___ (play) golf.",                       "answer": "are playing"},
                    {"text": "But this year he ___ (visit) Greece.",                  "answer": "is visiting"},
                    {"text": "But tonight she ___ (read).",                           "answer": "is reading"},
                    {"text": "But today he ___ (watch) a game.",                      "answer": "is watching"},
                    {"text": "But he often ___ (sleep) outside.",                     "answer": "sleeps"},
                    {"text": "But today she ___ (rest).",                             "answer": "is resting"},
                    {"text": "But today they ___ (shop).",                            "answer": "are shopping"},
                ],
            },
        },
    ],
}


class Command(BaseCommand):
    help = "DK English for Everyone Level 2 Unit 01-04+09 uchun namunaviy ma'lumot yuklaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mavjud categories, lessons va exercises ni tozalab, qayta yuklaydi',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Exercise.objects.all().delete()
            Vocabulary.objects.all().delete()
            Lesson.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Eski ma'lumotlar tozalandi."))

        # Categories
        cat_map = {}
        for cat_data in DATA['categories']:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data.get('description', '')},
            )
            cat_map[cat_data['id']] = cat
            status = 'yaratildi' if created else 'mavjud'
            self.stdout.write(f"  Kategoriya [{status}]: {cat.name}")

        # Lessons
        lesson_map = {}
        for l_data in DATA['lessons']:
            lesson, created = Lesson.objects.get_or_create(
                title=l_data['title'],
                defaults={
                    'description': l_data['description'],
                    'video_url': l_data['video_url'],
                    'category': cat_map[l_data['category_id']],
                    'order': l_data['order'],
                },
            )
            lesson_map[l_data['id']] = lesson
            status = 'yaratildi' if created else 'mavjud'
            self.stdout.write(f"  Dars [{status}]: {lesson.title}")

        # Vocabulary
        vocab_count = 0
        for v_data in DATA['vocabulary']:
            lesson = lesson_map.get(v_data['lesson_id'])
            if not lesson:
                continue
            _, created = Vocabulary.objects.get_or_create(
                lesson=lesson,
                word=v_data['word'],
                defaults={
                    'translation': v_data['translation'],
                    'example': v_data.get('example', ''),
                    'order': v_data['order'],
                },
            )
            if created:
                vocab_count += 1

        # Exercises
        created_count = 0
        for ex_data in DATA['exercises']:
            lesson = lesson_map.get(ex_data['lesson_id'])
            if not lesson:
                continue
            _, created = Exercise.objects.get_or_create(
                lesson=lesson,
                type=ex_data['type'],
                instruction=ex_data['instruction'],
                defaults={
                    'content': ex_data['content'],
                    'order': ex_data['order'],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nTayyor! {len(DATA['categories'])} kategoriya, "
            f"{len(DATA['lessons'])} dars, {vocab_count} lug'at so'zi, "
            f"{created_count} mashq yuklandi."
        ))
        self.stdout.write(self.style.WARNING(
            "Video URL larni admin paneldan yangilashni unutmang!"
        ))
