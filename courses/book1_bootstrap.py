"""
Book 1 bo'sh/yarim unitlar uchun boshlang'ich kontent.
Gemini topshiriq topa olmagan unitlarni to'ldiradi.
"""

BOOK1_BOOTSTRAP = {
    2: {
        'vocabulary': [
            ('hello', 'salom', 'Hello, how are you?'),
            ('goodbye', 'xayr', 'Goodbye, see you tomorrow.'),
            ('hi', 'salom (norasmiy)', 'Hi, nice to meet you.'),
            ('good morning', 'xayrli tong', 'Good morning, class.'),
            ('good night', 'xayrli tun', 'Good night, sleep well.'),
            ('please', 'iltimos', 'Please sit down.'),
            ('thank you', 'rahmat', 'Thank you very much.'),
            ('nice to meet you', 'tanishganimdan xursandman', 'Nice to meet you too.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Fill in the gaps with the correct greeting',
                'content': {'sentences': [
                    {'text': '___ , my name is Sam.', 'answer': 'Hello'},
                    {'text': '___ , see you later!', 'answer': 'Goodbye'},
                    {'text': '___ morning, teacher.', 'answer': 'Good'},
                    {'text': '___ you for your help.', 'answer': 'Thank'},
                ]},
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct word',
                'content': {'sentences': [
                    {'before': 'We say "', 'options': ['goodbye', 'hello'], 'after': '" when we leave.', 'correct': 0},
                    {'before': 'We say "', 'options': ['hello', 'goodbye'], 'after': '" when we arrive.', 'correct': 0},
                    {'before': '"', 'options': ['Please', 'Thank you'], 'after': '" means "iltimos".', 'correct': 0},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match the English phrases with Uzbek translations',
                'content': {
                    'left': ['hello', 'goodbye', 'thank you', 'good morning'],
                    'right': ['salom', 'xayr', 'rahmat', 'xayrli tong'],
                    'pairs': [0, 1, 2, 3],
                },
            },
        ],
        'quizzes': [
            ('What do you say when you meet someone?', ['hello', 'goodbye', 'good night', 'please'], 0),
            ('What do you say when you leave?', ['hello', 'goodbye', 'hi', 'morning'], 1),
            ('"Rahmat" in English is:', ['please', 'thank you', 'sorry', 'hello'], 1),
        ],
    },
    4: {
        'vocabulary': [
            ('he', 'u (erkak)', 'He is my brother.'),
            ('she', 'u (ayol)', 'She is my sister.'),
            ('they', 'ular', 'They are students.'),
            ('his', 'uning (erkak)', 'This is his book.'),
            ('her', 'uning (ayol)', 'Her name is Sara.'),
            ('their', 'ularning', 'This is their house.'),
            ('man', 'erkak', 'The man is tall.'),
            ('woman', 'ayol', 'The woman is kind.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete the sentences with he, she, or they',
                'content': {'sentences': [
                    {'text': '___ is a doctor. (Maria)', 'answer': 'She'},
                    {'text': '___ are from Japan.', 'answer': 'They'},
                    {'text': '___ is my father.', 'answer': 'He'},
                    {'text': '___ is a teacher. (Anna)', 'answer': 'She'},
                ]},
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct possessive word',
                'content': {'sentences': [
                    {'before': 'This is ', 'options': ['his', 'her'], 'after': ' bag. (Tom)', 'correct': 0},
                    {'before': 'That is ', 'options': ['his', 'her'], 'after': ' phone. (Lisa)', 'correct': 1},
                    {'before': '', 'options': ['Their', 'Her'], 'after': ' children are happy.', 'correct': 0},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match the pronouns',
                'content': {
                    'left': ['he', 'she', 'they', 'her'],
                    'right': ['u (erkak)', 'u (ayol)', 'ular', 'uning (ayol)'],
                    'pairs': [0, 1, 2, 3],
                },
            },
        ],
        'quizzes': [
            ('"She" refers to:', ['a man', 'a woman', 'many people', 'a thing'], 1),
            ('"Their" means:', ['uning', 'ularning', 'mening', 'sizning'], 1),
            ('Complete: ___ is a student. (Ali — erkak)', ['She', 'He', 'They', 'Her'], 1),
        ],
    },
    8: {
        'vocabulary': [
            ('bag', 'sumka', 'This is my bag.'),
            ('phone', 'telefon', 'Her phone is new.'),
            ('keys', 'kalitlar', 'My keys are on the table.'),
            ('glasses', 'ko\'zoynak', 'His glasses are broken.'),
            ('watch', 'soat', 'I lost my watch.'),
            ('umbrella', 'soyabon', 'Take your umbrella.'),
            ('laptop', 'noutbuk', 'This is her laptop.'),
            ('camera', 'kamera', 'His camera is expensive.'),
        ],
    },
    10: {
        'vocabulary': [
            ('office', 'ofis', 'I work in an office.'),
            ('colleague', 'hamkasb', 'She is my colleague.'),
            ('boss', 'rahbar', 'The boss is strict.'),
            ('salary', 'maosh', 'His salary is good.'),
            ('meeting', 'yig\'ilish', 'We have a meeting today.'),
            ('deadline', 'muddat', 'The deadline is Friday.'),
            ('full-time', 'to\'liq stavka', 'She works full-time.'),
            ('part-time', 'yarim stavka', 'He works part-time.'),
        ],
    },
    12: {
        'vocabulary': [
            ('movie', 'kino', 'We watched a movie.'),
            ('music', 'musiqa', 'I love music.'),
            ('concert', 'konsert', 'The concert was amazing.'),
            ('theater', 'teatr', 'They went to the theater.'),
            ('game', 'o\'yin', 'Let\'s play a game.'),
            ('party', 'ziyofat', 'The party was fun.'),
            ('dance', 'raqs', 'She likes to dance.'),
            ('sing', "qo'shiq aytmoq", 'He can sing well.'),
        ],
    },
    20: {
        'vocabulary': [
            ('what', 'nima', 'What is your name?'),
            ('where', 'qayerda', 'Where do you live?'),
            ('when', 'qachon', 'When is your birthday?'),
            ('who', 'kim', 'Who is that?'),
            ('why', 'nega', 'Why are you late?'),
            ('how', 'qanday', 'How are you?'),
            ('which', 'qaysi', 'Which color do you prefer?'),
            ('how old', 'necha yosh', 'How old are you?'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Fill in the question words',
                'content': {'sentences': [
                    {'text': '___ is your name?', 'answer': 'What'},
                    {'text': '___ do you live?', 'answer': 'Where'},
                    {'text': '___ is your birthday?', 'answer': 'When'},
                    {'text': '___ are you?', 'answer': 'How'},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match question words to Uzbek',
                'content': {
                    'left': ['what', 'where', 'when', 'who'],
                    'right': ['nima', 'qayerda', 'qachon', 'kim'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct question word',
                'content': {'sentences': [
                    {'before': '', 'options': ['Who', 'What'], 'after': ' is that man?', 'correct': 0},
                    {'before': '', 'options': ['Why', 'Where'], 'after': ' are you sad?', 'correct': 0},
                    {'before': '', 'options': ['How', 'When'], 'after': ' old are you?', 'correct': 0},
                ]},
            },
        ],
        'quizzes': [
            ('"Qayerda?" in English:', ['what', 'where', 'when', 'who'], 1),
            ('"Kim?" in English:', ['what', 'where', 'who', 'why'], 2),
            ('___ is your phone number?', ['Who', 'What', 'Where', 'When'], 1),
        ],
    },
    27: {
        'vocabulary': [
            ('in', 'ichida', 'The keys are in the bag.'),
            ('on', 'ustida', 'The book is on the table.'),
            ('under', 'ostida', 'The cat is under the chair.'),
            ('next to', 'yonida', 'The bank is next to the school.'),
            ('behind', 'orqasida', 'The garden is behind the house.'),
            ('in front of', 'oldida', 'The car is in front of the building.'),
            ('between', 'orasida', 'The cafe is between the bank and the shop.'),
            ('near', 'yaqinida', 'The park is near my house.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Fill in the prepositions',
                'content': {'sentences': [
                    {'text': 'The phone is ___ the table.', 'answer': 'on'},
                    {'text': 'The cat is ___ the chair.', 'answer': 'under'},
                    {'text': 'She sits ___ me.', 'answer': 'next to'},
                    {'text': 'The keys are ___ my bag.', 'answer': 'in'},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match prepositions',
                'content': {
                    'left': ['in', 'on', 'under', 'next to'],
                    'right': ['ichida', 'ustida', 'ostida', 'yonida'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct preposition',
                'content': {'sentences': [
                    {'before': 'The picture is ', 'options': ['on', 'in'], 'after': ' the wall.', 'correct': 0},
                    {'before': 'The shop is ', 'options': ['behind', 'under'], 'after': ' the school.', 'correct': 0},
                ]},
            },
        ],
        'quizzes': [
            ('"Ostida" in English:', ['on', 'under', 'in', 'near'], 1),
            ('The book is ___ the bag.', ['on', 'in', 'under', 'behind'], 1),
            ('"Yonida" means:', ['behind', 'next to', 'under', 'in front of'], 1),
        ],
    },
    30: {
        'vocabulary': [
            ('how many', 'nechta', 'How many books do you have?'),
            ('a lot of', 'ko\'p', 'I have a lot of friends.'),
            ('a few', 'bir nechta', 'I need a few minutes.'),
            ('some', 'ba\'zi', 'I have some questions.'),
            ('any', 'biror', 'Do you have any brothers?'),
            ('none', 'hech biri', 'I have none.'),
            ('count', 'sanamoq', 'Can you count to ten?'),
            ('number', 'raqam', 'Write the number here.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete with how many or how much',
                'content': {'sentences': [
                    {'text': '___ apples do you want?', 'answer': 'How many'},
                    {'text': '___ students are in the class?', 'answer': 'How many'},
                    {'text': 'I have ___ friends.', 'answer': 'a lot of'},
                    {'text': 'Do you have ___ questions?', 'answer': 'any'},
                ]},
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct word',
                'content': {'sentences': [
                    {'before': '', 'options': ['How many', 'How much'], 'after': ' chairs are there?', 'correct': 0},
                    {'before': 'I have ', 'options': ['a few', 'a little'], 'after': ' books.', 'correct': 0},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match the phrases',
                'content': {
                    'left': ['how many', 'a lot of', 'a few', 'none'],
                    'right': ['nechta', 'ko\'p', 'bir nechta', 'hech biri'],
                    'pairs': [0, 1, 2, 3],
                },
            },
        ],
        'quizzes': [
            ('"Nechta?" in English:', ['how much', 'how many', 'how old', 'how long'], 1),
            ('___ brothers do you have?', ['How much', 'How many', 'How old', 'What'], 1),
            ('"Ko\'p" means:', ['a few', 'a lot of', 'none', 'any'], 1),
        ],
    },
    33: {
        'vocabulary': [
            ('price', 'narx', 'What is the price?'),
            ('cheap', 'arzon', 'This shirt is cheap.'),
            ('expensive', 'qimmat', 'The watch is expensive.'),
            ('how much', 'qancha', 'How much is it?'),
            ('dollar', 'dollar', 'It costs ten dollars.'),
            ('pound', 'funt', 'It costs five pounds.'),
            ('cost', 'turadi', 'How much does it cost?'),
            ('pay', 'to\'lamoq', 'I will pay by card.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete the sentences about prices',
                'content': {'sentences': [
                    {'text': '___ much is this bag?', 'answer': 'How'},
                    {'text': 'This jacket is very ___.', 'answer': 'expensive'},
                    {'text': 'The shoes are ___.', 'answer': 'cheap'},
                    {'text': 'I will ___ by card.', 'answer': 'pay'},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match price vocabulary',
                'content': {
                    'left': ['cheap', 'expensive', 'how much', 'price'],
                    'right': ['arzon', 'qimmat', 'qancha', 'narx'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct word',
                'content': {'sentences': [
                    {'before': '', 'options': ['How much', 'How many'], 'after': ' is the shirt?', 'correct': 0},
                    {'before': 'The bag is very ', 'options': ['cheap', 'expensive'], 'after': '. (only $5)', 'correct': 0},
                ]},
            },
        ],
        'quizzes': [
            ('"Qancha?" when asking price:', ['how many', 'how much', 'how old', 'what'], 1),
            ('"Arzon" means:', ['expensive', 'cheap', 'free', 'new'], 1),
            ('___ does it cost?', ['How many', 'How much', 'What', 'Where'], 1),
        ],
    },
    36: {
        'vocabulary': [
            ('bigger', 'kattaroq', 'This house is bigger.'),
            ('smaller', 'kichikroq', 'My room is smaller.'),
            ('taller', 'balandroq', 'He is taller than me.'),
            ('shorter', 'pastroq', 'She is shorter than him.'),
            ('faster', 'tezroq', 'The car is faster.'),
            ('slower', 'sekinroq', 'The bus is slower.'),
            ('better', 'yaxshiroq', 'This is better.'),
            ('than', '...dan', 'She is older than me.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete with comparatives',
                'content': {'sentences': [
                    {'text': 'She is ___ than her sister.', 'answer': 'taller'},
                    {'text': 'This bag is ___ than that one.', 'answer': 'bigger'},
                    {'text': 'He runs ___ than me.', 'answer': 'faster'},
                    {'text': 'My phone is ___ than yours.', 'answer': 'better'},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match comparatives',
                'content': {
                    'left': ['bigger', 'smaller', 'faster', 'better'],
                    'right': ['kattaroq', 'kichikroq', 'tezroq', 'yaxshiroq'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct comparative',
                'content': {'sentences': [
                    {'before': 'Tom is ', 'options': ['taller', 'tallest'], 'after': ' than Sam.', 'correct': 0},
                    {'before': 'This test is ', 'options': ['easier', 'easy'], 'after': ' than the last one.', 'correct': 0},
                ]},
            },
        ],
        'quizzes': [
            ('"Kattaroq" means:', ['big', 'bigger', 'biggest', 'small'], 1),
            ('She is older ___ me.', ['of', 'than', 'from', 'at'], 1),
            ('Complete: fast → ___', ['fastly', 'faster', 'fastest', 'more fast'], 1),
        ],
    },
    39: {
        'vocabulary': [
            ('weekend', 'dam olish kunlari', 'I relax on the weekend.'),
            ('hobby', 'hobbi', 'Reading is my hobby.'),
            ('relax', 'dam olmoq', 'I like to relax at home.'),
            ('go out', 'tashqariga chiqmoq', 'We go out on Saturdays.'),
            ('stay in', 'uyda qolmoq', 'I prefer to stay in.'),
            ('visit', 'tashrif buyurmoq', 'We visit friends.'),
            ('picnic', 'piknik', 'We had a picnic in the park.'),
            ('barbecue', 'barbekyu', 'They had a barbecue.'),
        ],
    },
    41: {
        'vocabulary': [
            ('prefer', 'afzal ko\'rmoq', 'I prefer tea to coffee.'),
            ('would rather', 'afzal ko\'rgan bo\'lar edim', 'I would rather stay home.'),
            ('favorite', 'sevimli', 'Blue is my favorite color.'),
            ('instead', 'buning o\'rniga', 'I will have water instead.'),
            ('choice', 'tanlov', 'It is your choice.'),
            ('opinion', 'fikr', 'In my opinion, it is good.'),
            ('agree', 'rozi bo\'lmoq', 'I agree with you.'),
            ('disagree', 'rozi bo\'lmaslik', 'I disagree.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete the preference sentences',
                'content': {'sentences': [
                    {'text': 'I ___ tea to coffee.', 'answer': 'prefer'},
                    {'text': 'I would ___ stay home.', 'answer': 'rather'},
                    {'text': 'Blue is my ___ color.', 'answer': 'favorite'},
                    {'text': 'I ___ with you.', 'answer': 'agree'},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match preference words',
                'content': {
                    'left': ['prefer', 'favorite', 'agree', 'choice'],
                    'right': ['afzal ko\'rmoq', 'sevimli', 'rozi bo\'lmoq', 'tanlov'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose the correct word',
                'content': {'sentences': [
                    {'before': 'I ', 'options': ['prefer', 'favorite'], 'after': ' reading to watching TV.', 'correct': 0},
                    {'before': 'I ', 'options': ['agree', 'disagree'], 'after': ' — that is wrong.', 'correct': 1},
                ]},
            },
        ],
        'quizzes': [
            ('"Afzal ko\'rmoq" means:', ['prefer', 'favorite', 'choice', 'agree'], 0),
            ('I prefer coffee ___ tea.', ['of', 'to', 'than', 'from'], 1),
            ('"Sevimli" in English:', ['prefer', 'favorite', 'choice', 'opinion'], 1),
        ],
    },
    43: {
        'vocabulary': [
            ('can', 'qila olmoq', 'I can swim.'),
            ('cannot', 'qila olmaslik', 'I cannot drive.'),
            ("can't", 'qila olmayman', "I can't cook."),
            ('able to', 'qodir bo\'lmoq', 'She is able to help.'),
            ('unable to', 'qodir emas', 'He is unable to come.'),
            ('possible', 'mumkin', 'It is possible.'),
            ('impossible', 'imkonsiz', 'It is impossible.'),
            ('permission', 'ruxsat', 'You have permission.'),
        ],
        'exercises': [
            {
                'type': 'fill_blank',
                'instruction': 'Complete with can or can\'t',
                'content': {'sentences': [
                    {'text': 'I ___ swim very well.', 'answer': 'can'},
                    {'text': 'She ___ drive a car.', 'answer': "can't"},
                    {'text': 'They ___ speak French.', 'answer': 'can'},
                    {'text': 'He ___ cook.', 'answer': "can't"},
                ]},
            },
            {
                'type': 'matching',
                'instruction': 'Match ability words',
                'content': {
                    'left': ['can', "can't", 'able to', 'unable to'],
                    'right': ['qila olmoq', 'qila olmayman', 'qodir', 'qodir emas'],
                    'pairs': [0, 1, 2, 3],
                },
            },
            {
                'type': 'choose_correct',
                'instruction': 'Choose can or can\'t',
                'content': {'sentences': [
                    {'before': 'Birds ', 'options': ['can', "can't"], 'after': ' fly.', 'correct': 0},
                    {'before': 'Fish ', 'options': ['can', "can't"], 'after': ' walk on land.', 'correct': 1},
                ]},
            },
        ],
        'quizzes': [
            ('"Qila olmoq" means:', ['can', "can't", 'must', 'should'], 0),
            ('I ___ play the piano. (I don\'t know how)', ['can', "can't", 'do', 'am'], 1),
            ('She ___ speak three languages.', ['can', "can't", 'is', 'has'], 0),
        ],
    },
}