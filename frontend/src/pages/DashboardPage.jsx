import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Flame, Loader2, Map, Zap } from 'lucide-react';
import api from '../api';
import LearningRoadmap from '../components/lesson/LearningRoadmap';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const { xp, streak, badges } = useGame();
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const navigate = useNavigate();

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
  }, []);

  const completedCount = lessons.filter(
    (lesson) => progress[lesson.id]?.status === 'completed',
  ).length;
  const completionPercent = lessons.length
    ? Math.round((completedCount / lessons.length) * 100)
    : 0;
  const currentLesson = lessons.find(
    (lesson) => progress[lesson.id]?.status !== 'completed' && !lesson.is_locked,
  );

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-xl px-4 py-20 text-center">
        <div className="student-card p-8">
          <div className="mb-4 text-5xl" aria-hidden="true">🧭</div>
          <h1 className="stu-title text-xl font-extrabold">Yo‘l xaritasini yuklab bo‘lmadi</h1>
          <p className="stu-muted mt-2">Internet aloqasini tekshirib, sahifani qayta yangilang.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-3 py-7 sm:px-5 sm:py-9">
      <section className="mb-6 overflow-hidden rounded-3xl border border-indigo-500/20 bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600 p-5 text-white shadow-xl shadow-indigo-500/15 sm:p-7">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-extrabold uppercase tracking-[.15em] text-indigo-100">
              <Map size={16} /> Mening o‘quv sayohatim
            </div>
            <h1 className="text-2xl font-black sm:text-3xl">
              Salom, {(user?.full_name || user?.username || 'O‘quvchi').split(' ')[0]}! 👋
            </h1>
            <p className="mt-2 max-w-xl text-sm text-indigo-100 sm:text-base">
              {currentLesson
                ? `Keyingi manzil — ${currentLesson.order || completedCount + 1}-dars. Yo‘lni davom ettiramiz!`
                : completedCount > 0
                  ? 'Ajoyib! Barcha mavjud darslarni yakunladingiz.'
                  : 'Birinchi darsdan boshlang va yangi hududlarni oching.'}
            </p>
          </div>

          <div className="min-w-48 rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
            <div className="flex items-end justify-between">
              <span className="text-xs font-bold text-indigo-100">Umumiy yo‘l</span>
              <strong className="text-2xl font-black">{completionPercent}%</strong>
            </div>
            <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-black/15">
              <div
                className="h-full rounded-full bg-gradient-to-r from-amber-300 to-yellow-100 transition-all duration-700"
                style={{ width: `${completionPercent}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-indigo-100">{completedCount} / {lessons.length} dars yakunlandi</p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-sm font-bold">
            <Zap size={14} className="text-yellow-300" /> {xp} XP
          </span>
          {streak > 0 && (
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-sm font-bold">
              <Flame size={14} className="text-orange-300" /> {streak} kunlik seriya
            </span>
          )}
          {completedCount > 0 && (
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-sm font-bold">
              <CheckCircle size={14} className="text-emerald-200" /> {completedCount} ta marra
            </span>
          )}
        </div>

        {badges.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {badges.map((badge) => (
              <span
                key={badge.id}
                title={badge.desc}
                className="inline-flex cursor-default items-center gap-1.5 rounded-full border border-white/15 bg-black/10 px-2.5 py-1 text-xs font-semibold"
              >
                {badge.emoji} {badge.label}
              </span>
            ))}
          </div>
        )}
      </section>

      <LearningRoadmap
        lessons={lessons}
        progress={progress}
        onOpenLesson={(lesson) => navigate(`/lessons/${lesson.id}`)}
      />
    </div>
  );
}
