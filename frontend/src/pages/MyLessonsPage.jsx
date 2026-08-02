import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Clock, Loader2, LockKeyhole } from 'lucide-react';
import api from '../api';
import LearningRoadmap from '../components/lesson/LearningRoadmap';

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

  return (
    <div className="mx-auto max-w-5xl px-3 py-7 sm:px-5 sm:py-9">
      <div className="mb-6">
        <h1 className="stu-title text-2xl font-black sm:text-3xl">Darslarim</h1>
        <p className="stu-muted mt-1">Barcha darslar bitta sayohat xaritasida</p>
      </div>

      {loadError ? (
        <div className="student-card p-10 text-center">
          <div className="mb-3 text-5xl" aria-hidden="true">🧭</div>
          <h2 className="stu-title text-xl font-extrabold">Darslarni yuklab bo‘lmadi</h2>
          <p className="stu-muted mt-2">Sahifani yangilab, qayta urinib ko‘ring.</p>
        </div>
      ) : (
        <>
          <section className="mb-6 flex items-center gap-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 p-5 text-white shadow-lg shadow-indigo-500/20">
            <span className="text-4xl" aria-hidden="true">{motivation.emoji}</span>
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-indigo-200">Bugungi ruhiyat</p>
              <p className="mt-1 font-bold sm:text-lg">{motivation.msg}</p>
            </div>
          </section>

          <div className="mb-7 grid grid-cols-3 gap-2 sm:gap-4">
            <StatCard icon={CheckCircle} value={completedCount} label="Yakunlangan" color="emerald" />
            <StatCard icon={Clock} value={inProgressCount} label="Jarayonda" color="amber" />
            <StatCard icon={LockKeyhole} value={lockedCount} label="Oldinda" color="slate" />
          </div>

          <LearningRoadmap
            lessons={lessons}
            progress={progress}
            onOpenLesson={(lesson) => navigate(`/lessons/${lesson.id}`)}
          />
        </>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, value, label, color }) {
  const styles = {
    emerald: 'bg-emerald-500/15 text-emerald-500',
    amber: 'bg-amber-500/15 text-amber-500',
    slate: 'bg-slate-500/15 text-slate-500',
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
