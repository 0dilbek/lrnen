"""Offline Qoraqalpoq/Uzbek content backfill.

This command intentionally has no network client and never sends course data to
an external service. It uses reviewed educational phrase dictionaries plus
deterministic normalization for the existing Qoraqalpoq vocabulary.
"""

import re

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Lesson, Vocabulary
from quiz.models import Exercise


# Course topics are repetitive. Long phrases are replaced first so smaller
# words cannot corrupt them. Quoted English grammar tokens stay unchanged.
TOPIC_PHRASES = {
    'Suggestions and explanations': 'Takliflar va tushuntirishlar',
    'General and specific things': 'Umumiy va aniq narsalar',
    'Activities and their results': 'Faoliyatlar va ularning natijalari',
    'Things that are always true': 'Doimo to‘g‘ri bo‘ladigan holatlar',
    'Things that might happen': 'Sodir bo‘lishi mumkin bo‘lgan voqealar',
    'What other people said': 'Boshqa odamlar nima degan',
    'What other people asked': 'Boshqa odamlar nima so‘ragan',
    'Someone, anyone, everyone': 'Kimdir, istalgan kishi, hamma',
    'Achievements and ambitions': 'Yutuqlar va maqsadlar',
    'Geographical features': 'Geografik obyektlar',
    'Separable phrasal verbs': 'Ajraladigan frazali fe’llar',
    'Reporting simple questions': 'Oddiy savollarni o‘zlashtirma gapda aytish',
    'Interrupted actions': 'Bo‘lib qo‘yilgan harakatlar',
    'Real and unreal situations': 'Haqiqiy va faraziy vaziyatlar',
    'Predictions and promises': 'Bashoratlar va va’dalar',
    'Plans and intentions': 'Rejalar va niyatlar',
    'Future possibilities': 'Kelajakdagi imkoniyatlar',
    'Future arrangements': 'Kelajak kelishuvlari',
    'Applying for a job': 'Ishga ariza topshirish',
    'Household chores': 'Uy yumushlari',
    'Numbers and statistics': 'Raqamlar va statistika',
    'Routine and free time': 'Kun tartibi va bo‘sh vaqt',
    'Vocabulary: Feelings and moods': 'Lug‘at: hislar va kayfiyatlar',
    'Vocabulary: Geographical features': 'Lug‘at: geografik obyektlar',
    'Vocabulary: Household chores': 'Lug‘at: uy yumushlari',
    'Vocabulary: Transportation': 'Lug‘at: transport',
    'Vocabulary: Entertainment': 'Lug‘at: ko‘ngilochar mashg‘ulotlar',
    'Vocabulary: The calendar': 'Lug‘at: taqvim',
    'Vocabulary: The body': 'Lug‘at: tana a’zolari',
    'Vocabulary: Weather': 'Lug‘at: ob-havo',
    'Vocabulary: Travel': 'Lug‘at: sayohat',
    'Vocabulary: Animals': 'Lug‘at: hayvonlar',
    'Vocabulary: Going out': 'Lug‘at: tashqariga chiqish',
    'Vocabulary: Tools': 'Lug‘at: asboblar',
    'Talking about yourself': 'O‘zingiz haqingizda gapirish',
    'Introducing yourself': 'O‘zingizni tanishtirish',
    'Saying hello and goodbye': 'Salomlashish va xayrlashish',
    'Talking about other people': 'Boshqa odamlar haqida gapirish',
    'Talking about your things': 'Buyumlaringiz haqida gapirish',
    'Talking about your job': 'Ishingiz haqida gapirish',
    'Talking about jobs': 'Kasblar haqida gapirish',
    'Talking about your town': 'Shahringiz haqida gapirish',
    'Talking about sports': 'Sport haqida gapirish',
    'Talking about routines': 'Kun tartibi haqida gapirish',
    'Talking about extremes': 'Eng yuqori darajalar haqida gapirish',
    'Talking about dates': 'Sanalar haqida gapirish',
    'Talking about the past': 'O‘tmish haqida gapirish',
    'Making conversation': 'Suhbat qurish',
    'Making comparisons': 'Taqqoslash',
    'Making choices': 'Tanlov qilish',
    'Making predictions': 'Bashorat qilish',
    'Making quick decisions': 'Tez qaror qabul qilish',
    'Making suggestions': 'Taklif bildirish',
    'Making deductions': 'Mantiqiy xulosa chiqarish',
    'Asking for agreement': 'Tasdiq so‘rash',
    'Asking about the past': 'O‘tmish haqida so‘rash',
    'Asking questions': 'Savol berish',
    'Answering questions': 'Savollarga javob berish',
    'Simple questions': 'Oddiy savollar',
    'Polite questions': 'Muloyim savollar',
    'Polite requests': 'Muloyim iltimoslar',
    'Types of questions': 'Savol turlari',
    'Question words': 'So‘roq so‘zlar',
    'Describing your day': 'Kuningizni tasvirlash',
    'Describing your week': 'Haftangizni tasvirlash',
    'Describing places': 'Joylarni tasvirlash',
    'Describing things': 'Narsalarni tasvirlash',
    'Describing actions': 'Harakatlarni tasvirlash',
    'Describing ability': 'Qobiliyatni tasvirlash',
    'Describing people': 'Odamlarni tasvirlash',
    'Describing a process': 'Jarayonni tasvirlash',
    'Where things are': 'Narsalar qayerda',
    'What things are for': 'Narsalar nima uchun kerak',
    'Things I have done': 'Men qilgan ishlar',
    'Things you have': 'Sizdagi narsalar',
    'The things I have': 'Mendagi narsalar',
    'What do you have?': 'Sizda nima bor?',
    'What I’m wearing': 'Men nima kiyganman',
    'Today I’m wearing…': 'Bugun men … kiyganman',
    'What’s happening?': 'Nima sodir bo‘lyapti?',
    'What’s going to happen?': 'Nima sodir bo‘ladi?',
    'What happened when?': 'Qachon nima sodir bo‘ldi?',
    'What was happening when?': 'Qachon nima sodir bo‘layotgan edi?',
    'What’s the matter?': 'Nima bo‘ldi?',
    'What’s the weather like?': 'Ob-havo qanday?',
    'How are you feeling?': 'O‘zingizni qanday his qilyapsiz?',
    "What you can and can't do": 'Nimalarni qila olishingiz va qila olmasligingiz',
    "Can and can't": 'Qila olish va qila olmaslik',
    'Negatives with "to be"': '“to be” bilan inkor gaplar',
    'More negatives': 'Yana inkor gaplar',
    'Using apostrophes': 'Apostroflardan foydalanish',
    'Using "a" and "the"': '“a” va “the”dan foydalanish',
    'Using large numbers': 'Katta sonlardan foydalanish',
    'Orders and directions': 'Buyruqlar va yo‘nalishlar',
    'Joining sentences': 'Gaplarni bog‘lash',
    'Prepositions of place': 'Joy predloglari',
    'Likes and dislikes': 'Yoqtirish va yoqtirmaslik',
    'Expressing preference': 'Afzallikni ifodalash',
    'Preferences': 'Afzalliklar',
    'Comparatives': 'Qiyosiy daraja',
    'Counting': 'Sanash', 'Measuring': 'O‘lchash', 'Prices': 'Narxlar',
    'At the shops': 'Do‘konlarda', 'Free time': 'Bo‘sh vaqt',
    'Hobbies and free time': 'Sevimli mashg‘ulotlar va bo‘sh vaqt',
    'Telling the time': 'Vaqtni aytish', 'Times and dates': 'Vaqt va sanalar',
    'Contact details': 'Aloqa ma’lumotlari', 'Everyday activities': 'Kundalik faoliyatlar',
    'Daily routines': 'Kun tartibi', 'Early years': 'Bolalik yillari',
    'Changing meaning': 'Ma’noni o‘zgartirish', 'Places I have been': 'Men bo‘lgan joylar',
    'Activities in progress': 'Davom etayotgan faoliyatlar',
    'My talents and skills': 'Iste’dod va ko‘nikmalarim',
    'Everyday problems': 'Kundalik muammolar', 'Myself, yourself': 'O‘zim, o‘zingiz',
    'Opinions and plans': 'Fikrlar va rejalar', 'Planning the future': 'Kelajakni rejalashtirish',
    'Possibility': 'Ehtimollik', 'Obligations': 'Majburiyatlar',
    'More phrasal verbs': 'Yana frazali fe’llar', 'Solving problems': 'Muammolarni hal qilish',
    'Planning activities': 'Faoliyatlarni rejalashtirish',
    'Unlikely situations': 'Ehtimoli kam vaziyatlar', 'Giving advice': 'Maslahat berish',
    'Being specific': 'Aniq ifodalash', 'Adding information': 'Ma’lumot qo‘shish',
    'Setting the scene': 'Vaziyatni tasvirlash', 'Events in the past': 'O‘tmishdagi voqealar',
    'Past events': 'O‘tgan voqealar', 'Past abilities': 'O‘tmishdagi qobiliyatlar',
    'Before and after': 'Oldin va keyin', 'First times': 'Birinchi marta',
    'Telling a story': 'Hikoya aytish', 'Telling things to people': 'Odamlarga ma’lumot aytish',
    'Telling people what to do': 'Odamlarga nima qilishni aytish',
    'Wishes and regrets': 'Istaklar va afsuslar', 'Events in your life': 'Hayotingizdagi voqealar',
    'Events in your year': 'Yilingizdagi voqealar', 'Eating out': 'Tashqarida ovqatlanish',
    'Irregular past verbs': 'Noto‘g‘ri o‘tgan zamon fe’llari', 'Types of verbs': 'Fe’l turlari',
    'Around the house': 'Uy atrofida', 'Entertainment': 'Ko‘ngilochar mashg‘ulotlar',
}


