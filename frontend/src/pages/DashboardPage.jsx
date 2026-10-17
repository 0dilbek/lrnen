import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Flame,
  Headphones,
  Languages,
  Map as MapIcon,
  RotateCcw,
  Sparkles,
  Star,
  Target,
  Trophy,
  Zap,
} from 'lucide-react';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import { formatLessonTitle } from '../utils/lessonDisplay';
import { useLanguage } from '../context/LanguageContext';

const FEATURE_CARDS = [
  {
    icon: Languages,
    title: 'So‘z boyligini oshiring',
    text: 'Har bir mavzudagi yangi so‘zlarni misollar bilan o‘rganing va mustahkamlang.',
    style: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-300',
  },
  {
    icon: Target,
    title: 'Amaliyot bilan o‘sish',
    text: 'Interaktiv mashqlar va yakuniy testlar orqali bilimingizni darhol tekshiring.',
    style: 'bg-violet-500/10 text-violet-600 dark:text-violet-300',
  },
  {
    icon: Headphones,
    title: 'Tinglang va o‘qing',
    text: 'Audio, video va kitob sahifalari bilan tilni real kontekstda o‘zlashtiring.',
    style: 'bg-amber-500/10 text-amber-600 dark:text-amber-300',
  },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const { xp, streak, badges } = useGame();
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const navigate = useNavigate();
  const { language, t } = useLanguage();

  useEffect(() => {
    setLoading(true);
    setLoadError(false);
    Promise.all([
      api.get('/courses/lessons/'),
      api.get('/courses/progress/'),
    ])
      .then(([lessonResponse, progressResponse]) => {
        setLessons(lessonResponse.data);
        const progressMap = {};
        progressResponse.data.forEach((item) => {
          progressMap[item.lesson] = item;
        });
        setProgress(progressMap);
      })
      .catch(() => setLoadError(true))
      .finally(() => setLoading(false));
  }, [reloadKey, language]);

  if (loading) return <DashboardSkeleton />;

  if (loadError) {
    return (
      <div className="mx-auto max-w-xl px-4 py-20 text-center">
        <div className="student-card p-8">
          <div className="mb-4 text-5xl" aria-hidden="true">🧭</div>
          <h1 className="stu-title text-xl font-extrabold">{t('Bosh sahifani yuklab bo‘lmadi')}</h1>
          <p className="stu-muted mt-2">{t('Internet aloqasini tekshirib, qayta urinib ko‘ring.')}</p>
          <button
            type="button"
            onClick={() => setReloadKey((value) => value + 1)}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
          >
            <RotateCcw size={16} /> {t('Qayta urinish')}
          </button>
        </div>
      </div>
    );
  }

  const progressRows = Object.values(progress);
  const completedRows = progressRows.filter((item) => item.status === 'completed');
  const completedCount = lessons.filter(
    (lesson) => progress[lesson.id]?.status === 'completed',
  ).length;
  const completionPercent = lessons.length
    ? Math.round((completedCount / lessons.length) * 100)
    : 0;
  const averageScore = completedRows.length
    ? Math.round(completedRows.reduce((sum, item) => sum + (item.score || 0), 0) / completedRows.length)
    : 0;
  const currentLessonIndex = lessons.findIndex(
    (lesson) => progress[lesson.id]?.status !== 'completed' && !lesson.is_locked,
  );
  const currentLesson = currentLessonIndex >= 0 ? lessons[currentLessonIndex] : null;
  const upcomingLessons = currentLesson
    ? lessons.slice(currentLessonIndex + 1, currentLessonIndex + 4)
    : lessons.slice(-3).reverse();
  const firstName = (user?.full_name || user?.username || 'O‘quvchi').split(' ')[0];
  const currentLevel = currentLesson?.levels?.[0]?.name || 'Shaxsiy o‘quv yo‘li';

  const openPrimaryAction = () => {
    if (currentLesson) navigate(`/lessons/${currentLesson.id}`);
    else navigate('/results');
  };

  return (
    <div className="mx-auto max-w-7xl px-3 py-5 sm:px-5 sm:py-8">
      <section className="relative isolate overflow-hidden rounded-[2rem] bg-indigo-950 text-white shadow-2xl shadow-indigo-950/20">
        <img
          src="/assets/english-learning-hero.webp"
          alt="Noutbuk va quloqchin yordamida ingliz tilini o‘rganayotgan o‘quvchi"
          className="absolute inset-0 hidden h-full w-full object-cover object-[68%_center] lg:block"
          loading="eager"
          fetchPriority="high"
        />
        <div className="absolute inset-0 hidden bg-gradient-to-r from-indigo-950 via-indigo-950/90 to-indigo-950/10 lg:block" />

        <div className="relative grid items-center lg:min-h-[460px] lg:grid-cols-[1.08fr_.92fr]">
          <div className="max-w-2xl bg-gradient-to-b from-indigo-950 to-indigo-900 px-5 py-8 sm:px-9 sm:py-10 lg:bg-none lg:px-12 lg:py-12">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-extrabold uppercase tracking-[.13em] text-indigo-100 backdrop-blur-md">
              <Sparkles size={14} className="text-amber-300" /> {currentLevel}
            </div>
            <p className="mb-2 text-sm font-bold text-indigo-200">{t('Salom, {name}! 👋', { name: firstName })}</p>
            <h1 className="max-w-xl text-3xl font-black leading-[1.08] sm:text-4xl lg:text-5xl">
              {currentLesson
                ? t('Ingliz tilida navbatdagi qadamingiz tayyor.')
                : t('Ajoyib natija — barcha darslar yakunlandi!')}
            </h1>
            <p className="mt-4 max-w-lg text-sm leading-relaxed text-indigo-100 sm:text-base">
              {currentLesson
                ? `${currentLessonIndex + 1}-dars — ${formatLessonTitle(currentLesson.title)}. O‘rganishni to‘xtagan joyingizdan davom ettiring.`
                : 'Natijalaringizni ko‘ring va erishgan yutuqlaringizni yana bir bor nishonlang.'}
            </p>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={openPrimaryAction}
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-black text-indigo-700 shadow-xl shadow-indigo-950/20 transition hover:-translate-y-0.5 hover:bg-indigo-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-white/40"
              >
                {currentLesson ? <BookOpen size={18} /> : <Trophy size={18} />}
                {currentLesson ? t('Darsni davom ettirish') : t('Natijalarni ko‘rish')}
                <ArrowRight size={17} />
              </button>
              <button
                type="button"
                onClick={() => navigate('/my-lessons')}
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-2xl border border-white/20 bg-white/10 px-5 py-3 text-sm font-bold text-white backdrop-blur-md transition hover:bg-white/15 focus:outline-none focus-visible:ring-4 focus-visible:ring-white/30"
              >
                <MapIcon size={18} /> {t('Darslar xaritasi')}
              </button>
            </div>

            <div className="mt-8 max-w-md rounded-2xl border border-white/15 bg-indigo-950/35 p-4 backdrop-blur-md">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="text-xs font-bold text-indigo-200">{t('Umumiy progress')}</p>
                  <p className="mt-1 text-sm font-extrabold">{completedCount} / {lessons.length} {t('dars')}</p>
                </div>
                <strong className="text-2xl font-black">{completionPercent}%</strong>
              </div>
              <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-black/25">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-300 via-yellow-300 to-emerald-300 transition-all duration-700"
                  style={{ width: `${completionPercent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="relative h-72 overflow-hidden border-t border-white/10 sm:h-80 lg:hidden">
            <img
              src="/assets/english-learning-hero-mobile.webp"
              alt="Mobil qurilmada ingliz tilini o‘rganishga mos illustratsiya"
              className="h-full w-full object-cover object-[center_58%]"
              loading="eager"
              fetchPriority="high"
            />
            <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-indigo-900 to-transparent" />
          </div>
        </div>
      </section>

      <section className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <DashboardStat icon={CheckCircle2} value={completedCount} label={t('Yakunlangan dars')} color="emerald" />
        <DashboardStat icon={Star} value={`${averageScore}%`} label={t('O‘rtacha natija')} color="amber" />
        <DashboardStat icon={Flame} value={streak} label={t('Kunlik seriya')} color="orange" />
        <DashboardStat icon={Zap} value={xp} label={t('To‘plangan XP')} color="violet" />
      </section>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.25fr_.75fr]">
        <section>
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-extrabold uppercase tracking-[.14em] text-indigo-500 dark:text-indigo-300">{t('O‘quv yo‘lingiz')}</p>
              <h2 className="stu-title mt-1 text-xl font-black sm:text-2xl">
                {currentLesson ? t('Oldinda nimalar bor?') : t('So‘nggi marralaringiz')}
              </h2>
            </div>
            <button
              type="button"
              onClick={() => navigate('/my-lessons')}
              className="inline-flex shrink-0 items-center gap-1.5 text-sm font-bold text-indigo-600 transition hover:text-indigo-500 dark:text-indigo-300"
            >
              {t('Barchasi')} <ArrowRight size={16} />
            </button>
          </div>

          <div className="student-card overflow-hidden">
            {currentLesson && (
              <button
                type="button"
                onClick={() => navigate(`/lessons/${currentLesson.id}`)}
                className="group flex w-full items-center gap-4 border-b border-border bg-indigo-500/5 px-4 py-4 text-left transition hover:bg-indigo-500/10 sm:px-5"
              >
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-md shadow-orange-500/20">
                  <BookOpen size={20} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="text-[11px] font-extrabold uppercase tracking-wider text-orange-600 dark:text-orange-300">{t('Hozirgi dars')} · {currentLessonIndex + 1}</span>
                  <span className="stu-title mt-0.5 block truncate font-extrabold">{formatLessonTitle(currentLesson.title)}</span>
                </span>
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-indigo-600 text-white transition group-hover:translate-x-0.5">
                  <ArrowRight size={17} />
                </span>
              </button>
            )}

            {upcomingLessons.length > 0 ? upcomingLessons.map((lesson) => {
              const lessonIndex = lessons.findIndex((item) => item.id === lesson.id);
              const isCompleted = progress[lesson.id]?.status === 'completed';
              return (
                <div key={lesson.id} className="flex items-center gap-4 border-b border-border px-4 py-3.5 last:border-0 sm:px-5">
                  <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl text-sm font-black ${isCompleted ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300' : 'bg-surface-200 stu-muted'}`}>
                    {isCompleted ? <CheckCircle2 size={18} /> : lessonIndex + 1}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="stu-title block truncate text-sm font-bold">{formatLessonTitle(lesson.title)}</span>
                    <span className="stu-muted mt-0.5 block text-xs">{isCompleted ? t('Yakunlangan') : t('Hali ochilmagan')}</span>
                  </span>
                </div>
              );
            }) : (
              <div className="px-5 py-8 text-center">
                <Trophy className="mx-auto text-amber-500" size={32} />
                <p className="stu-title mt-2 font-bold">{t('Barcha darslarni yakunladingiz!')}</p>
              </div>
            )}
          </div>
        </section>

        <section>
          <div className="mb-4">
            <p className="text-xs font-extrabold uppercase tracking-[.14em] text-violet-500 dark:text-violet-300">{t('Yutuqlaringiz')}</p>
            <h2 className="stu-title mt-1 text-xl font-black sm:text-2xl">{t('Har bir qadam hisobda')}</h2>
          </div>
          <div className="student-card h-[calc(100%-3.75rem)] p-5">
            {badges.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {badges.slice(0, 6).map((badge) => (
                  <div key={badge.id} title={badge.desc} className="rounded-2xl border border-border bg-surface-200/60 p-3 text-center">
                    <span className="text-3xl" aria-hidden="true">{badge.emoji}</span>
                    <p className="stu-title mt-1 text-xs font-extrabold">{badge.label}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex h-full min-h-48 flex-col items-center justify-center text-center">
                <span className="grid h-16 w-16 place-items-center rounded-3xl bg-violet-500/10 text-violet-500">
                  <Trophy size={29} />
                </span>
                <p className="stu-title mt-4 font-extrabold">{t('Birinchi nishon sizni kutmoqda')}</p>
                <p className="stu-muted mt-1 max-w-xs text-sm">{t('Birinchi darsni boshlang va yutuqlar to‘plashni boshlang.')}</p>
              </div>
            )}
          </div>
        </section>
      </div>

      <section className="mt-10 pb-3">
        <div className="mb-5 text-center">
          <p className="text-xs font-extrabold uppercase tracking-[.14em] text-indigo-500 dark:text-indigo-300">{t('Barcha imkoniyatlar')}</p>
          <h2 className="stu-title mt-1 text-2xl font-black sm:text-3xl">{t('Tilni har tomonlama o‘rganing')}</h2>
          <p className="stu-muted mx-auto mt-2 max-w-2xl text-sm sm:text-base">Bitta dars ichida kerakli nazariya, amaliyot va real materiallar bir joyda.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {FEATURE_CARDS.map(({ icon: Icon, title, text, style }) => (
            <article key={title} className="student-card p-5 sm:p-6">
              <span className={`grid h-12 w-12 place-items-center rounded-2xl ${style}`}>
                <Icon size={23} />
              </span>
              <h3 className="stu-title mt-4 text-lg font-extrabold">{t(title)}</h3>
              <p className="stu-muted mt-2 text-sm leading-relaxed">{t(text)}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function DashboardStat({ icon: Icon, value, label, color }) {
  const colors = {
    emerald: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300',
    amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-300',
    orange: 'bg-orange-500/10 text-orange-600 dark:text-orange-300',
    violet: 'bg-violet-500/10 text-violet-600 dark:text-violet-300',
  };

  return (
    <article className="student-card flex min-w-0 items-center gap-3 p-3.5 sm:gap-4 sm:p-5">
      <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl sm:h-12 sm:w-12 sm:rounded-2xl ${colors[color]}`}>
        <Icon size={21} />
      </span>
      <span className="min-w-0">
        <strong className="stu-title block truncate text-xl font-black sm:text-2xl">{value}</strong>
        <span className="stu-muted block truncate text-[11px] font-semibold sm:text-sm">{label}</span>
      </span>
    </article>
  );
}

function DashboardSkeleton() {
  return (
    <div className="mx-auto max-w-7xl animate-pulse px-3 py-5 sm:px-5 sm:py-8" aria-label="Bosh sahifa yuklanmoqda">
      <div className="h-[460px] rounded-[2rem] bg-surface-300" />
      <div className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => <div key={index} className="h-24 rounded-2xl bg-surface-300" />)}
      </div>
      <div className="mt-8 grid gap-6 lg:grid-cols-[1.25fr_.75fr]">
        <div className="h-72 rounded-2xl bg-surface-300" />
        <div className="h-72 rounded-2xl bg-surface-300" />
      </div>
    </div>
  );
}
