"""
DK English for Everyone Level 2 — Units 05-26 exercises + vocabulary.
Usage: python manage.py seed_book2
       python manage.py seed_book2 --clear
"""
from django.core.management.base import BaseCommand
from courses.models import Category, Lesson, Vocabulary
from quiz.models import Exercise


DATA = {
    # ──────────────────────────────────────────────
    # CATEGORIES
    # ──────────────────────────────────────────────
    "categories": [
        {"name": "Feelings & State Verbs",   "description": "State verbs vs action verbs, expressing feelings"},
        {"name": "Health & Body",             "description": "Body parts, health problems and complaints"},
        {"name": "Weather & Nature",          "description": "Weather conditions and descriptions"},
        {"name": "Travel & Transport",        "description": "Transportation and travel vocabulary"},
        {"name": "Comparisons",               "description": "Comparative and superlative adjectives"},
        {"name": "Past Simple",               "description": "Past simple tense, regular and irregular verbs"},
    ],

    # ──────────────────────────────────────────────
    # LESSONS  (id = internal key used below)
    # ──────────────────────────────────────────────
    "lessons": [
        {
            "id": 10,
            "title": "Unit 05 – Types of verbs",
            "description": "Learn the difference between action verbs and state verbs. State verbs are not normally used in the continuous form.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Feelings & State Verbs",
            "order": 1,
        },
        {
            "id": 11,
            "title": "Unit 07 – How are you feeling?",
            "description": "Use the present continuous with 'feeling' to describe emotions. Learn adjectives for feelings and moods.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Feelings & State Verbs",
            "order": 2,
        },
        {
            "id": 12,
            "title": "Unit 11 – What's the matter?",
            "description": "Learn body parts and how to talk about health problems and illnesses using 'have', 'has' and 'have got'.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Health & Body",
            "order": 1,
        },
        {
            "id": 13,
            "title": "Unit 13 – What's the weather like?",
            "description": "Use 'to be' with weather words and phrases to describe temperature and conditions.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Weather & Nature",
            "order": 1,
        },
        {
            "id": 14,
            "title": "Unit 15 – Making comparisons",
            "description": "Use comparative adjectives with 'than' to describe the difference between two people, places or things.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Comparisons",
            "order": 1,
        },
        {
            "id": 15,
            "title": "Unit 16 – Talking about extremes",
            "description": "Use superlative adjectives to talk about the biggest, the smallest, the most — describing extremes.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Comparisons",
            "order": 2,
        },
        {
            "id": 16,
            "title": "Unit 22 – Talking about the past",
            "description": "Use the past simple of 'to be' — was and were — to talk about past states and situations.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Past Simple",
            "order": 1,
        },
        {
            "id": 17,
            "title": "Unit 26 – Irregular past verbs",
            "description": "Many common English verbs have irregular past simple forms. Learn the most important ones.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_name": "Past Simple",
            "order": 2,
        },
    ],

    # ──────────────────────────────────────────────
    # VOCABULARY
    # ──────────────────────────────────────────────
    "vocabulary": [

        # ── Unit 05: Types of verbs ────────────────
        {"lesson_id": 10, "order": 1,  "word": "action verb",   "translation": "harakat fe'li",       "example": "Run, eat, and play are action verbs."},
        {"lesson_id": 10, "order": 2,  "word": "state verb",    "translation": "holat fe'li",          "example": "Know, love, and want are state verbs."},
        {"lesson_id": 10, "order": 3,  "word": "want",          "translation": "xohlamoq",             "example": "I want some juice, please."},
        {"lesson_id": 10, "order": 4,  "word": "know",          "translation": "bilmoq",               "example": "I know the answer."},
        {"lesson_id": 10, "order": 5,  "word": "love",          "translation": "sevmoq",               "example": "She loves her cat."},
        {"lesson_id": 10, "order": 6,  "word": "hate",          "translation": "yomon ko'rmoq",        "example": "He hates snakes."},
        {"lesson_id": 10, "order": 7,  "word": "remember",      "translation": "eslamoq",              "example": "I remember your birthday."},
        {"lesson_id": 10, "order": 8,  "word": "understand",    "translation": "tushunmoq",            "example": "Do you understand the question?"},
        {"lesson_id": 10, "order": 9,  "word": "believe",       "translation": "ishonmoq",             "example": "I believe you."},
        {"lesson_id": 10, "order": 10, "word": "own",           "translation": "egalik qilmoq",        "example": "We own a horse."},
        {"lesson_id": 10, "order": 11, "word": "seem",          "translation": "ko'rinmoq / tuyulmoq", "example": "She seems tired today."},
        {"lesson_id": 10, "order": 12, "word": "belong",        "translation": "tegishli bo'lmoq",     "example": "This bag belongs to me."},

        # ── Unit 07: Feelings ─────────────────────
        {"lesson_id": 11, "order": 1,  "word": "happy",         "translation": "xursand / baxtli",     "example": "I'm feeling very happy today."},
        {"lesson_id": 11, "order": 2,  "word": "sad",           "translation": "xafa / g'amgin",       "example": "She is feeling sad."},
        {"lesson_id": 11, "order": 3,  "word": "excited",       "translation": "hayajonli / shoshqaloq","example": "The children are excited about the trip."},
        {"lesson_id": 11, "order": 4,  "word": "bored",         "translation": "zerikkan / zerikarli", "example": "Angela is so bored."},
        {"lesson_id": 11, "order": 5,  "word": "nervous",       "translation": "asabiy / xavotirli",   "example": "Jenny is so nervous about the exam."},
        {"lesson_id": 11, "order": 6,  "word": "tired",         "translation": "charchagan",           "example": "Peter is feeling very tired today."},
        {"lesson_id": 11, "order": 7,  "word": "angry",         "translation": "g'azablangan",         "example": "Eve is really angry."},
        {"lesson_id": 11, "order": 8,  "word": "calm",          "translation": "xotirjam / sokin",     "example": "Try to stay calm."},
        {"lesson_id": 11, "order": 9,  "word": "confident",     "translation": "ishonchli / o'ziga ishongan", "example": "She feels confident before the interview."},
        {"lesson_id": 11, "order": 10, "word": "anxious",       "translation": "tashvishli / xavotirli","example": "Peter is feeling anxious."},
        {"lesson_id": 11, "order": 11, "word": "disappointed",  "translation": "umidi puchga chiqqan", "example": "Danny is feeling really disappointed."},
        {"lesson_id": 11, "order": 12, "word": "proud",         "translation": "mag'rur / faxrlanuvchi","example": "She is very proud of her son."},
        {"lesson_id": 11, "order": 13, "word": "worried",       "translation": "tashvishlanayotgan",   "example": "I'm worried about the exam."},
        {"lesson_id": 11, "order": 14, "word": "relaxed",       "translation": "xotirjam / dam olgan", "example": "He feels relaxed on vacation."},
        {"lesson_id": 11, "order": 15, "word": "stressed",      "translation": "stress ostida",        "example": "She is very stressed at work."},
        {"lesson_id": 11, "order": 16, "word": "lonely",        "translation": "yolg'iz / yolg'izlik hissiyoti", "example": "He feels lonely in the big city."},

        # ── Unit 11: Health & Body ────────────────
        {"lesson_id": 12, "order": 1,  "word": "head",          "translation": "bosh",                 "example": "I have a pain in my head."},
        {"lesson_id": 12, "order": 2,  "word": "neck",          "translation": "bo'yin",               "example": "My neck hurts."},
        {"lesson_id": 12, "order": 3,  "word": "shoulder",      "translation": "yelka",                "example": "He has a pain in his shoulder."},
        {"lesson_id": 12, "order": 4,  "word": "arm",           "translation": "qo'l (tirsak yuqori)", "example": "My arm is broken."},
        {"lesson_id": 12, "order": 5,  "word": "knee",          "translation": "tizza",                "example": "I have a pain in my knee."},
        {"lesson_id": 12, "order": 6,  "word": "leg",           "translation": "oyoq",                 "example": "Dan's leg hurts."},
        {"lesson_id": 12, "order": 7,  "word": "foot",          "translation": "oyoq (panja)",         "example": "I have a pain in my foot."},
        {"lesson_id": 12, "order": 8,  "word": "back",          "translation": "orqa",                 "example": "Alfred's back is hurting."},
        {"lesson_id": 12, "order": 9,  "word": "toothache",     "translation": "tish og'rig'i",        "example": "Fiona has an awful toothache."},
        {"lesson_id": 12, "order": 10, "word": "headache",      "translation": "bosh og'rig'i",        "example": "I don't feel well. I have a headache."},
        {"lesson_id": 12, "order": 11, "word": "stomachache",   "translation": "qorin og'rig'i",       "example": "Claire has a terrible stomachache."},
        {"lesson_id": 12, "order": 12, "word": "backache",      "translation": "bel og'rig'i",         "example": "Philip can't stand. He has backache."},
        {"lesson_id": 12, "order": 13, "word": "earache",       "translation": "quloq og'rig'i",       "example": "I can't hear and I have an earache."},
        {"lesson_id": 12, "order": 14, "word": "broken",        "translation": "singan / buzilgan",    "example": "Maria has a broken leg."},
        {"lesson_id": 12, "order": 15, "word": "hurts",         "translation": "og'riydi",             "example": "My knee hurts when I walk."},
        {"lesson_id": 12, "order": 16, "word": "feel sick",     "translation": "kasal his qilmoq",     "example": "I don't feel well today."},

        # ── Unit 13: Weather ──────────────────────
        {"lesson_id": 13, "order": 1,  "word": "sunny",         "translation": "quyoshli",             "example": "It's a sunny day today."},
        {"lesson_id": 13, "order": 2,  "word": "cloudy",        "translation": "bulutli",              "example": "It's very cloudy outside."},
        {"lesson_id": 13, "order": 3,  "word": "rainy",         "translation": "yomg'irli",            "example": "It's raining. We can't play tennis."},
        {"lesson_id": 13, "order": 4,  "word": "windy",         "translation": "shamolly",             "example": "It's a really windy day here."},
        {"lesson_id": 13, "order": 5,  "word": "foggy",         "translation": "tumanli",              "example": "It's very foggy. The airport is closed."},
        {"lesson_id": 13, "order": 6,  "word": "freezing",      "translation": "muzlatuvchi sovuq",    "example": "It's 14°F here and it's freezing."},
        {"lesson_id": 13, "order": 7,  "word": "boiling",       "translation": "qaynoq / juda issiq",  "example": "It's boiling here in Morocco. It's 104°F."},
        {"lesson_id": 13, "order": 8,  "word": "warm",          "translation": "iliq / issiqroq",      "example": "It's quite warm here. The temperature is 68°F."},
        {"lesson_id": 13, "order": 9,  "word": "storm",         "translation": "bo'ron",               "example": "There's a storm. We can't play golf."},
        {"lesson_id": 13, "order": 10, "word": "thunder",       "translation": "momaqaldiroq",         "example": "There's a lot of thunder and lightning."},
        {"lesson_id": 13, "order": 11, "word": "lightning",     "translation": "chaqmoq",              "example": "Last night we had lots of lightning."},
        {"lesson_id": 13, "order": 12, "word": "temperature",   "translation": "harorat / temperatura", "example": "The temperature is 68°F."},
        {"lesson_id": 13, "order": 13, "word": "ice",           "translation": "muz",                  "example": "Be careful. There's ice on the road."},
        {"lesson_id": 13, "order": 14, "word": "flood",         "translation": "suv toshqini",         "example": "The flood destroyed many houses."},
        {"lesson_id": 13, "order": 15, "word": "humidity",      "translation": "namlik / namgarchilik", "example": "The humidity here is very high."},
        {"lesson_id": 13, "order": 16, "word": "rainbow",       "translation": "kamalak",              "example": "After the rain there was a beautiful rainbow."},

        # ── Unit 15: Comparisons / Travel vocab ───
        {"lesson_id": 14, "order": 1,  "word": "luggage",       "translation": "bagaj / yuk",          "example": "I have a lot of luggage for this trip."},
        {"lesson_id": 14, "order": 2,  "word": "passport",      "translation": "pasport",              "example": "Don't forget your passport."},
        {"lesson_id": 14, "order": 3,  "word": "runway",        "translation": "uchish-qo'nish yo'lagi","example": "The plane is on the runway."},
        {"lesson_id": 14, "order": 4,  "word": "boarding card", "translation": "o'tirish kartasi",    "example": "Please show your boarding card."},
        {"lesson_id": 14, "order": 5,  "word": "miss a flight", "translation": "samolyotni qoldirmoq", "example": "We missed our flight by 10 minutes."},
        {"lesson_id": 14, "order": 6,  "word": "go sightseeing","translation": "sayr qilmoq / diqqatga sazovor joylar ko'rmoq", "example": "We go sightseeing every day."},
        {"lesson_id": 14, "order": 7,  "word": "cruise",        "translation": "kruiz / dengiz sayohati","example": "They went on a Caribbean cruise."},
        {"lesson_id": 14, "order": 8,  "word": "hostel",        "translation": "yotoqxona / xonadon",  "example": "I stayed in a hostel to save money."},
        {"lesson_id": 14, "order": 9,  "word": "on time",       "translation": "o'z vaqtida",          "example": "The train arrived on time."},
        {"lesson_id": 14, "order": 10, "word": "road trip",     "translation": "avtomobil sayohati",   "example": "We went on a road trip across Europe."},
        {"lesson_id": 14, "order": 11, "word": "bigger",        "translation": "kattaroq",             "example": "A tiger is bigger than a pig."},
        {"lesson_id": 14, "order": 12, "word": "smaller",       "translation": "kichikroq",            "example": "Vatican City is smaller than Russia."},
        {"lesson_id": 14, "order": 13, "word": "faster",        "translation": "tezroq",               "example": "A plane is faster than a car."},
        {"lesson_id": 14, "order": 14, "word": "older",         "translation": "kattaroq / qadimiyroq","example": "Athens is older than Los Angeles."},
        {"lesson_id": 14, "order": 15, "word": "earlier",       "translation": "ertaroq",              "example": "6am is earlier than 9am."},
        {"lesson_id": 14, "order": 16, "word": "prettier",      "translation": "chiroyliroq",          "example": "Your dress is prettier than mine."},

        # ── Unit 16: Superlatives ─────────────────
        {"lesson_id": 15, "order": 1,  "word": "the biggest",   "translation": "eng katta",            "example": "The African elephant is the biggest land animal."},
        {"lesson_id": 15, "order": 2,  "word": "the smallest",  "translation": "eng kichik",           "example": "Vatican City is the smallest country."},
        {"lesson_id": 15, "order": 3,  "word": "the tallest",   "translation": "eng baland / eng uzun", "example": "The Burj Khalifa is the tallest building."},
        {"lesson_id": 15, "order": 4,  "word": "the longest",   "translation": "eng uzun",             "example": "The Great Wall is the longest wall."},
        {"lesson_id": 15, "order": 5,  "word": "the hottest",   "translation": "eng issiq",            "example": "Death Valley is the hottest place."},
        {"lesson_id": 15, "order": 6,  "word": "the coldest",   "translation": "eng sovuq",            "example": "Antarctica is the coldest place on Earth."},
        {"lesson_id": 15, "order": 7,  "word": "the most",      "translation": "eng ko'p / eng...",    "example": "She is the most intelligent student."},
        {"lesson_id": 15, "order": 8,  "word": "superlative",   "translation": "eng yuqori daraja",    "example": "Use superlative adjectives to talk about extremes."},
        {"lesson_id": 15, "order": 9,  "word": "extreme",       "translation": "ekstremal / haddan tashqari","example": "Death Valley has an extreme climate."},
        {"lesson_id": 15, "order": 10, "word": "record",        "translation": "rekord",               "example": "It holds the record for the highest temperature."},
        {"lesson_id": 15, "order": 11, "word": "highest",       "translation": "eng yuqori",           "example": "Everest is the highest mountain."},
        {"lesson_id": 15, "order": 12, "word": "deepest",       "translation": "eng chuqur",           "example": "The Mariana Trench is the deepest part of the ocean."},

        # ── Unit 22: Past "to be" ─────────────────
        {"lesson_id": 16, "order": 1,  "word": "was",           "translation": "edi (men/u/u uchun)",  "example": "I was at school yesterday."},
        {"lesson_id": 16, "order": 2,  "word": "were",          "translation": "edik/edingiz/edilar",  "example": "We were in Paris last year."},
        {"lesson_id": 16, "order": 3,  "word": "wasn't",        "translation": "emas edi (yakka)",     "example": "It wasn't an interesting book."},
        {"lesson_id": 16, "order": 4,  "word": "weren't",       "translation": "emas edilar (ko'plik)","example": "They weren't very good at science."},
        {"lesson_id": 16, "order": 5,  "word": "yesterday",     "translation": "kecha",                "example": "Where were you yesterday?"},
        {"lesson_id": 16, "order": 6,  "word": "last year",     "translation": "o'tgan yil",           "example": "I was in Canada last year."},
        {"lesson_id": 16, "order": 7,  "word": "ago",           "translation": "oldin",                "example": "The paintings are about 40,000 years old."},
        {"lesson_id": 16, "order": 8,  "word": "in the past",   "translation": "o'tmishda",            "example": "In the past, things were different."},
        {"lesson_id": 16, "order": 9,  "word": "when I was young","translation": "yoshligimda",        "example": "When I was young, I lived in London."},
        {"lesson_id": 16, "order": 10, "word": "born",          "translation": "tug'ilgan",            "example": "I was born in 1990."},
        {"lesson_id": 16, "order": 11, "word": "history",       "translation": "tarix",                "example": "He was a famous person in history."},
        {"lesson_id": 16, "order": 12, "word": "past state",    "translation": "o'tgan holat",         "example": "Use 'was/were' for past states."},

        # ── Unit 26: Irregular verbs ──────────────
        {"lesson_id": 17, "order": 1,  "word": "wrote",         "translation": "yozdi (write → wrote)","example": "I wrote you a letter. Did you get it?"},
        {"lesson_id": 17, "order": 2,  "word": "made",          "translation": "qildi / yaratdi (make → made)","example": "Archie made a cake for my birthday."},
        {"lesson_id": 17, "order": 3,  "word": "sang",          "translation": "kuyladi (sing → sang)", "example": "Bobby sang a song to his mother."},
        {"lesson_id": 17, "order": 4,  "word": "took",          "translation": "oldi / olib ketdi (take → took)","example": "Sophie took her cat to the vet."},
        {"lesson_id": 17, "order": 5,  "word": "began",         "translation": "boshladi (begin → began)","example": "My son began school yesterday."},
        {"lesson_id": 17, "order": 6,  "word": "met",           "translation": "uchrashdi (meet → met)","example": "We met some interesting people today."},
        {"lesson_id": 17, "order": 7,  "word": "sold",          "translation": "sotdi (sell → sold)",  "example": "He sold his car last week."},
        {"lesson_id": 17, "order": 8,  "word": "ate",           "translation": "yedi (eat → ate)",     "example": "She ate all her vegetables."},
        {"lesson_id": 17, "order": 9,  "word": "saw",           "translation": "ko'rdi (see → saw)",   "example": "Jane saw a really good film yesterday."},
        {"lesson_id": 17, "order": 10, "word": "slept",         "translation": "uxladi (sleep → slept)","example": "The dog slept outside last night."},
        {"lesson_id": 17, "order": 11, "word": "bought",        "translation": "sotib oldi (buy → bought)","example": "Roger bought a new car on Wednesday."},
        {"lesson_id": 17, "order": 12, "word": "found",         "translation": "topdi (find → found)", "example": "I found my glasses under the bed."},
        {"lesson_id": 17, "order": 13, "word": "went",          "translation": "bordi (go → went)",    "example": "Derek went home at 11pm."},
        {"lesson_id": 17, "order": 14, "word": "got",           "translation": "oldi / keldi (get → got)","example": "I got a postcard from my brother."},
        {"lesson_id": 17, "order": 15, "word": "felt",          "translation": "his qildi (feel → felt)","example": "Sid felt happy when he finished school."},
        {"lesson_id": 17, "order": 16, "word": "put",           "translation": "qo'ydi (put → put)",   "example": "Felicity put the dishes in the cupboard."},
    ],

    # ──────────────────────────────────────────────
    # EXERCISES
    # ──────────────────────────────────────────────
    "exercises": [

        # ── Unit 05: Types of verbs ────────────────
        {
            "lesson_id": 10,
            "type": "choose_correct",
            "instruction": "To'g'ri so'zni tanlang (holat fe'llar odatda davomli shaklda ishlatilmaydi)",
            "order": 1,
            "content": {
                "sentences": [
                    {"before": "I ",         "options": ["want", "am wanting"],        "after": " some juice please.",           "correct": 0},
                    {"before": "Greg ",      "options": ["plays", "is playing"],       "after": " tennis now.",                  "correct": 1},
                    {"before": "Mo ",        "options": ["watches", "is watching"],    "after": " TV right now.",                "correct": 1},
                    {"before": "We ",        "options": ["have", "are having"],        "after": " a new dog.",                   "correct": 0},
                    {"before": "You ",       "options": ["don't like", "aren't liking"],"after": " snakes.",                    "correct": 0},
                    {"before": "Dom ",       "options": ["goes", "is going"],          "after": " to school now.",               "correct": 1},
                    {"before": "I ",         "options": ["remember", "am remembering"],"after": " it is your birthday today.",  "correct": 0},
                    {"before": "Dan ",       "options": ["is drinking", "drinks"],     "after": " a cup of tea right now.",      "correct": 0},
                ]
            },
        },
        {
            "lesson_id": 10,
            "type": "matching",
            "instruction": "Harakat fe'llari va holat fe'llarini ajrating (Action verbs vs State verbs)",
            "order": 2,
            "content": {
                "left":  ["run", "sing", "eat", "play", "go", "listen", "cook", "walk"],
                "right": ["like", "know", "love", "want", "hate", "remember", "understand", "believe"],
                "pairs": [0, 1, 2, 3, 4, 5, 6, 7],
            },
        },

        # ── Unit 07: Feelings ─────────────────────
        {
            "lesson_id": 11,
            "type": "matching",
            "instruction": "His-tuyg'ularni sabablar bilan moslang",
            "order": 1,
            "content": {
                "left": [
                    "Claude is feeling really happy today.",
                    "Eve is really angry.",
                    "Peter is feeling very tired today.",
                    "Jenny is so nervous.",
                    "Danny is feeling really disappointed.",
                    "Angela is so bored.",
                ],
                "right": [
                    "So he's staying in bed.",
                    "He didn't win the competition.",
                    "He wants something to do.",
                    "It's his birthday.",
                    "The bus still hasn't arrived.",
                    "She has an exam tomorrow.",
                ],
                "pairs": [3, 1, 0, 5, 4, 2],
            },
        },
        {
            "lesson_id": 11,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri his-tuyg'u so'zini tanlang",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "I have my exam tomorrow. I'm so ___.",                  "answer": "nervous"},
                    {"text": "I don't know what to do. There's nothing on TV. I'm really ___.", "answer": "bored"},
                    {"text": "It's my birthday tomorrow. I really can't wait! I'm so ___.", "answer": "excited"},
                    {"text": "This book is really depressing. So many bad things happen. I'm feeling really ___.", "answer": "sad"},
                    {"text": "I don't like this house. It's so dark. I'm feeling ___.", "answer": "scared"},
                    {"text": "My girlfriend's forgotten my birthday. I'm so ___.",     "answer": "angry"},
                ],
                "word_panel": ["nervous", "bored", "excited", "sad", "scared", "angry"],
            },
        },

        # ── Unit 11: What's the matter? ───────────
        {
            "lesson_id": 12,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri so'zni tanlang (health complaints)",
            "order": 1,
            "content": {
                "sentences": [
                    {"text": "Fiona has an awful ___.",                   "answer": "toothache"},
                    {"text": "I can't hear and I have an ___.",           "answer": "earache"},
                    {"text": "Dan's leg ___.",                            "answer": "hurts"},
                    {"text": "Maria has a ___ leg.",                      "answer": "broken"},
                    {"text": "I don't feel well. I have a ___.",          "answer": "headache"},
                    {"text": "Claire has a terrible ___.",                "answer": "stomachache"},
                    {"text": "I have a ___ in my knee.",                  "answer": "pain"},
                    {"text": "Philip can't stand. He has ___.",           "answer": "backache"},
                ],
                "word_panel": ["stomachache", "headache", "pain", "broken", "hurts", "toothache", "backache", "earache"],
            },
        },
        {
            "lesson_id": 12,
            "type": "choose_correct",
            "instruction": "To'g'ri shaklni tanlang: 'have' yoki 'have got'",
            "order": 2,
            "content": {
                "sentences": [
                    {"before": "I ",          "options": ["have", "have got"],  "after": " a broken leg.",          "correct": 0},
                    {"before": "You ",        "options": ["have", "have got"],  "after": " a pain in my foot.",     "correct": 1},
                    {"before": "Anna ",       "options": ["has", "has got"],    "after": " a headache.",            "correct": 0},
                    {"before": "I ",          "options": ["have", "have got"],  "after": " a sore throat.",         "correct": 0},
                    {"before": "He ",         "options": ["has", "has got"],    "after": " a backache.",            "correct": 1},
                    {"before": "She ",        "options": ["has", "has got"],    "after": " toothache.",             "correct": 0},
                ]
            },
        },

        # ── Unit 13: Weather ──────────────────────
        {
            "lesson_id": 13,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri ob-havo so'zini tanlang",
            "order": 1,
            "content": {
                "sentences": [
                    {"text": "It's ___ here in Morocco. It's 104°F.",           "answer": "boiling"},
                    {"text": "Be careful. There's ___ on the road.",            "answer": "ice"},
                    {"text": "The weather's beautiful. It's hot and ___.",      "answer": "sunny"},
                    {"text": "It's quite ___ here. The temperature is 68°F.",   "answer": "warm"},
                    {"text": "It's 14°F here and it's snowy. It's ___.",        "answer": "freezing"},
                    {"text": "Oh no, it's ___. We can't play tennis now.",      "answer": "raining"},
                    {"text": "It's very ___. The airport is closed.",           "answer": "foggy"},
                    {"text": "There's a ___. We can't play golf.",              "answer": "storm"},
                ],
                "word_panel": ["warm", "freezing", "ice", "foggy", "boiling", "raining", "storm", "sunny"],
            },
        },
        {
            "lesson_id": 13,
            "type": "fill_blank",
            "instruction": "Gapni qayta yozing: 'There's a lot of...' shaklini boshqacha ifodalang",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "There's a lot of fog. → It's very ___.",              "answer": "foggy"},
                    {"text": "There's a lot of wind. → It's very ___.",             "answer": "windy"},
                    {"text": "There's a lot of rain. → It's very ___.",             "answer": "rainy"},
                    {"text": "There's a lot of snow. → It's very ___.",             "answer": "snowy"},
                    {"text": "There's a lot of sun. → It's very ___.",              "answer": "sunny"},
                    {"text": "There are a lot of storms. → It's very ___.",         "answer": "stormy"},
                    {"text": "There are a lot of clouds. → It's very ___.",         "answer": "cloudy"},
                    {"text": "There's a lot of ice. → It's very ___.",              "answer": "icy"},
                ],
                "word_panel": ["foggy", "windy", "rainy", "snowy", "sunny", "stormy", "cloudy", "icy"],
            },
        },

        # ── Unit 15: Making comparisons ───────────
        {
            "lesson_id": 14,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri qiyosiy sifatni tanlang",
            "order": 1,
            "content": {
                "sentences": [
                    {"text": "I'm ___ than you are.",                       "answer": "taller"},
                    {"text": "A train is ___ than a bus.",                  "answer": "faster"},
                    {"text": "79°F is ___ than 64°F.",                     "answer": "hotter"},
                    {"text": "A car is faster than a ___.",                 "answer": "bike"},
                    {"text": "___ is smaller than Russia.",                 "answer": "France"},
                    {"text": "Everest is higher than ___.",                 "answer": "Mont Blanc"},
                    {"text": "6am is ___ than 9am.",                       "answer": "earlier"},
                    {"text": "A tiger is ___ than a pig.",                  "answer": "bigger"},
                    {"text": "Your dress is ___ than mine.",                "answer": "prettier"},
                    {"text": "95°F is ___ than 110°F.",                    "answer": "colder"},
                    {"text": "The Sahara is ___ than the Arctic.",          "answer": "hotter"},
                    {"text": "11pm is ___ than 3pm.",                      "answer": "later"},
                    {"text": "An ___ is bigger than a mouse.",              "answer": "elephant"},
                    {"text": "A plane is ___ than a car.",                  "answer": "faster"},
                    {"text": "Mars is ___ to Earth than Pluto.",            "answer": "closer"},
                    {"text": "Athens is ___ than Los Angeles.",             "answer": "older"},
                ],
                "word_panel": ["taller", "faster", "hotter", "bike", "France", "Mont Blanc", "earlier", "bigger", "prettier", "colder", "later", "elephant", "closer", "older"],
            },
        },
        {
            "lesson_id": 14,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi sifatni qiyosiy shaklga soling",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "Anna is ___ (good) at skiing than I am.",             "answer": "better"},
                    {"text": "My exam results were ___ (bad) than Frank's.",         "answer": "worse"},
                    {"text": "The Plaza is the ___ (good) hotel in the city.",      "answer": "best"},
                    {"text": "My new workplace is ___ (far) from my house than my old one.", "answer": "farther"},
                    {"text": "I am a ___ (good) driver than my brother.",           "answer": "better"},
                    {"text": "Don't go to Gigi's. It's the ___ (bad) cafe in town.","answer": "worst"},
                ],
            },
        },

        # ── Unit 16: Talking about extremes ───────
        {
            "lesson_id": 15,
            "type": "fill_blank",
            "instruction": "Qavs ichidagi sifatni eng yuqori darajaga (superlative) soling",
            "order": 1,
            "content": {
                "sentences": [
                    {"text": "Death Valley in California is the ___ (hot) place in the world.",     "answer": "hottest"},
                    {"text": "The Great Wall of China is the ___ (long) wall in the country.",      "answer": "longest"},
                    {"text": "The African Bush Elephant is the ___ (big) land animal.",             "answer": "biggest"},
                    {"text": "Vatican City is the ___ (small) country in the world.",               "answer": "smallest"},
                    {"text": "The Burj Khalifa is the ___ (tall) building in the world.",           "answer": "tallest"},
                    {"text": "Dolphins are in the top 10 ___ (intelligent) animals.",               "answer": "most intelligent"},
                ],
            },
        },
        {
            "lesson_id": 15,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri eng yuqori daraja sifatni tanlang",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "Moscow is a very large city. It is ___ city in Europe.",          "answer": "the largest"},
                    {"text": "The Shanghai Tower is a very tall building. It is ___ in China.", "answer": "the tallest"},
                    {"text": "The Vasco da Gama bridge in Portugal is very long. It is ___ in Europe.", "answer": "the longest"},
                    {"text": "The Dead Sea is a very low place on Earth. It is ___ on Earth.", "answer": "the lowest"},
                    {"text": "Mount Elbrus in Russia is a very tall mountain. It is ___ in Europe.", "answer": "the highest"},
                ],
                "word_panel": ["the largest", "the tallest", "the longest", "the lowest", "the highest"],
            },
        },

        # ── Unit 22: Past simple "to be" ──────────
        {
            "lesson_id": 16,
            "type": "choose_correct",
            "instruction": "To'g'ri so'zni tanlang: 'wasn't' yoki 'weren't'",
            "order": 1,
            "content": {
                "sentences": [
                    {"before": "They ",             "options": ["wasn't", "weren't"], "after": " very good at science.",       "correct": 1},
                    {"before": "It ",               "options": ["wasn't", "weren't"], "after": " an interesting book.",        "correct": 0},
                    {"before": "There ",            "options": ["wasn't", "weren't"], "after": " any good movies on.",        "correct": 1},
                    {"before": "We ",               "options": ["wasn't", "weren't"], "after": " in the US in 2012.",         "correct": 1},
                    {"before": "Glen ",             "options": ["wasn't", "weren't"], "after": " at home when I called.",     "correct": 0},
                    {"before": "There ",            "options": ["wasn't", "weren't"], "after": " a theater in my town.",      "correct": 0},
                    {"before": "Trevor ",           "options": ["wasn't", "weren't"], "after": " in Berlin in 1994.",         "correct": 0},
                    {"before": "There ",            "options": ["wasn't", "weren't"], "after": " a library in the town.",     "correct": 0},
                    {"before": "We ",               "options": ["wasn't", "weren't"], "after": " at home last night.",        "correct": 1},
                    {"before": "Peter ",            "options": ["wasn't", "weren't"], "after": " a student at Harvard.",      "correct": 0},
                    {"before": "Meg and Clive ",    "options": ["wasn't", "weren't"], "after": " teachers then.",             "correct": 1},
                    {"before": "They ",             "options": ["wasn't", "weren't"], "after": " at the restaurant last night.", "correct": 1},
                ]
            },
        },
        {
            "lesson_id": 16,
            "type": "fill_blank",
            "instruction": "Gapni salbiy shaklga o'tkazing (was → wasn't / were → weren't)",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "She was a very good teacher. → She ___ a very good teacher.",          "answer": "wasn't"},
                    {"text": "Brad was a teacher in 2012. → Brad ___ a teacher in 2012.",            "answer": "wasn't"},
                    {"text": "The weather was bad. → The weather ___ bad.",                          "answer": "wasn't"},
                    {"text": "It was a comfortable bed. → It ___ a comfortable bed.",                "answer": "wasn't"},
                    {"text": "They were interesting people. → They ___ interesting people.",         "answer": "weren't"},
                    {"text": "Brendan's parents were doctors. → Brendan's parents ___ doctors.",     "answer": "weren't"},
                    {"text": "Pete and Sue were on the beach all day. → Pete and Sue ___ on the beach.", "answer": "weren't"},
                ],
                "word_panel": ["wasn't", "weren't"],
            },
        },

        # ── Unit 26: Irregular past verbs ─────────
        {
            "lesson_id": 17,
            "type": "matching",
            "instruction": "Fe'llarni o'tgan zamon shakli bilan moslang (Irregular verbs)",
            "order": 1,
            "content": {
                "left":  ["write", "make", "sing", "put", "begin", "meet", "sell", "take", "eat", "see", "sleep", "buy"],
                "right": ["sang", "wrote", "began", "took", "made", "ate", "slept", "put", "bought", "met", "saw", "sold"],
                "pairs": [1, 4, 0, 7, 2, 9, 11, 3, 5, 10, 6, 8],
            },
        },
        {
            "lesson_id": 17,
            "type": "fill_blank",
            "instruction": "So'z panelidan to'g'ri o'tgan zamon fe'lini tanlang",
            "order": 2,
            "content": {
                "sentences": [
                    {"text": "Sophie ___ her cat to the vet.",                "answer": "took"},
                    {"text": "I ___ you a letter. Did you get it?",           "answer": "wrote"},
                    {"text": "We ___ some interesting people today.",          "answer": "met"},
                    {"text": "Roger ___ a new car on Wednesday.",              "answer": "bought"},
                    {"text": "Jane ___ a really good film yesterday.",         "answer": "saw"},
                    {"text": "I ___ a postcard from my brother.",              "answer": "got"},
                    {"text": "Derek ___ home at 11pm.",                       "answer": "went"},
                    {"text": "Archie ___ a cake for my birthday.",             "answer": "made"},
                    {"text": "My son ___ school yesterday.",                   "answer": "began"},
                    {"text": "I ___ my glasses under the bed.",                "answer": "found"},
                    {"text": "Sid ___ happy when he finished school.",         "answer": "felt"},
                    {"text": "Bobby ___ a song to his mother.",                "answer": "sang"},
                ],
                "word_panel": ["took", "wrote", "met", "bought", "saw", "got", "went", "made", "began", "found", "felt", "sang"],
            },
        },
    ],
}