KAA_WORDS = [
    ('O‘zingiz', 'Ózińiz'), ('o‘zingiz', 'ózińiz'), ('O‘zim', 'Ózim'),
    ('haqida', 'haqqında'), ('gapirish', 'sóylew'), ('Savol', 'Soraw'),
    ('savol', 'soraw'), ('javob berish', 'juwap beriw'), ('tasvirlash', 'súwretlew'),
    ('foydalanish', 'paydalanıw'), ('narsalar', 'zatlar'), ('odamlar', 'adamlar'),
    ('joylar', 'orınlar'), ('harakatlar', 'háreketler'), ('qobiliyat', 'qábilet'),
    ('kelajak', 'keleshek'), ('o‘tmish', 'ótken dáwir'), ('O‘tgan', 'Ótken'),
    ('voqealar', 'waqıyalar'), ('faoliyatlar', 'iskerlikler'),
    ('rejalashtirish', 'rejelestiriw'), ('Rejalar', 'Rejeler'), ('rejalar', 'rejeler'),
    ('niyatlar', 'niyetler'), ('takliflar', 'usınıslar'),
    ('tushuntirishlar', 'túsindirmeler'), ('maslahat berish', 'másláhát beriw'),
    ('muammolarni hal qilish', 'mashqalalardı sheshiw'), ('Kundalik', 'Kúnlik'),
    ('kundalik', 'kúnlik'), ('bo‘sh vaqt', 'bos waqıt'), ('Kun tartibi', 'Kún tártibi'),
    ('uy', 'úy'), ('Uy', 'Úy'), ('ish', 'jumıs'), ('Ish', 'Jumıs'),
    ('kasblar', 'kásipler'), ('Lug‘at', 'Sózlik'), ('lug‘at', 'sózlik'),
    ('hislar', 'sezimler'), ('kayfiyatlar', 'keypiyatlar'), ('ob-havo', 'hawa rayı'),
    ('hayvonlar', 'haywanlar'), ('asboblar', 'ásbaplar'), ('tana a’zolari', 'dene músheleri'),
    ('qilish', 'etiw'), ('Qilish', 'Etiw'), ('berish', 'beriw'), ('aytish', 'aytıw'),
    ('yozish', 'jazıw'), ('o‘qish', 'oqıw'), ('bog‘lash', 'baylanıstırıw'),
    ('tanlov', 'tańlaw'), ('Tanlov', 'Tańlaw'), ('taqqoslash', 'salıstırıw'),
    ('Sanash', 'Sanaw'), ('O‘lchash', 'Ólshew'), ('Narxlar', 'Bahalar'),
    ('Do‘konlarda', 'Dúkanlarda'), ('Vaqt', 'Waqıt'), ('sanalar', 'sáneler'),
    ('qobiliyatlar', 'qábiletler'), ('ko‘nikmalarim', 'kónlikpelerim'),
    ('ma’lumot', 'maǵlıwmat'), ('Ma’lumot', 'Maǵlıwmat'), ('qo‘shish', 'qosıw'),
    ('Istaklar', 'Tilekler'), ('afsuslar', 'ókiniwler'), ('Ehtimollik', 'Itimallıq'),
    ('Majburiyatlar', 'Minetlemeler'), ('Oddiy', 'Ápiwayı'), ('Muloyim', 'Sıpayı'),
    ('eng yuqori darajalar', 'eń joqarı dárejeler'), ('Afzalliklar', 'Abzallıqlar'),
    ('Qiyosiy daraja', 'Salıstırıw dárejesi'),
    ('Ko‘ngilochar mashg‘ulotlar', 'Kewil ashar shınıǵıwlar'),
    ('haqingizda', 'haqqıńızda'), ('Haftangizni', 'Háptenizdi'),
    ('Kuningizni', 'Kúnińizdi'), ('Shahringiz', 'Qalańız'), ('Ishingiz', 'Jumısıńız'),
    ('Buyumlaringiz', 'Zatlarıńız'), ('Boshqa', 'Basqa'), ('boshqa', 'basqa'),
    ('qayerda', 'qay jerde'), ('Qayerda', 'Qay jerde'), ('nima', 'ne'), ('Nima', 'Ne'),
    ('Sizda', 'Sizde'), ('Sizdagi', 'Sizdegi'), ('Mendagi', 'Mendegi'),
    ('qanday', 'qalay'), ('Qanday', 'Qalay'),
    ('qila olishingiz', 'isley alıwıńız'), ('qila olmasligingiz', 'isley almawıńız'),
    ('inkor gaplar', 'biykarlaw gápleri'), ('gaplar', 'gápler'), ('Gaplar', 'Gápler'),
    ('So‘roq so‘zlar', 'Soraw sózler'), ('so‘zlar', 'sózler'), ('So‘zlar', 'Sózler'),
    ('fe’llar', 'feyiller'), ('Fe’l', 'Feyil'), ('sifatlar', 'kelbetlikler'),
    ('olmoshlar', 'almasıqlar'), ('iboralar', 'sóz dizbekleri'),
    ('yo‘nalishlar', 'baǵdarlar'), ('Buyruqlar', 'Buyrıq gápler'),
    ('predloglari', 'predlogları'), ('yoqtirish', 'jaqsı kóriw'),
    ('yoqtirmaslik', 'jaqsı kórmew'), ('afzallikni ifodalash', 'abzallıqtı bildiriw'),
    ('Bolalik yillari', 'Balalıq jılları'), ('Hikoya', 'Gúrriń'), ('hikoya', 'gúrriń'),
    ('Vaziyatni', 'Jaǵdaydı'), ('vaziyatlar', 'jaǵdaylar'),
    ('Haqiqiy', 'Haqıyqıy'), ('faraziy', 'boljawlı'), ('Bashorat', 'Boljaw'),
    ('bashorat', 'boljaw'), ('va’dalar', 'wádeler'), ('Yutuqlar', 'Jetiskenlikler'),
    ('maqsadlar', 'maqsetler'), ('imkoniyatlar', 'imkaniyatlar'),
    ('kelishuvlari', 'kelisimleri'), ('Mantiqiy xulosa chiqarish', 'Logikalıq juwmaq shıǵarıw'),
    ('Tasdiq so‘rash', 'Tastıyıqlawdı soraw'), ('Muloyim iltimoslar', 'Sıpayı ótinishler'),
    ('turlari', 'túrleri'), ('Aloqa', 'Baylanıs'), ('ma’noni', 'mánisti'),
    ('Men bo‘lgan', 'Men bolǵan'), ('Davom etayotgan', 'Dawam etip atırǵan'),
    ('Iste’dod', 'Talant'), ('muammolar', 'mashqalalar'), ('Fikrlar', 'Pikirler'),
    ('Aniq', 'Anıq'), ('ifodalash', 'bildiriw'), ('Odamlarga', 'Adamlarǵa'),
    ('odamlarga', 'adamlarǵa'), ('qobiliyatni', 'qábiletti'),
    ('katta sonlar', 'úlken sanlar'), ('Sanalar', 'Sáneler'), ('Vaqtni', 'Waqıttı'),
    ('Birinchi marta', 'Birinshi ret'), ('Oldin va keyin', 'Aldın hám keyin'),
    ('Tashqarida ovqatlanish', 'Sırtta awqatlanıw'), ('Hayotingizdagi', 'Ómirińizdegi'),
    ('Yilingizdagi', 'Jılıńızdaǵı'),
    ('O‘zingizni', 'Ózińizdi'), ('tanishtirish', 'tanıstırıw'),
    ('Suhbat qurish', 'Sáwbetlesiw'), ('Salomlashish', 'Sálemlesiw'),
    ('xayrlashish', 'xoshlasıw'), ('Kuningizni', 'Kúnińizdi'),
    ('Haftangizni', 'Háptenizdi'), ('Buyumlaringiz', 'Zatlarıńız'),
    ('Suhbat', 'Sáwbet'), ('qurish', 'qurıw'), ('o‘zgartirish', 'ózgertiw'),
    ('o‘rganish', 'úyreniw'), ('ta’riflash', 'súwretlew'), ('to‘ldirish', 'toltırıw'),
    ('tinglash', 'tıńlaw'), ('ovqatlanish', 'awqatlanıw'), ('kiyganman', 'kiygenmen'),
    ('sodir bo‘ladi', 'júz beredi'), ('sodir bo‘ldi', 'júz berdi'),
    ('sodir bo‘layotgan edi', 'júz berip atırǵan edi'),
]


