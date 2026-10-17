import { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';

const LanguageContext = createContext(null);
const STORAGE_KEY = 'interface_language';

const KAA = {
  'O‘zbekcha': 'Ózbekshe',
  'Qoraqalpoqcha': 'Qaraqalpaqsha',
  'Bosh sahifa': 'Bas bet',
  'Bosh': 'Bas bet',
  'Darslarim': 'Sabaqlarım',
  'Darslar': 'Sabaqlar',
  'Natijalar': 'Nátiyjeler',
  'Reyting': 'Reyting',
  'Reyting jadvali': 'Reyting kestesi',
  'Chiqish': 'Shıǵıw',
  'O‘quv platformasi': 'Oqıw platforması',
  'Kunduzgi rejim': 'Kúndizgi rejim',
  'Tungi rejim': 'Túngi rejim',
  'Natijalarim': 'Nátiyjelerim',
  'Progress': 'Ózlesiw',
  'bajarildi': 'orınlandı',
  'Til': 'Til',
  'Login va parolni kiriting': 'Login hám paroldı kiritiń',
  "Login yoki parol noto'g'ri": 'Login yamasa parol nadurıs',
  "Ingliz tilini o'rganishning eng qiziqarli usuli!": 'Inglis tilin úyreniwdiń eń qızıqlı usılı!',
  'Xush kelibsiz! 👋': 'Xosh keldińiz! 👋',
  'Parol': 'Parol',
  'Kirish': 'Kiriw',
  'Kirish...': 'Kirip atır...',
  'Loginingizni kiriting': 'Loginińizdi kiritiń',
  'Parolingizni kiriting': 'Parolińizdi kiritiń',
  "Login va parol o'qituvchi tomonidan beriladi": 'Login hám paroldı oqıtıwshı beredi',
  'Bilim sari yangi qadam': 'Bilimge qaray jańa qádem',
  'Ingliz tilini ishonch bilan o‘rganing': 'Inglis tilin isenim menen úyreniń',
  'Har kuni yangi qadam, har darsda yangi imkoniyat.': 'Hár kúni jańa qádem, hár sabaqta jańa imkaniyat.',
  'Shaxsiy darslar': 'Jeke sabaqlar',
  'Interaktiv mashqlar': 'Interaktiv shınıǵıwlar',
  'Natijalarni kuzatish': 'Nátiyjelerdi baqlaw',
  'Hisobingizga kiring': 'Esabıńızǵa kiriń',
  'Darslaringizni davom ettirish uchun ma’lumotlaringizni kiriting.': 'Sabaqlarıńızdı dawam ettiriw ushın maǵlıwmatlarıńızdı kiritiń.',
  'Parolni ko‘rsatish': 'Paroldı kórsetiw',
  'Parolni yashirish': 'Paroldı jasırıw',
  'Dars haqida': 'Sabaq haqqında',
  "Yangi so'zlar": 'Jańa sózler',
  'Mashqlar': 'Shınıǵıwlar',
  'Test': 'Test',
  'Izohlar': 'Pikirler',
  "Hali izoh yo'q — birinchi bo'ling!": 'Ele pikir joq — birinshi bolıń!',
  'Yuborish': 'Jiberiw',
  'Oldingi dars': 'Aldınǵı sabaq',
  'Keyingi dars': 'Keyingi sabaq',
  'Hali qulflangan': 'Ele qulıplı',
  'Testdan kamida 60% oling': 'Testten keminde 60% alıń',
  'Barcha darslar yakunlandi! 🎓': 'Barlıq sabaqlar juwmaqlandı! 🎓',
  'Testni yakunlash': 'Testti juwmaqlaw',
  'Tekshirilmoqda...': 'Tekserilip atır...',
  'Darslarimga qaytish': 'Sabaqlarımǵa qaytıw',
  'Video dars': 'Video sabaq',
  'Reading': 'Oqıw',
  'Eng ko‘p XP to‘plagan o‘quvchilar': 'Eń kóp XP toplaǵan oqıwshılar',
  'Siz': 'Siz',
  'dars': 'sabaq',
  'Hali reyting mavjud emas': 'Ele reyting joq',
  'Umumiy bilim darajangiz statistikasi': 'Ulıwma bilim dárejeńiz statistikası',
  "Hali natija yo'q": 'Ele nátiyje joq',
  'Darslarni boshlash': 'Sabaqlardı baslaw',
  'Boshlangan': 'Baslanǵan',
  'Yakunlangan': 'Juwmaqlanǵan',
  "O'rtacha ball": 'Ortalama ball',
  "Darslar bo'yicha natijalar": 'Sabaqlar boyınsha nátiyjeler',
  'Jarayonda': 'Processde',
  'Yakunlandi': 'Juwmaqlandı',
  'Bosh sahifani yuklab bo‘lmadi': 'Bas betti júklep bolmadı',
  'Internet aloqasini tekshirib, qayta urinib ko‘ring.': 'Internet baylanısın tekserip, qayta urınıp kóriń.',
  'Qayta urinish': 'Qayta urınıw',
  'Salom, {name}! 👋': 'Sálem, {name}! 👋',
  'Ingliz tilida navbatdagi qadamingiz tayyor.': 'Inglis tilindegi keyingi qádemińiz tayar.',
  'Ajoyib natija — barcha darslar yakunlandi!': 'Ájayıp nátiyje — barlıq sabaqlar juwmaqlandı!',
  'Darsni davom ettirish': 'Sabaqtı dawam ettiriw',
  'Natijalarni ko‘rish': 'Nátiyjelerdi kóriw',
  'Darslar xaritasi': 'Sabaqlar kartası',
  'Umumiy progress': 'Ulıwma ózlesiw',
  'Yakunlangan dars': 'Juwmaqlanǵan sabaq',
  'O‘rtacha natija': 'Ortalama nátiyje',
  'Kunlik seriya': 'Kúnlik seriya',
  'To‘plangan XP': 'Toplanǵan XP',
  'O‘quv yo‘lingiz': 'Oqıw jolıńız',
  'Oldinda nimalar bor?': 'Aldında neler bar?',
  'So‘nggi marralaringiz': 'Sońǵı jetiskenliklerińiz',
  'Barchasi': 'Barlıǵı',
  'Hozirgi dars': 'Házirgi sabaq',
  'Hali ochilmagan': 'Ele ashılmaǵan',
  'Barcha darslarni yakunladingiz!': 'Barlıq sabaqlardı juwmaqladıńız!',
  'Yutuqlaringiz': 'Jetiskenliklerińiz',
  'Har bir qadam hisobda': 'Hár bir qádem esapta',
  'Birinchi nishon sizni kutmoqda': 'Birinshi belgi sizdi kútip tur',
  'Birinchi darsni boshlang va yutuqlar to‘plashni boshlang.': 'Birinshi sabaqtı baslap, jetiskenliklerdi toplań.',
  'Barcha imkoniyatlar': 'Barlıq imkaniyatlar',
  'Tilni har tomonlama o‘rganing': 'Tildi hár tárepleme úyreniń',
  'So‘z boyligini oshiring': 'Sóz baylıǵıńızdı arttırıń',
  'Amaliyot bilan o‘sish': 'Ámeliyat penen rawajlanıw',
  'Tinglang va o‘qing': 'Tıńlań hám oqıń',
  'Har bir dars testidan kamida 60% oling — keyingi dars avtomatik ochiladi': 'Hár sabaq testinen keminde 60% alıń — keyingi sabaq avtomat túrde ashıladı',
  'Darslarni yuklab bo‘lmadi': 'Sabaqlardı júklep bolmadı',
  'Sahifani yangilab, qayta urinib ko‘ring.': 'Betti jańalap, qayta urınıp kóriń.',
  'Barcha darslar yakunlandi': 'Barlıq sabaqlar juwmaqlandı',
  'Xaritadagi joyim': 'Kartadaǵı ornım',
  'Darsni ochish': 'Sabaqtı ashıw',
  'Oldinda': 'Aldında',
  'Dars topilmadi': 'Sabaq tabılmadı',
  'Video mavjud emas': 'Video joq',
  'Bu til uchun video hali yuklanmagan.': 'Bul til ushın video ele júklenbegen.',
  'ta so‘z — 4 bosqichda o‘rganing': 'sóz — 4 basqıshta úyreniń',
  'ta mashq': 'shınıǵıw',
  'ta savol': 'soraw',
  'ta izoh': 'pikir',
  'Savol yoki izoh yozing...': 'Soraw yamasa pikir jazıń...',
  '1-savol namuna — shunday yechiladi. Siz 2-savoldan boshlang.': '1-soraw úlgi — usınday sheshiledi. Siz 2-sorawdan baslań.',
  'Test javoblarini yuborib bo‘lmadi. Qayta urinib ko‘ring.': 'Test juwapların jiberip bolmadı. Qayta urınıp kóriń.',
  'Ajoyib natija!': 'Ájayıp nátiyje!',
  'Yaxshi natija!': 'Jaqsı nátiyje!',
  'Davom eting!': 'Dawam etiń!',
  'Boshlang!': 'Baslań!',
  'O‘rtacha ballingiz:': 'Ortalama ballıńız:',
  'Birinchi darsni yakunlang va natijangizni ko‘ring!': 'Birinshi sabaqtı juwmaqlap, nátiyjeńizdi kóriń!',
  "Eng ko'p XP to'plagan o'quvchilar": 'Eń kóp XP toplaǵan oqıwshılar',
  'Hozircha darslar yo‘q': 'Házirinshe sabaqlar joq',
  'Sizga dars biriktirilganda yo‘l xaritasi shu yerda paydo bo‘ladi.': 'Sizge sabaq biriktirilgende jol kartası usı jerde payda boladı.',
  'Oldingi dars testidan 60% oling': 'Aldınǵı sabaq testinen 60% alıń',
  'Ochiq dars': 'Ashıq sabaq',
  'Siz shu yerdasiz': 'Siz usı jerdesiz',
  'Yo‘l xaritasining marrasi': 'Jol kartasınıń márresi',
  'Barcha darslarni tugatib, til cho‘qqisini zabt eting!': 'Barlıq sabaqlardı juwmaqlap, til shıńın iyeleń!',
  "To'g'ri so'zni tanlash": 'Durıs sózdi tańlaw',
  "Bo'sh joy to'ldirish": 'Bos orındı toltırıw',
  'Moslashtirish': 'Sáykeslestiriw',
  'Speaking': 'Sóylew',
  "So'zlarni tartiblash": 'Sózlerdi tártipke keltiriw',
  'Yozma javob': 'Jazba juwap',
  'Course Book manbasi': 'Course Book deregi',
  'Birinchi gap namuna. So‘zlarni bosib to‘g‘ri gap tuzing.': 'Birinshi gáp úlgi. Sózlerdi basıp, durıs gáp dúziń.',
  'Birinchi javob namuna. Qolgan javoblarni to‘liq gap bilan yozing.': 'Birinshi juwap úlgi. Qalǵan juwaplardı tolıq gáp penen jazıń.',
  'To‘g‘ri javob:': 'Durıs juwap:',
  'Tekshirish': 'Tekseriw',
  'Javobni inglizcha yozing...': 'Juwaptı inglisshe jazıń...',
  'Natijani serverga saqlab bo‘lmadi.': 'Nátiyjeni serverge saqlap bolmadı.',
  '1. Tanishish': '1. Tanısıw',
  '4. Yozish': '4. Jazıw',
  'Bugun birinchi darsni boshlang — sayohat sizni kutmoqda!': 'Búgin birinshi sabaqtı baslań — sayaxat sizdi kútip tur!',
  'Zo‘r boshladingiz! Keyingi manzilga yo‘l oling!': 'Jaqsı basladıńız! Keyingi mánzilge jol alıń!',
  'Ajoyib! Yo‘l xaritangiz tobora kengaymoqda!': 'Ájayıp! Jol kartańız keńeyip barmaqta!',
  'Juda faol o‘quvchisiz — shu tempda davom eting!': 'Júdá belsendi oqıwshısız — usı tempte dawam etiń!',
  'Ingliz tili cho‘qqisi tobora yaqinlashmoqda!': 'Inglis tili shıńı jaqınlap barmaqta!',
  'Har bir mavzudagi yangi so‘zlarni misollar bilan o‘rganing va mustahkamlang.': 'Hár temadaǵı jańa sózlerdi mısallar menen úyrenip, bekkemleń.',
  'Interaktiv mashqlar va yakuniy testlar orqali bilimingizni darhol tekshiring.': 'Interaktiv shınıǵıwlar hám juwmaqlawshı testler arqalı bilimińizdi tekseriń.',
  'Audio, video va kitob sahifalari bilan tilni real kontekstda o‘zlashtiring.': 'Audio, video hám kitap betleri menen tildi real kontekstte ózlestiriń.',
  'Dashboard': 'Basqarıw paneli',
  'O‘quvchilar': 'Oqıwshılar',
  'Notificationlar': 'Xabarlamalar',
  'Kontent': 'Kontent',
  'Administrator': 'Administrator',
  'Boshqaruv': 'Basqarıw',
  "Platformaning umumiy ko'rinishi": 'Platformanıń ulıwma kórinisi',
  "Ro'yxatdan o'tganlar va faollik": 'Dizimnen ótkenler hám belsendilik',
  "Darslar, mashqlar va lug'at": 'Sabaqlar, shınıǵıwlar hám sózlik',
};

function interpolate(value, params) {
  return Object.entries(params || {}).reduce(
    (result, [key, replacement]) => result.replaceAll(`{${key}}`, replacement),
    value,
  );
}

export function LanguageProvider({ children }) {
  const { user, updateProfile } = useAuth();
  const [language, setLanguage] = useState(
    () => localStorage.getItem(STORAGE_KEY) || 'kaa',
  );

  useEffect(() => {
    if (user?.language) {
      setLanguage(user.language);
      localStorage.setItem(STORAGE_KEY, user.language);
    }
  }, [user?.language]);

  const changeLanguage = async (nextLanguage) => {
    if (!['kaa', 'uz'].includes(nextLanguage)) return;
    const previous = language;
    setLanguage(nextLanguage);
    localStorage.setItem(STORAGE_KEY, nextLanguage);
    if (user) {
      try {
        await updateProfile({ language: nextLanguage });
      } catch (error) {
        setLanguage(previous);
        localStorage.setItem(STORAGE_KEY, previous);
        throw error;
      }
    }
  };

  const value = {
    language,
    changeLanguage,
    t: (uzbekText, params) => interpolate(
      language === 'kaa' ? (KAA[uzbekText] || uzbekText) : uzbekText,
      params,
    ),
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export const useLanguage = () => useContext(LanguageContext);
