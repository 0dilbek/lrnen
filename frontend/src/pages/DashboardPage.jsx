import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import api from '../api';
import { Search, CheckCircle, Clock, Loader2, Zap, Flame, ChevronRight } from 'lucide-react';
import { formatLessonTitle, getUnitNumber } from '../utils/lessonDisplay';

export default function DashboardPage() {
  const { user } = useAuth();
  const { xp, streak, badges } = useGame();
  const [lessons, setLessons] = useState([]);
  const [search, setSearch] = useState('');
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get('/courses/lessons/'),
      api.get('/courses/progress/'),
    ]).then(([lsns, prog]) => {
      setLessons(lsns.data);
      const progressMap = {};
      prog.data.forEach((p) => { progressMap[p.lesson] = p; });
      setProgress(progressMap);
    }).finally(() => setLoading(false));
  }, []);

  const filtered = lessons.filter((l) => {
    const title = formatLessonTitle(l.title);
    return title.toLowerCase().includes(search.toLowerCase());
  });

  const completedCount = Object.values(progress).filter((p) => p.status === 'completed').length;
  const currentLesson = lessons.find((l) => progress[l.id]?.status !== 'completed');

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">
          Salom, {(user?.full_name || user?.username || 'O\'quvchi').split(' ')[0]}! 👋
        </h1>
        <p className="text-slate-400 mb-4">
          {currentLesson
            ? 'Keyingi darsingiz tayyor — boshlaymizmi?'
            : completedCount > 0
              ? 'Barcha mavjud darslarni yakunladingiz!'
              : 'Birinchi darsdan boshlang'}
        </p>

        <div className="flex gap-3 flex-wrap">
          <div className="flex items-center gap-2 bg-violet-500/15 text-violet-300 px-3 py-1.5 rounded-full text-sm font-semibold border border-violet-500/25">
            <Zap size={14} className="text-violet-500" />
            {xp} XP
          </div>
          {streak > 0 && (
            <div className="flex items-center gap-2 bg-orange-500/15 text-orange-300 px-3 py-1.5 rounded-full text-sm font-semibold border border-orange-500/25">
              <Flame size={14} className="text-orange-500" />
              {streak} kunlik seria
            </div>
          )}
          {completedCount > 0 && (
            <div className="flex items-center gap-2 bg-emerald-500/15 text-emerald-300 px-3 py-1.5 rounded-full text-sm font-semibold border border-emerald-500/25">
              <CheckCircle size={14} />
              {completedCount} yakunlandi
            </div>
          )}
        </div>

        {badges.length > 0 && (
          <div className="flex gap-2 mt-3 flex-wrap">
            {badges.map((b) => (
              <span
                key={b.id}
                title={b.desc}
                className="inline-flex items-center gap-1.5 bg-surface-100 border border-border text-slate-300 text-xs font-semibold px-2.5 py-1 rounded-full cursor-default"
              >
                {b.emoji} {b.label}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Search */}
      {lessons.length > 3 && (
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Dars qidirish..."
            className="admin-input pl-10"
          />
        </div>
      )}

      {/* Lesson path */}
      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-slate-300 text-lg font-medium">Dars topilmadi</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((lesson, idx) => (
            <LessonRow
              key={lesson.id}
              lesson={lesson}
              progress={progress[lesson.id]}
              isCurrent={lesson.id === currentLesson?.id}
              isLast={idx === filtered.length - 1}
              onClick={() => navigate(`/lessons/${lesson.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function LessonRow({ lesson, progress, isCurrent, isLast, onClick }) {
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in-progress';
  const score = progress?.score || 0;
  const unitNum = getUnitNumber(lesson.title);
  const title = formatLessonTitle(lesson.title);

  return (
    <div className="flex gap-4">
      {/* Timeline */}
      <div className="flex flex-col items-center shrink-0 w-8">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
          isCompleted
            ? 'bg-emerald-500/20 text-emerald-400 border-2 border-emerald-500/40'
            : isCurrent
              ? 'bg-indigo-500 text-white border-2 border-indigo-400 shadow-lg shadow-indigo-500/30'
              : 'bg-surface-200 text-slate-400 border-2 border-border'
        }`}>
          {isCompleted ? <CheckCircle size={16} /> : unitNum ?? '·'}
        </div>
        {!isLast && (
          <div className={`w-0.5 flex-1 min-h-[12px] mt-1 ${
            isCompleted ? 'bg-emerald-500/30' : 'bg-border'
          }`} />
        )}
      </div>

      {/* Card */}
      <button
        onClick={onClick}
        className={`flex-1 text-left student-card p-4 mb-1 transition-all duration-200 hover:-translate-y-0.5 ${
          isCurrent ? 'border-indigo-500/40 ring-1 ring-indigo-500/20' : ''
        }`}
      >
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {isCurrent && (
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/15 px-2 py-0.5 rounded-full">
                  Hozirgi dars
                </span>
              )}
              {isCompleted && (
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/15 px-2 py-0.5 rounded-full">
                  Yakunlandi
                </span>
              )}
              {isInProgress && !isCurrent && (
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded-full">
                  Jarayonda
                </span>
              )}
            </div>
            <h3 className="font-bold text-white text-base leading-snug truncate">{title}</h3>
          </div>
          <ChevronRight size={18} className="text-slate-500 shrink-0" />
        </div>

        {progress && (
          <div className="mt-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-500">
                {isCompleted ? 'Natija' : 'Jarayon'}
              </span>
              <span className={`text-xs font-bold ${isCompleted ? 'text-emerald-400' : 'text-amber-400'}`}>
                {score}%
              </span>
            </div>
            <div className="w-full bg-surface-200 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-1.5 rounded-full transition-all duration-500 ${
                  isCompleted
                    ? 'bg-gradient-to-r from-emerald-400 to-green-500'
                    : 'bg-gradient-to-r from-amber-400 to-orange-400'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        )}

        {isCurrent && !progress && (
          <p className="text-xs text-indigo-400 mt-2 flex items-center gap-1">
            <Clock size={12} />
            Boshlash uchun bosing
          </p>
        )}
      </button>
    </div>
  );
}