INSTRUCTION_START = {
    'uz': [
        ('fill in the gaps to write each sentence three different ways', 'har bir gapni uch xil usulda yozish uchun bo‘sh joylarni to‘ldiring'),
        ('match the beginnings of the sentences to the correct endings', 'gap boshlarini to‘g‘ri yakunlar bilan birlashtiring'),
        ('respond out loud to', 'ovoz chiqarib javob bering:'),
        ('say the sentences out loud', 'gaplarni ovoz chiqarib ayting'),
        ('write answers to the questions', 'savollarga javoblarni yozing'),
        ('write a question to match each sentence', 'har bir gapga mos savol yozing'),
        ('rewrite the highlighted phrases', 'ajratib ko‘rsatilgan iboralarni qayta yozing'),
        ('rewrite the sentences', 'gaplarni qayta yozing'), ('rewrite each sentence', 'har bir gapni qayta yozing'),
        ('rewrite the statements', 'darak gaplarni qayta yozing'), ('rewrite each verb', 'har bir fe’lni qayta yozing'),
        ('rewrite the verbs', 'fe’llarni qayta yozing'), ('rewrite the words', 'so‘zlarni qayta yozing'),
        ('fill in the gaps', 'bo‘sh joylarni to‘ldiring'), ('fill in the blanks', 'bo‘sh joylarni to‘ldiring'),
        ('complete the sentences', 'gaplarni to‘ldiring'), ('complete each sentence', 'har bir gapni to‘ldiring'),
        ('complete the responses', 'javoblarni to‘ldiring'), ('complete the questions', 'savollarni to‘ldiring'),
        ('correct the errors', 'xatolarni tuzating'), ('correct the error', 'xatoni tuzating'),
        ('cross out the incorrect words', 'noto‘g‘ri so‘zlarni chizing'),
        ('cross out the incorrect word', 'noto‘g‘ri so‘zni chizing'),
        ('cross out the incorrect spellings', 'noto‘g‘ri yozilgan so‘zlarni chizing'),
        ('choose the correct words', 'to‘g‘ri so‘zlarni tanlang'), ('choose the correct word', 'to‘g‘ri so‘zni tanlang'),
        ('choose the correct sentence', 'to‘g‘ri gapni tanlang'), ('choose the correct statement', 'to‘g‘ri fikrni tanlang'),
        ('choose the correct', 'to‘g‘risini tanlang:'), ('listen to the audio and', 'audioni tinglang va'),
        ('listen and', 'tinglang va'), ('read the article and', 'maqolani o‘qing va'),
        ('read the blog and', 'blogni o‘qing va'), ('read the email and', 'elektron xatni o‘qing va'),
        ('read the note and', 'qaydni o‘qing va'), ('read the story and', 'hikoyani o‘qing va'),
        ('read the', 'o‘qing:'), ('answer the questions', 'savollarga javob bering'),
        ('match the beginnings', 'gap boshlarini mos yakunlar bilan birlashtiring'),
        ('match the questions', 'savollarni javoblari bilan moslashtiring'),
        ('match the definitions', 'ta’riflarni moslashtiring'), ('match the phrases', 'iboralarni moslashtiring'),
        ('match the sentences', 'gaplarni moslashtiring'), ('match the', 'moslashtiring:'),
        ('mark the sentences', 'gaplarni belgilang'), ('mark the sentence', 'gapni belgilang'),
        ('mark the correct', 'to‘g‘risini belgilang'), ('mark the best reply', 'eng yaxshi javobni belgilang'),
        ('put the verbs', 'fe’llarni qo‘ying'), ('add question tags', 'question tag qo‘shing'),
        ('describe the people', 'odamlarni tasvirlang'), ('turn the', 'o‘zgartiring:'),
        ('write the', 'yozing:'), ('write each', 'har birini yozing:'), ('respond to', 'javob bering:'),
    ],
    'kaa': [
        ('fill in the gaps to write each sentence three different ways', 'hár gápti úsh túrli usılda jazıw ushın bos orınlardı toltırıń'),
        ('match the beginnings of the sentences to the correct endings', 'gáp basların durıs juwmaqlar menen sáykeslestiń'),
        ('respond out loud to', 'dawıslap juwap beriń:'),
        ('say the sentences out loud', 'gáplerdi dawıslap aytıń'),
        ('write answers to the questions', 'sorawlarǵa juwaplardı jazıń'),
        ('write a question to match each sentence', 'hár gáptıń sáykes sorawın jazıń'),
        ('rewrite the highlighted phrases', 'belgilengen sóz dizbeklerin qayta jazıń'),
        ('rewrite the sentences', 'gáplerdi qayta jazıń'), ('rewrite each sentence', 'hár gápti qayta jazıń'),
        ('rewrite the statements', 'xabar gáplerdi qayta jazıń'), ('rewrite each verb', 'hár feyildi qayta jazıń'),
        ('rewrite the verbs', 'feyillerdi qayta jazıń'), ('rewrite the words', 'sózlerdi qayta jazıń'),
        ('fill in the gaps', 'bos orınlardı toltırıń'), ('fill in the blanks', 'bos orınlardı toltırıń'),
        ('complete the sentences', 'gáplerdi toltırıń'), ('complete each sentence', 'hár gápti toltırıń'),
        ('complete the responses', 'juwaplardı toltırıń'), ('complete the questions', 'sorawlardı toltırıń'),
        ('correct the errors', 'qátelerdi dúzetiń'), ('correct the error', 'qáteni dúzetiń'),
        ('cross out the incorrect words', 'nadurıs sózlerdi sızıń'),
        ('cross out the incorrect word', 'nadurıs sózdi sızıń'),
        ('cross out the incorrect spellings', 'nadurıs jazılǵan sózlerdi sızıń'),
        ('choose the correct words', 'durıs sózlerdi tańlań'), ('choose the correct word', 'durıs sózdi tańlań'),
        ('choose the correct sentence', 'durıs gápti tańlań'), ('choose the correct statement', 'durıs pikirdi tańlań'),
        ('choose the correct', 'durısın tańlań:'), ('listen to the audio and', 'audionı tıńlań hám'),
        ('listen and', 'tıńlań hám'), ('read the article and', 'maqalanı oqıń hám'),
        ('read the blog and', 'blogtı oqıń hám'), ('read the email and', 'elektron xattı oqıń hám'),
        ('read the note and', 'jazbanı oqıń hám'), ('read the story and', 'gúrrińdi oqıń hám'),
        ('read the', 'oqıń:'), ('answer the questions', 'sorawlarǵa juwap beriń'),
        ('match the beginnings', 'gáp basların durıs juwmaqları menen sáykeslestiń'),
        ('match the questions', 'sorawlardı juwapları menen sáykeslestiń'),
        ('match the definitions', 'anıqlamalardı sáykeslestiń'),
        ('match the phrases', 'sóz dizbeklerin sáykeslestiń'), ('match the sentences', 'gáplerdi sáykeslestiń'),
        ('match the', 'sáykeslestiń:'), ('mark the sentences', 'gáplerdi belgileń'),
        ('mark the sentence', 'gápti belgileń'), ('mark the correct', 'durısın belgileń'),
        ('mark the best reply', 'eń jaqsı juwaptı belgileń'), ('put the verbs', 'feyillerdi qoyıń'),
        ('add question tags', 'question tag qosıń'), ('describe the people', 'adamlardı súwretleń'),
        ('turn the', 'ózgertiń:'), ('write the', 'jazıń:'), ('write each', 'hár birin jazıń:'),
        ('respond to', 'juwap beriń:'),
    ],
}


