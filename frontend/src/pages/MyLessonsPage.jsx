import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Loader2, CheckCircle, Clock, ArrowRight } from 'lucide-react';
import { formatLessonTitle } from '../utils/lessonDisplay';

const MOTIVATIONAL = [
  { min: 0,  max: 0,  msg: "Hali hech narsa yo'q — bugun birinchi darsni boshlang! 🚀", emoji: '🚀' },
  { min: 1,  max: 2,  msg: "Zo'r boshladingiz! Davom eting! 💪",                         emoji: '💪' },
  { min: 3,  max: 5,  msg: "Ajoyib! Siz yaxshi yo'ldasiz! ⭐",                            emoji: '⭐' },
  { min: 6,  max: 10, msg: "Wow, juda aktiv o'quvchisiz! 🔥",                             emoji: '🔥' },
  { min: 11, max: Infinity, msg: "Ingliz tili ustasi bo'lyapsiz! 🏆",                     emoji: '🏆' },
];

function getMotivation(count) {
  return MOTIVATIONAL.find((m) => count >= m.min && count <= m.max) || MOTIVATIONAL[0];
}

export default function MyLessonsPage() {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/courses/progress/')
      .then(({ data }) => setProgress(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  const completed = progress.filter((p) => p.status === 'completed');
  const inProgress = progress.filter((p) => p.status === 'in-progress');
  const motivation = getMotivation(progress.length);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-1">Darslarim</h1>
      <p className="text-slate-400 mb-6">Boshlagan va yakunlagan darslaringiz</p>

      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-5 mb-8 text-white flex items-center gap-4 shadow-lg shadow-indigo-500/20">
        <span className="text-4xl">{motivation.emoji}</span>
        <p className="font-semibold text-lg">{motivation.msg}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="student-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 bg-emerald-500/15 rounded-xl flex items-center justify-center">
            <CheckCircle className="text-emerald-400" size={24} />
          </div>
          <div>
            <p className="text-3xl font-extrabold text-emerald-400">{completed.length}</p>
            <p className="text-sm text-slate-400 font-medium">Yakunlangan</p>
          </div>
        </div>
        <div className="student-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-500/15 rounded-xl flex items-center justify-center">
            <Clock className="text-amber-400" size={24} />
          </div>
          <div>
            <p className="text-3xl font-extrabold text-amber-400">{inProgress.length}</p>
            <p className="text-sm text-slate-400 font-medium">Jarayonda</p>
          </div>
        </div>
      </div>

      {progress.length === 0 ? (
        <div className="text-center py-16 student-card">
          <div className="text-6xl mb-4">📖</div>
          <p className="text-xl font-bold text-white mb-2">Hali hech qaysi dars boshlanmagan</p>
          <p className="text-slate-500 mb-6">Bugun birinchi darsni boshlang!</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 admin-btn-primary px-6 py-3"
          >
            Darslarni ko'rish <ArrowRight size={16} />
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {progress.map((p) => {
            const isDone = p.status === 'completed';
            return (
              <div
                key={p.id}
                onClick={() => navigate(`/lessons/${p.lesson}`)}
                className="student-card p-5 flex items-center gap-4 cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
              >
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
                  isDone ? 'bg-emerald-500/15' : 'bg-amber-500/15'
                }`}>
                  {isDone
                    ? <CheckCircle className="text-emerald-400" size={22} />
                    : <Clock className="text-amber-400" size={22} />
                  }
                </div>

                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white truncate">{formatLessonTitle(p.lesson_title)}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <div className="flex-1 bg-surface-200 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-700 ${
                          isDone
                            ? 'bg-gradient-to-r from-emerald-400 to-green-500'
                            : 'bg-gradient-to-r from-amber-400 to-orange-400'
                        }`}
                        style={{ width: `${p.score || 0}%` }}
                      />
                    </div>
                    <span className={`text-xs font-bold shrink-0 ${isDone ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {p.score || 0}%
                    </span>
                  </div>
                </div>

                <span className={`text-xs px-3 py-1.5 rounded-full font-semibold shrink-0 ${
                  isDone ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'
                }`}>
                  {isDone ? 'Yakunlandi' : 'Jarayonda'}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}