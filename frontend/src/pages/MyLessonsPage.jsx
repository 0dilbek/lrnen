import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  CheckCircle,
  Clock,
  Loader2,
  LocateFixed,
  LockKeyhole,
} from 'lucide-react';
import api from '../api';
import LearningRoadmap from '../components/lesson/LearningRoadmap';
import { formatLessonTitle } from '../utils/lessonDisplay';
import { useLanguage } from '../context/LanguageContext';

const MOTIVATIONAL = [
  { min: 0, max: 0, msg: 'Bugun birinchi darsni boshlang — sayohat sizni kutmoqda!', emoji: '🚀' },
  { min: 1, max: 2, msg: 'Zo‘r boshladingiz! Keyingi manzilga yo‘l oling!', emoji: '💪' },
  { min: 3, max: 5, msg: 'Ajoyib! Yo‘l xaritangiz tobora kengaymoqda!', emoji: '⭐' },
  { min: 6, max: 10, msg: 'Juda faol o‘quvchisiz — shu tempda davom eting!', emoji: '🔥' },
  { min: 11, max: Infinity, msg: 'Ingliz tili cho‘qqisi tobora yaqinlashmoqda!', emoji: '🏆' },
];

function getMotivation(count) {
  return MOTIVATIONAL.find((item) => count >= item.min && count <= item.max) || MOTIVATIONAL[0];
}

export default function MyLessonsPage() {
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const navigate = useNavigate();
  const { language, t } = useLanguage();

  useEffect(() => {
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
  }, [language]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  const completedCount = lessons.filter(
    (lesson) => progress[lesson.id]?.status === 'completed',
  ).length;
  const inProgressCount = lessons.filter(
    (lesson) => progress[lesson.id]?.status === 'in-progress',
  ).length;
  const lockedCount = lessons.filter((lesson) => lesson.is_locked).length;
  const motivation = getMotivation(completedCount);
  const currentLessonIndex = lessons.findIndex(
    (lesson) => progress[lesson.id]?.status !== 'completed' && !lesson.is_locked,
  );
  const currentLesson = currentLessonIndex >= 0 ? lessons[currentLessonIndex] : null;

  const jumpToCurrentLesson = () => {
    if (!currentLesson) return;
    document.getElementById(`roadmap-lesson-${currentLesson.id}`)?.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    });
  };

  return (
    <div className="mx-auto max-w-5xl px-3 py-7 sm:px-5 sm:py-9">
      <div className="mb-6">
        <h1 className="stu-title text-2xl font-black sm:text-3xl">{t('Darslarim')}</h1>
        <p className="stu-muted mt-1">{t('Har bir dars testidan kamida 60% oling — keyingi dars avtomatik ochiladi')}</p>
      </div>

      {loadError ? (
        <div className="student-card p-10 text-center">
          <div className="mb-3 text-5xl" aria-hidden="true">🧭</div>
          <h2 className="stu-title text-xl font-extrabold">{t('Darslarni yuklab bo‘lmadi')}</h2>
          <p className="stu-muted mt-2">{t('Sahifani yangilab, qayta urinib ko‘ring.')}</p>
        </div>
      ) : (
        <>
          <section className="mb-6 overflow-hidden rounded-3xl border border-indigo-500/20 bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600 p-5 text-white shadow-xl shadow-indigo-500/15 sm:p-6">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex min-w-0 items-center gap-4">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl border border-white/15 bg-white/10 text-3xl backdrop-blur-sm" aria-hidden="true">
                  {currentLesson ? motivation.emoji : '🏆'}
                </span>
                <div className="min-w-0">
                  <p className="text-xs font-extrabold uppercase tracking-[.13em] text-indigo-200">
                    {currentLesson ? `${t('Hozirgi dars')} · ${currentLessonIndex + 1}` : t('Barcha darslar yakunlandi')}
                  </p>
                  <h2 className="mt-1 truncate text-lg font-black sm:text-xl">
                    {currentLesson ? formatLessonTitle(currentLesson.title) : 'Til cho‘qqisini zabt etdingiz!'}
                  </h2>
                  <p className="mt-1 text-sm text-indigo-100">{t(motivation.msg)}</p>
                </div>
              </div>

              {currentLesson && (
                <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={jumpToCurrentLesson}
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 text-sm font-bold transition hover:bg-white/15"
                  >
                    <LocateFixed size={17} /> {t('Xaritadagi joyim')}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate(`/lessons/${currentLesson.id}`)}
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-white px-4 text-sm font-black text-indigo-700 shadow-lg transition hover:bg-indigo-50"
                  >
                    <BookOpen size={17} /> {t('Darsni ochish')} <ArrowRight size={16} />
                  </button>
                </div>
              )}
            </div>
          </section>

          <div className="mb-7 grid grid-cols-3 gap-2 sm:gap-4">
            <StatCard icon={CheckCircle} value={completedCount} label={t('Yakunlangan')} color="emerald" />
            <StatCard icon={Clock} value={inProgressCount} label={t('Jarayonda')} color="amber" />
            <StatCard icon={LockKeyhole} value={lockedCount} label={t('Oldinda')} color="slate" />
          </div>

          <LearningRoadmap
            lessons={lessons}
            progress={progress}
            onOpenLesson={(lesson) => navigate(`/lessons/${lesson.id}`)}
          />

          {currentLesson && (
            <button
              type="button"
              onClick={jumpToCurrentLesson}
              className="fixed bottom-20 right-3 z-40 inline-flex items-center gap-2 rounded-full border border-indigo-400/25 bg-indigo-600 px-4 py-3 text-xs font-black text-white shadow-xl shadow-indigo-950/25 transition hover:bg-indigo-500 md:bottom-6 md:right-6"
            >
              <LocateFixed size={16} /> {t('Hozirgi dars')}
            </button>
          )}
        </>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, value, label, color }) {
  const styles = {
    emerald: 'bg-emerald-500/15 text-emerald-500',
    amber: 'bg-amber-500/15 text-amber-500',
    slate: 'bg-slate-500/15 text-slate-600 dark:text-slate-300',
  };

  return (
    <div className="student-card flex min-w-0 flex-col items-center gap-2 p-3 text-center sm:flex-row sm:gap-4 sm:p-5 sm:text-left">
      <div className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl sm:h-12 sm:w-12 ${styles[color]}`}>
        <Icon size={22} />
      </div>
      <div className="min-w-0">
        <p className="stu-title text-xl font-black sm:text-3xl">{value}</p>
        <p className="stu-muted truncate text-[11px] font-semibold sm:text-sm">{label}</p>
      </div>
    </div>
  );
}