# A small set of recurring instructions needs sentence-level translation.
# Keeping these here avoids unnatural word order that token replacement cannot
# solve while still keeping the whole backfill deterministic and offline.
INSTRUCTION_EXACT = {
    'uz': {
        'rewrite the phrases using an apostrophe with "s"': 'Iboralarni apostrof va “s” yordamida qayta yozing',
        'rewrite each verb as an imperative': 'Har bir fe’lni buyruq gap shaklida qayta yozing',
        'mark the sentences that are correct': 'To‘g‘ri gaplarni belgilang',
        'mark the sentence that is correct': 'To‘g‘ri gapni belgilang',
        'mark the question that is correct': 'To‘g‘ri savolni belgilang',
        'mark the indirect questions that are correct': 'To‘g‘ri bilvosita savollarni belgilang',
        'complete with how many or how much': '“How many” yoki “how much” bilan to‘ldiring',
        'mark whether each sentence is imperative or present simple': 'Har bir gap buyruq gap yoki Present Simple ekanini belgilang',
        'fill in the gaps by making either an "-ed" or "-ing" adjective from the verbs in brackets': 'Qavsdagi fe’llardan “-ed” yoki “-ing” sifat yasab, bo‘sh joylarni to‘ldiring',
        'read the email and mark whether each sentence is a prediction, offer, promise, or decision': 'Elektron xatni o‘qing va har bir gap bashorat, taklif, va’da yoki qaror ekanini belgilang',
        'read the email on page 69 and answer the questions': '69-sahifadagi elektron xatni o‘qing va savollarga javob bering',
        "fill in the gaps to say what each person hasn't done and what they want to do": 'Har bir kishi nima qilmagani va nima qilishni xohlashini aytish uchun bo‘sh joylarni to‘ldiring',
        'write out what each image shows': 'Har bir rasmda nima tasvirlanganini yozing',
        'rewrite the highlighted phrases using a pronoun and the contracted form of the verb': 'Ajratilgan iboralarni olmosh va fe’lning qisqartirilgan shakli yordamida qayta yozing',
        'complete each sentence to make it negative': 'Har bir gapni inkor shaklda to‘ldiring',
        'look at the image and say the sentences out loud, filling in the gaps': 'Rasmga qarang, bo‘sh joylarni to‘ldirib, gaplarni ovoz chiqarib ayting',
    },
    'kaa': {
        'rewrite the phrases using an apostrophe with "s"': 'Sóz dizbeklerin apostrof hám “s” járdeminde qayta jazıń',
        'rewrite each verb as an imperative': 'Hár bir feyildi buyrıq gáp túrinde qayta jazıń',
        'mark the sentences that are correct': 'Durıs gáplerdi belgileń',
        'mark the sentence that is correct': 'Durıs gápti belgileń',
        'mark the question that is correct': 'Durıs sorawdı belgileń',
        'mark the indirect questions that are correct': 'Durıs janapay sorawlardı belgileń',
        'complete with how many or how much': '“How many” yamasa “how much” penen toltırıń',
        'mark whether each sentence is imperative or present simple': 'Hár bir gáp buyrıq gáp yamasa Present Simple ekenin belgileń',
        'fill in the gaps by making either an "-ed" or "-ing" adjective from the verbs in brackets': 'Qawsırmadaǵı feyillerden “-ed” yamasa “-ing” kelbetlik jasap, bos orınlardı toltırıń',
        'read the email and mark whether each sentence is a prediction, offer, promise, or decision': 'Elektron xattı oqıń hám hár bir gáp boljaw, usınıs, wáde yamasa qarar ekenin belgileń',
        'read the email on page 69 and answer the questions': '69-bettegi elektron xattı oqıń hám sorawlarǵa juwap beriń',
        "fill in the gaps to say what each person hasn't done and what they want to do": 'Hár bir adam ne islemegenin hám ne islewin qáleytuǵının aytıw ushın bos orınlardı toltırıń',
        'write out what each image shows': 'Hár bir súwrette ne kórsetilgenin jazıń',
        'rewrite the highlighted phrases using a pronoun and the contracted form of the verb': 'Belgilengen sóz dizbeklerin almasıq hám feyildiń qısqartılǵan túri járdeminde qayta jazıń',
        'complete each sentence to make it negative': 'Hár bir gápti biykarlaw túrinde toltırıń',
        'look at the image and say the sentences out loud, filling in the gaps': 'Súwretke qarań, bos orınlardı toltırıp, gáplerdi dawıslap aytıń',
    },
}