class Command(BaseCommand):
    help = "DK English Level 2 Units 05-26 — kategoriya, dars, lug'at va mashqlarni yuklaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Faqat shu komanda tomonidan qo\'shiladigan darslarni tozalab, qayta yuklaydi',
        )

    def handle(self, *args, **options):
        lesson_titles = [l['title'] for l in DATA['lessons']]

        if options['clear']:
            deleted_v = Vocabulary.objects.filter(lesson__title__in=lesson_titles).delete()[0]
            deleted_e = Exercise.objects.filter(lesson__title__in=lesson_titles).delete()[0]
            deleted_l = Lesson.objects.filter(title__in=lesson_titles).delete()[0]
            self.stdout.write(self.style.WARNING(
                f"Tozalandi: {deleted_l} dars, {deleted_v} lugat, {deleted_e} mashq."
            ))

        # Categories
        cat_map = {}
        for cat_data in DATA['categories']:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data.get('description', '')},
            )
            cat_map[cat_data['name']] = cat
            status = 'yaratildi' if created else 'mavjud'
            self.stdout.write(f"  Kategoriya [{status}]: {cat.name}")

        # Lessons
        lesson_map = {}
        for l_data in DATA['lessons']:
            cat = cat_map.get(l_data['category_name'])
            if not cat:
                self.stdout.write(self.style.ERROR(f"  Kategoriya topilmadi: {l_data['category_name']}"))
                continue
            lesson, created = Lesson.objects.get_or_create(
                title=l_data['title'],
                defaults={
                    'description': l_data['description'],
                    'video_url': l_data['video_url'],
                    'category': cat,
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
        ex_count = 0
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
                ex_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nTayyor! {len(DATA['categories'])} kategoriya, "
            f"{len(DATA['lessons'])} dars, "
            f"{vocab_count} lug'at so'zi, "
            f"{ex_count} mashq yuklandi."
        ))
        self.stdout.write(self.style.WARNING(
            "Video URL larni admin paneldan haqiqiy YouTube linklarga yangilang!"
        ))