TAIL_WORDS = {
    'uz': [
        ('using the words in the panel', 'paneldagi so‘zlardan foydalanib'),
        ('using the correct possessive adjectives', 'to‘g‘ri egalik sifatlaridan foydalanib'),
        ('using an apostrophe', 'apostrofdan foydalanib'),
        ('with an apostrophe', 'apostrof bilan'), ('by putting', 'qo‘yib'),
        ('in their', 'ularning'), ('travel vocabulary', 'sayohat lug‘ati'),
        ('filling in the gaps', 'bo‘sh joylarni to‘ldirib'),
        ('fill in the gaps', 'bo‘sh joylarni to‘ldiring'),
        ('using the phrases in the panel', 'paneldagi iboralardan foydalanib'),
        ('using the verbs in brackets', 'qavsdagi fe’llardan foydalanib'),
        ('putting the words in the correct order', 'so‘zlarni to‘g‘ri tartibga qo‘yib'),
        ('putting the verbs in the correct tense', 'fe’llarni to‘g‘ri zamonga qo‘yib'),
        ('putting the verbs in the correct form', 'fe’llarni to‘g‘ri shaklga qo‘yib'),
        ('in the correct tenses', 'to‘g‘ri zamonlarda'), ('in the correct tense', 'to‘g‘ri zamonda'),
        ('in the correct form', 'to‘g‘ri shaklda'), ('in each sentence', 'har bir gapda'),
        ('to complete the sentences', 'gaplarni to‘ldirish uchun'),
        ('to complete each sentence', 'har bir gapni to‘ldirish uchun'),
        ('to complete the questions', 'savollarni to‘ldirish uchun'),
        ('and answer the questions', 'va savollarga javob bering'),
        ('as full sentences', 'to‘liq gaplar bilan'), ('correcting the errors', 'xatolarni tuzatib'),
        ('the correct endings', 'to‘g‘ri yakunlar'), ('correct endings', 'to‘g‘ri yakunlar'),
        ('reported speech', 'o‘zlashtirma gap'), ('reported questions', 'o‘zlashtirma savollar'),
        ('three different ways', 'uch xil usulda'), ('in its other form', 'boshqa shaklida'),
        ('in its contracted form', 'qisqartirilgan shaklida'),
        ('to make negative sentences', 'inkor gaplar tuzish uchun'),
        ('number as a figure', 'sonni raqam bilan'), ('numbers as figures', 'sonlarni raqam bilan'),
        ('with the correct answers', 'to‘g‘ri javoblar bilan'), ('the correct words', 'to‘g‘ri so‘zlar'),
        ('the correct word', 'to‘g‘ri so‘z'), ('the correct forms', 'to‘g‘ri shakllar'),
        ('the questions', 'savollar'), ('the sentences', 'gaplar'), ('the statements', 'darak gaplar'),
        ('the words', 'so‘zlar'), ('true or false', 'to‘g‘ri yoki noto‘g‘ri'),
        ('present continuous', 'Present Continuous'), ('present perfect', 'Present Perfect'),
        ('present simple', 'Present Simple'), ('past continuous', 'Past Continuous'),
        ('past perfect', 'Past Perfect'), ('past simple', 'Past Simple'), ('future tense', 'kelasi zamon'),
        ('negative form', 'inkor shakl'), ('comparative form', 'qiyosiy daraja'),
        ('superlative form', 'orttirma daraja'), ('questions', 'savollar'), ('sentences', 'gaplar'),
        ('words', 'so‘zlar'), ('verbs', 'fe’llar'), ('adjectives', 'sifatlar'),
        ('pronouns', 'olmoshlar'), ('prepositions', 'predloglar'), ('phrases', 'iboralar'),
        ('answer the questions', 'savollarga javob bering'), ('answer', 'javob bering'),
        ('choose', 'tanlang'), ('complete', 'to‘ldiring'), ('mark', 'belgilang'),
        ('match', 'moslashtiring'), ('fill', 'to‘ldiring'), ('write', 'yozing'),
        ('read', 'o‘qing'), ('listen', 'tinglang'),
        ('putting', 'qo‘yib'), ('gaps', 'bo‘sh joylar'), ('question', 'savol'),
        ('sentence', 'gap'), ('statements', 'darak gaplar'), ('statement', 'darak gap'),
        ('endings', 'yakunlar'), ('hear', 'eshitasiz'), ('pairs', 'juftlar'),
        ('postcard', 'otkritka'), ('times', 'vaqtlar'), ('numbers', 'sonlar'),
        ('number', 'son'), ('figure', 'raqam'), ('other', 'boshqa'),
        ('pictures', 'rasmlar'), ('objects', 'buyumlar'), ('owners', 'egalari'),
        ('activities', 'faoliyatlar'), ('activity', 'faoliyat'), ('name', 'ism'),
        ('based on', 'asosida'), ('each', 'har bir'), ('with', 'bilan'),
        ('from', 'dan'), ('into', 'ga'), ('through', 'orqali'), ('without', 'siz'),
        ('make', 'tuzing'), ('say', 'ayting'), ('to', 'uchun'), ('of', 'ning'),
        ('and', 'va'), ('or', 'yoki'), ('by', 'orqali'),
        ('using', 'foydalanib'), ('the correct', 'to‘g‘ri'),
        ('that matches', 'mos keladigan'), ('their', 'ularning'),
        ('answers', 'javoblar'), ('you', 'siz'), ('forms', 'shakllar'),
        ('form', 'shakl'), ('word', 'so‘z'), ('verb', 'fe’l'), ('about', 'haqida'),
        ('direct', 'bevosita'), ('blank', 'bo‘sh joy'), ('short', 'qisqa'),
        ('vocabulary', 'lug‘at'), ('whether', 'ekanligini'), ('these', 'bu'),
        ('adverbs', 'ravishlar'), ('adverb', 'ravish'), ('places', 'joylar'),
        ('phrasal', 'frazali'), ('highlighted', 'ajratilgan'), ('adjective', 'sifat'),
        ('tense', 'zamon'), ('pronoun', 'olmosh'), ('advertisements', 'e’lonlar'),
        ('names', 'ismlar'), ('person', 'shaxs'), ('brackets', 'qavslar'),
        ('together', 'birgalikda'), ('possessive', 'egalik'), ('imperative', 'buyruq gap'),
        ('picture', 'rasm'), ('they', 'ular'), ('comparatives', 'qiyosiy darajalar'),
        ('preference', 'afzallik'), ('errors', 'xatolar'), ('same', 'bir xil'),
        ('mean', 'anglatadi'), ('passive', 'majhul nisbat'), ('indirect', 'bilvosita'),
        ('changing', 'o‘zgartirib'), ('rest', 'qolgan qismi'), ('advice', 'maslahat'),
        ('animal', 'hayvon'), ('scrambled', 'aralashtirilgan'), ('versions', 'variantlar'),
        ('description', 'tavsif'), ('loud', 'ovoz chiqarib'), ('figures', 'raqamlar'),
        ('opposite', 'teskarisi'), ('adding', 'qo‘shib'), ('page', 'sahifa'),
        ('determiners', 'aniqlovchilar'), ('instructions', 'ko‘rsatmalar'),
        ('image', 'rasm'), ('gerunds', 'gerundiylar'), ('correct', 'to‘g‘ri'),
        ('rewrite', 'qayta yozing'), ('panel', 'panel'), ('for', 'uchun'),
        ('as', 'sifatida'), ('in', 'da'), ('the', ''),
    ],
    'kaa': [
        ('fill in the gaps to write each sentence three different ways', 'hár gápti úsh túrli usılda jazıw ushın bos orınlardı toltırıń'),
        ('match the beginnings of the sentences to the correct endings', 'gáp basların durıs juwmaqlar menen sáykeslestiń'),
        ('using the words in the panel', 'paneldegi sózlerden paydalanıp'),
        ('using the correct possessive adjectives', 'durıs iyelik kelbetliklerinen paydalanıp'),
        ('using an apostrophe', 'apostroftan paydalanıp'),
        ('with an apostrophe', 'apostrof menen'), ('by putting', 'qoyıp'),
        ('in their', 'olardıń'), ('travel vocabulary', 'sayaxat sózligi'),
        ('filling in the gaps', 'bos orınlardı toltırıp'),
        ('fill in the gaps', 'bos orınlardı toltırıń'),
        ('using the phrases in the panel', 'paneldegi sóz dizbeklerinen paydalanıp'),
        ('using the verbs in brackets', 'qawsırmadaǵı feyillerden paydalanıp'),
        ('putting the words in the correct order', 'sózlerdi durıs tártipke qoyıp'),
        ('putting the verbs in the correct tense', 'feyillerdi durıs máhálge qoyıp'),
        ('putting the verbs in the correct form', 'feyillerdi durıs túrge qoyıp'),
        ('in the correct tenses', 'durıs máhállerde'), ('in the correct tense', 'durıs máhálde'),
        ('in the correct form', 'durıs túrde'), ('in each sentence', 'hár gáptiń ishinde'),
        ('to complete the sentences', 'gáplerdi toltırıw ushın'),
        ('to complete each sentence', 'hár gápti toltırıw ushın'),
        ('to complete the questions', 'sorawlardı toltırıw ushın'),
        ('and answer the questions', 'hám sorawlarǵa juwap beriń'),
        ('as full sentences', 'tolıq gápler menen'), ('correcting the errors', 'qátelerdi dúzetip'),
        ('the correct endings', 'durıs juwmaqlar'), ('correct endings', 'durıs juwmaqlar'),
        ('reported speech', 'ózlestirme gáp'), ('reported questions', 'ózlestirme sorawlar'),
        ('three different ways', 'úsh túrli usılda'), ('in its other form', 'basqa túrinde'),
        ('in its contracted form', 'qısqartılǵan túrinde'),
        ('to make negative sentences', 'biykarlaw gáplerin dúziw ushın'),
        ('number as a figure', 'sandı cifra menen'), ('numbers as figures', 'sanlardı cifra menen'),
        ('with the correct answers', 'durıs juwaplar menen'), ('the correct words', 'durıs sózler'),
        ('the correct word', 'durıs sóz'), ('the correct forms', 'durıs túrler'),
        ('the questions', 'sorawlar'), ('the sentences', 'gápler'), ('the statements', 'xabar gápler'),
        ('the words', 'sózler'), ('true or false', 'durıs yamasa nadurıs'),
        ('present continuous', 'Present Continuous'), ('present perfect', 'Present Perfect'),
        ('present simple', 'Present Simple'), ('past continuous', 'Past Continuous'),
        ('past perfect', 'Past Perfect'), ('past simple', 'Past Simple'), ('future tense', 'keler máhál'),
        ('negative form', 'biykarlaw túri'), ('comparative form', 'salıstırıw dárejesi'),
        ('superlative form', 'asırma dáreje'), ('questions', 'sorawlar'), ('sentences', 'gápler'),
        ('words', 'sózler'), ('verbs', 'feyiller'), ('adjectives', 'kelbetlikler'),
        ('pronouns', 'almasıqlar'), ('prepositions', 'predloglar'), ('phrases', 'sóz dizbekleri'),
        ('answer the questions', 'sorawlarǵa juwap beriń'), ('answer', 'juwap beriń'),
        ('choose', 'tańlań'), ('complete', 'toltırıń'), ('mark', 'belgileń'),
        ('match', 'sáykeslestiń'), ('fill', 'toltırıń'), ('write', 'jazıń'),
        ('read', 'oqıń'), ('listen', 'tıńlań'),
        ('putting', 'qoyıp'), ('gaps', 'bos orınlar'), ('question', 'soraw'),
        ('sentence', 'gáp'), ('statements', 'xabar gápler'), ('statement', 'xabar gáp'),
        ('endings', 'juwmaqlar'), ('hear', 'esitesiz'), ('pairs', 'juplar'),
        ('postcard', 'otkritka'), ('times', 'waqıtlar'), ('numbers', 'sanlar'),
        ('number', 'san'), ('figure', 'cifra'), ('other', 'basqa'),
        ('pictures', 'súwretler'), ('objects', 'zatlar'), ('owners', 'iyeleri'),
        ('activities', 'iskerlikler'), ('activity', 'iskerlik'), ('name', 'at'),
        ('based on', 'tiykarında'), ('each', 'hár bir'), ('with', 'menen'),
        ('from', 'dan'), ('into', 'ǵa'), ('through', 'arqalı'), ('without', 'sız'),
        ('make', 'dúziń'), ('say', 'aytıń'), ('to', 'ushın'), ('of', 'dıń'),
        ('and', 'hám'), ('or', 'yamasa'), ('by', 'arqalı'),
        ('using', 'paydalanıp'), ('the correct', 'durıs'),
        ('that matches', 'sáykes keletuǵın'), ('their', 'olardıń'),
        ('answers', 'juwaplar'), ('you', 'siz'), ('forms', 'túrler'),
        ('form', 'túr'), ('word', 'sóz'), ('verb', 'feyil'), ('about', 'haqqında'),
        ('direct', 'tuwrıdan-tuwrı'), ('blank', 'bos orın'), ('short', 'qısqa'),
        ('vocabulary', 'sózlik'), ('whether', 'ekenin'), ('these', 'bul'),
        ('adverbs', 'ráwishler'), ('adverb', 'ráwish'), ('places', 'orınlar'),
        ('phrasal', 'frazalı'), ('highlighted', 'belgilengen'), ('adjective', 'kelbetlik'),
        ('tense', 'máhál'), ('pronoun', 'almasıq'), ('advertisements', 'járiyamalar'),
        ('names', 'atlar'), ('person', 'adam'), ('brackets', 'qawsırmalar'),
        ('together', 'birgelikte'), ('possessive', 'iyelik'), ('imperative', 'buyrıq gáp'),
        ('picture', 'súwret'), ('they', 'olar'), ('comparatives', 'salıstırıw dárejeleri'),
        ('preference', 'abzallıq'), ('errors', 'qáteler'), ('same', 'birdey'),
        ('mean', 'bildiredi'), ('passive', 'ırıqsız dáreje'), ('indirect', 'janapay'),
        ('changing', 'ózgertip'), ('rest', 'qalǵan bóligi'), ('advice', 'másláhát'),
        ('animal', 'haywan'), ('scrambled', 'aralastırılǵan'), ('versions', 'variantlar'),
        ('description', 'súwretleme'), ('loud', 'dawıslap'), ('figures', 'cifralar'),
        ('opposite', 'kerisi'), ('adding', 'qosıp'), ('page', 'bet'),
        ('determiners', 'anıqlawshılar'), ('instructions', 'kórsetpeler'),
        ('image', 'súwret'), ('gerunds', 'gerundiyler'), ('correct', 'durıs'),
        ('rewrite', 'qayta jazıń'), ('panel', 'panel'), ('for', 'ushın'),
        ('as', 'sıpatında'), ('in', 'de'), ('the', ''),
    ],
}


VOCAB_UZ = {
    'ability': 'qobiliyat', 'able to': 'qila olmoq', 'act': 'harakat qilmoq', 'add': 'qo‘shmoq',
    'all day': 'kun bo‘yi', 'around the work': 'dunyo bo‘ylab', 'attic': 'chordoq',
    'audience': 'tomoshabinlar', 'backyard': 'orqa hovli', 'bake': 'pishirmoq',
    'band/group': 'guruh', 'bar': 'bo‘lak', 'baseball hat': 'beysbol kepkasi',
    'bathroom': 'yuvinish xonasi', 'beach': 'sohil', 'beautifully': 'chiroyli tarzda',
    'because': 'chunki', 'bed': 'karavot', 'behind': 'orqasida', 'both': 'ikkalasi ham',
    'bowl': 'kosa', 'bread': 'non', 'breakfast': 'nonushta', 'building': 'bino',
    'called': 'deb atalgan', 'cannot': 'qila olmaslik', 'carefully': 'ehtiyotkorlik bilan',
    'carry': 'ko‘tarib yurmoq', 'castle': 'qal’a', 'casual': 'norasmiy', 'catch': 'ushlab olmoq',
    'cereal': 'donli nonushta', 'church': 'cherkov', 'classical music': 'klassik musiqa',
    'clean': 'tozalamoq', 'climb': 'tirmashmoq', 'clumsy': 'no‘noq', 'coin': 'tanga',
    'cold': 'sovuq', 'color': 'rang', 'cook': 'pishirmoq', 'cost': 'narxi turmoq',
    'count': 'sanamoq', 'country': 'mamlakat', 'countryside': 'qishloq joy',
    'customer': 'xaridor', 'cycle to work': 'ishga velosipedda bormoq',
    'daily routine': 'kun tartibi', 'dance': 'raqsga tushmoq', 'dancer': 'raqqos',
    'deadline': 'oxirgi muddat', 'dictionary': 'lug‘at', 'dining room': 'ovqatlanish xonasi',
    'do (homework)': 'uy vazifasini bajarmoq', 'do puzzles': 'boshqotirma yechmoq',
    'do the gardening': 'bog‘dorchilik qilmoq', 'doctor': 'shifokor', 'doll': 'qo‘g‘irchoq',
    'downstairs': 'pastki qavatda', 'drinks': 'ichimliklar', 'drive': 'haydamoq',
    'during': 'davomida', 'early': 'erta', 'easily': 'osonlik bilan', 'egg': 'tuxum',
    'enough': 'yetarli', 'everyday things': 'kundalik narsalar', 'extra large': 'juda katta',
    'extra small': 'juda kichik', 'far': 'uzoq', 'fire fighter': 'o‘t o‘chiruvchi',
    'firefighter': 'o‘t o‘chiruvchi', 'floor': 'pol/qavat', 'fly': 'uchmoq', 'food': 'ovqat',
    'free time': 'bo‘sh vaqt', 'fruit': 'meva', 'full-time': 'to‘liq stavka',
    'fun': 'qiziqarli', 'get a degree': 'diplom olmoq', 'get there': 'u yerga yetib bormoq',
    'go bird watching': 'qushlarni kuzatishga bormoq',
    'go camping': 'chodirli dam olishga bormoq', 'go cycling': 'velosiped haydashga bormoq',
    'go on vacation go on holiday': 'ta’tilga chiqmoq',
    'go out for a meal': 'tashqarida ovqatlanmoq', 'go past': 'yonidan o‘tmoq',
    'go sightseeing': 'diqqatga sazovor joylarni tomosha qilmoq',
    'go straight (ahead)': 'to‘g‘riga yuring', 'go surfing': 'serfingga bormoq',
    'grass': 'o‘t', 'grey/gray': 'kulrang', 'hairbrush': 'soch tarog‘i', 'hard': 'qiyin',
    'hate': 'yomon ko‘rmoq', 'he': 'u (erkak)', 'her': 'uning (ayol)', 'here': 'shu yerda',
    'hers': 'uniki (ayol)', 'high': 'baland', 'his': 'uning (erkak)', 'hit': 'urmoq',
    'horrible': 'dahshatli', 'hospital': 'shifoxona', 'how many': 'nechta',
    'how much': 'qancha', 'in a store': 'do‘konda', 'in an office': 'ofisda',
    'in the backyard': 'orqa hovlida', 'in the kitchen': 'oshxonada', 'inside': 'ichkarida',
    'introduce': 'tanishtirmoq', 'it': 'u (narsa)', 'its': 'uning (narsa)', 'job': 'ish',
    'juice': 'sharbat', 'jump': 'sakramoq', 'keyboard': 'klavishli musiqa asbobi',
    'kick': 'tepmoq', 'kitchen': 'oshxona', 'large': 'katta', 'later': 'keyinroq',
    'learn': 'o‘rganmoq', 'letter': 'harf', 'library': 'kutubxona', 'lift': 'ko‘tarmoq',
    'lion': 'arslon', 'listen': 'tinglamoq', 'listen to music': 'musiqa tinglamoq',
    'listen to the audio': 'audioni tinglamoq', 'living room': 'mehmonxona',
    'long sleeves': 'uzun yeng', 'loudly': 'baland ovozda', 'lunch': 'tushlik',
    'make (a snowman)': 'qorbobo yasamoq', 'meet': 'uchrashmoq',
    'meet friends': 'do‘stlar bilan uchrashmoq', 'mine': 'meniki',
    'move': 'harakatlanmoq; ko‘chmoq', 'musical instruments': 'musiqa asboblari',
    'my': 'mening', 'name/first name': 'ism', 'nationality': 'millat', 'near': 'yaqin',
    'near here': 'shu yerga yaqin', 'never': 'hech qachon', 'next to': 'yonida',
    'next year': 'keyingi yil', 'noon': 'tush payti', 'nurse': 'hamshira',
    'on the corner': 'burchakda', 'on the right': 'o‘ngda', 'on vacation': 'ta’tilda',
    'open': 'ochmoq', 'opposite': 'qarama-qarshi', 'other': 'boshqa', 'our': 'bizning',
    'ours': 'bizniki', 'outside': 'tashqarida', 'own': 'egalik qilmoq', 'people': 'odamlar',
    'physical education': 'jismoniy tarbiya', 'pilot': 'uchuvchi', 'place': 'joy',
    'play a musical instrument': 'musiqa asbobini chalmoq',
    'play board games': 'stol o‘yinlarini o‘ynamoq', 'play cards': 'karta o‘ynamoq',
    'play computer games play video games': 'kompyuter o‘yinlarini o‘ynamoq',
    'play sport do exercise': 'sport bilan shug‘ullanmoq', 'play the trumpet': 'karnay chalmoq',
    'player': 'o‘yinchi', 'practice/practise': 'mashq qilmoq', 'pronouns': 'olmoshlar',
    'pupil': 'o‘quvchi', 'question words': 'so‘roq so‘zlar', 'quiet': 'tinch',
    'quietly': 'sekin ovozda', 'raincoat': 'yomg‘irpo‘sh', 'read': 'o‘qimoq',
    'read the text': 'matnni o‘qimoq', 'receptionist': 'qabulxona xodimi',
    'remember': 'eslab qolmoq', 'ride': 'minmoq', 'road': 'yo‘l', 'roof': 'tom',
    'sailing': 'qayiqda suzish', 'sand': 'qum', 'school': 'maktab', 'science': 'fan',
    'scientist': 'olim', 'seafood': 'dengiz mahsulotlari', 'see': 'ko‘rmoq',
    'see a play': 'pyesa tomosha qilmoq', 'she': 'u (ayol)', 'shoes': 'oyoq kiyim',
    'shop': 'do‘kon', 'short sleeves': 'kalta yeng', 'shout': 'baqirmoq',
    'sing (a song)': 'qo‘shiq aytmoq', 'singer': 'qo‘shiqchi', 'sit': 'o‘tirmoq',
    'small': 'kichik', 'slowly': 'sekin', 'smart': 'aqlli; bashang',
    'sometimes': 'ba’zan', 'son-in-law': 'kuyov', 'song': 'qo‘shiq', 'soon': 'tez orada',
    'speak': 'gapirmoq', 'speak english': 'inglizcha gapirmoq', 'spell': 'harflab aytmoq',
    'stairs': 'zina', 'stand up': 'turmoq', 'step': 'o‘gay', 'stop': 'to‘xtamoq',
    'street': 'ko‘cha', 'study room': 'o‘qish xonasi', 'substract': 'ayirmoq',
    'sugar': 'shakar', 'take an exam': 'imtihon topshirmoq', 'take care': 'o‘zingizni asrang',
    'take photos': 'suratga olmoq', 'talk': 'gapirmoq',
    'talk ( to somebody)': 'kim bilandir gaplashmoq', 'talk about': 'haqida gapirmoq',
    'teacher': 'o‘qituvchi', 'tell': 'aytmoq', 'temple': 'ibodatxona',
    'their': 'ularning', 'theirs': 'ularniki', 'there': 'u yerda', 'these': 'bular',
    'they': 'ular', 'think': 'o‘ylamoq', 'this': 'bu', 'those': 'ular', 'throw': 'uloqtirmoq',
    'today': 'bugun', 'together': 'birgalikda', 'tonight': 'bugun kechqurun',
    'too many too much': 'juda ko‘p', 'town': 'shaharcha', 'town hall': 'shahar hokimligi',
    'try': 'urinmoq', 'unable to': 'qila olmaslik', 'understand': 'tushunmoq',
    'until': 'gacha', 'upstairs': 'yuqori qavatda', 'usually': 'odatda',
    'vegetables': 'sabzavotlar', 'village': 'qishloq', 'visit': 'tashrif buyurmoq',
    'visit a museum/art gallery': 'muzey/san’at galereyasiga bormoq',
    'waiter waitress (woman)': 'ofitsiant', 'walk': 'piyoda yurmoq',
    'walk/hike': 'piyoda sayr qilmoq', 'want': 'xohlamoq', 'watch': 'qo‘l soati',
    'watch television (tv)': 'televizor ko‘rmoq', 'water': 'suv', 'way': 'yo‘l',
    'we': 'biz', 'whisper': 'pichirlamoq', 'win': 'yutmoq', 'window': 'deraza',
    'with': 'bilan', 'work': 'ishlamoq', 'worker': 'ishchi', 'write': 'yozmoq',
    'yard/garden': 'hovli/bog‘', 'you': 'siz', 'your': 'sizning', 'yours': 'sizniki',
    'yourself': 'o‘zingiz',
}


def _replace_case_insensitive(text, source, target):
    return re.sub(
        rf"(?<![\w‘’']){re.escape(source)}(?![\w‘’'])",
        target,
        text,
        flags=re.IGNORECASE,
    )


def translate_topic(topic, language):
    uzbek = TOPIC_PHRASES.get(topic.strip(), topic.strip())
    if language == 'uz':
        return uzbek
    result = uzbek
    for source, target in KAA_WORDS:
        # Whole phrase matching prevents short words such as "ish" from
        # corrupting longer words such as "tanishtirish".
        result = re.sub(
            rf"(?<![\w‘’']){re.escape(source)}(?![\w‘’'])",
            target,
            result,
        )
    return result


def translate_lesson_title(title, language):
    match = re.match(r'^\[Book (\d+)\]\s+Unit (\d+)\s+[—-]\s+(.+)$', title.strip())
    if not match:
        return translate_topic(title, language)
    book, unit, topic = match.groups()
    translated = translate_topic(topic, language)
    return (
        f'[{book}-kitap] {unit}-bólim — {translated}'
        if language == 'kaa'
        else f'[{book}-kitob] {unit}-bo‘lim — {translated}'
    )


def translate_description(description, language):
    if not description:
        return ''
    result = description
    if language == 'kaa':
        for source, target in (
            ('Practice Book', 'Shınıǵıw kitabı'), ('Intermediate', 'Orta dáreje'),
            ('Level', 'Dáreje'), ('section', 'bólim'), ('Unit', 'Bólim'), ('pages', 'betler'),
        ):
            result = result.replace(source, target)
    else:
        for source, target in (
            ('Practice Book', 'Mashq kitobi'), ('Intermediate', 'O‘rta daraja'),
            ('Level', 'Daraja'), ('section', 'bo‘lim'), ('Unit', 'Bo‘lim'), ('pages', 'betlar'),
        ):
            result = result.replace(source, target)
    return result


def translate_instruction(text, language):
    original = re.sub(r'\s+', ' ', text.strip())
    lowered = original.lower().rstrip('.')
    translated = INSTRUCTION_EXACT[language].get(lowered)
    if translated is None:
        for source, target in sorted(INSTRUCTION_START[language], key=lambda item: -len(item[0])):
            if lowered.startswith(source):
                translated = target + lowered[len(source):]
                break
    if translated is None:
        translated = lowered
    for source, target in sorted(TAIL_WORDS[language], key=lambda item: -len(item[0])):
        translated = _replace_case_insensitive(translated, source, target)
    translated = re.sub(r'\s+', ' ', translated).strip(' :')
    if translated:
        translated = translated[0].upper() + translated[1:]
    return translated + ('.' if original.endswith('.') and not translated.endswith('.') else '')


def normalize_uzbek(existing, english):
    key = re.sub(r'\s+', ' ', english.strip().lower())
    if key in VOCAB_UZ:
        return VOCAB_UZ[key]
    text = (existing or english).strip()
    replacements = {
        '`': '‘', '’': '‘', 'ı': 'i', 'á': 'a', 'ǵ': 'g‘', 'ń': 'ng', 'ó': 'o‘', 'ú': 'u',
        'shigw': 'chiqish', 'shigiw': 'chiqish', 'bariw': 'borish', 'koriw': 'ko‘rish',
        'tinlaw': 'tinglash', 'soylew': 'gapirish', 'oqiw': 'o‘qish', 'jaziw': 'yozish',
        'oynaw': 'o‘ynash', 'pisiriw': 'pishirish', 'tigiw': 'tikish', 'toqiw': 'to‘qish',
        'ushiw': 'uchish', 'juriw': 'yurish', 'koteriw': 'ko‘tarish', 'tusiniw': 'tushunish',
        'qiliw': 'qilish', 'islew': 'ishlash', 'shaliw': 'chalish', 'atiw': 'aytish',
        'qosiw': 'qo‘shish', 'aliw': 'olish', 'miniw': 'minish', 'tazalaw': 'tozalash',
        'boyaw': 'bo‘yash', 'ormelew': 'tirmashish', 'baqiriw': 'baqirish',
        'sekiriw': 'sakrash', 'tebiw': 'tepish', 'uriw': 'urish', 'ilaqtiriw': 'uloqtirish',
        'qalew': 'xohlash', 'qa‘lew': 'xohlash', 'jumis': 'ish', 'awqat': 'ovqat',
        'koshe': 'ko‘cha', 'suw': 'suv', 'miywe': 'meva', 'teniz': 'dengiz',
        'qoshiq': 'qoshiq', 'kitap': 'kitob', 'mektep': 'maktab',
        'oqitiwshi': 'o‘qituvchi', 'oqiwshi': 'o‘quvchi', 'joqari': 'yuqori',
        'tomengi': 'pastki', 'jaqin': 'yaqin', 'usi jer': 'shu yer', 'onin': 'uning',
        'olardin': 'ularning', 'bizlerdin': 'bizning', 'sizlerdin': 'sizning',
        'menin': 'mening', 'senin': 'sening', 'olar': 'ular', 'bizler': 'biz',
        'sizler': 'siz', 'ulken': 'katta', 'kishkene': 'kichkina', 'kishi': 'kichik',
        'suliw': 'chiroyli', 'jaman': 'yomon', 'ansat': 'oson', 'qimbat': 'qimmat',
        'arzan': 'arzon', 'erte': 'erta', 'bugin': 'bugun', 'erten': 'ertaga',
        'adette': 'odatda', 'barqulla': 'har doim', 'heshqashan': 'hech qachon',
        'arasinda': 'ba’zan', 'dawaminda': 'davomida',
    }
    for source, target in sorted(replacements.items(), key=lambda item: -len(item[0])):
        text = _replace_case_insensitive(text, source, target)
    return re.sub(r'\s+', ' ', text).strip()


class Command(BaseCommand):
    help = 'Offline: fill Qoraqalpoq and Uzbek content without any API calls.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--section', choices=['all', 'lessons', 'exercises', 'vocabulary'], default='all'
        )
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--force', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        section = options['section']
        dry_run = options['dry_run']
        force = options['force']
        counts = {'lessons': 0, 'exercises': 0, 'vocabulary': 0}

        if section in {'all', 'lessons'}:
            for lesson in Lesson.objects.all().iterator():
                lesson.title_kaa = translate_lesson_title(lesson.title, 'kaa')
                lesson.title_uz = translate_lesson_title(lesson.title, 'uz')
                lesson.description_kaa = translate_description(lesson.description, 'kaa')
                lesson.description_uz = translate_description(lesson.description, 'uz')
                lesson.video_url_kaa = lesson.video_url_kaa or lesson.video_url
                if force:
                    lesson.video_url_uz = None
                if not dry_run:
                    lesson.save(update_fields=[
                        'title_kaa', 'title_uz', 'description_kaa', 'description_uz',
                        'video_url_kaa', 'video_url_uz',
                    ])
                counts['lessons'] += 1

        if section in {'all', 'exercises'}:
            for exercise in Exercise.objects.all().iterator():
                if force or not exercise.instruction_kaa or exercise.instruction_kaa == exercise.instruction:
                    exercise.instruction_kaa = translate_instruction(exercise.instruction, 'kaa')
                if force or not exercise.instruction_uz or exercise.instruction_uz == exercise.instruction:
                    exercise.instruction_uz = translate_instruction(exercise.instruction, 'uz')
                if not dry_run:
                    exercise.save(update_fields=['instruction_kaa', 'instruction_uz'])
                counts['exercises'] += 1

        if section in {'all', 'vocabulary'}:
            for vocabulary in Vocabulary.objects.all().iterator():
                vocabulary.translation_kaa = vocabulary.translation_kaa or vocabulary.translation
                if force or not vocabulary.translation_uz:
                    vocabulary.translation_uz = normalize_uzbek(
                        vocabulary.translation_kaa, vocabulary.word
                    )
                if not dry_run:
                    vocabulary.save(update_fields=['translation_kaa', 'translation_uz'])
                counts['vocabulary'] += 1

        if dry_run:
            transaction.set_rollback(True)
        prefix = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}Offline localization complete: {counts['lessons']} lessons, "
            f"{counts['exercises']} exercises, {counts['vocabulary']} vocabulary rows."
        ))
