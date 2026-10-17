import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Loader2, Trophy, Target, BookOpen, TrendingUp, ArrowRight } from 'lucide-react';
import { formatLessonTitle } from '../utils/lessonDisplay';
import { useLanguage } from '../context/LanguageContext';

function getScoreEmoji(avg, t) {
  if (avg >= 90) return { emoji: '🏆', label: t('Ajoyib natija!'),    color: 'from-yellow-400 to-orange-500' };
  if (avg >= 70) return { emoji: '⭐', label: t('Yaxshi natija!'),    color: 'from-indigo-500 to-violet-600' };
  if (avg >= 50) return { emoji: '💪', label: t('Davom eting!'),       color: 'from-emerald-400 to-teal-500' };
  if (avg > 0)   return { emoji: '📚', label: 'Ko\'proq o\'rganing!', color: 'from-pink-500 to-rose-500' };
  return           { emoji: '🚀', label: t('Boshlang!'),              color: 'from-slate-500 to-slate-600' };
}

export default function ResultsPage() {
  const [stats, setStats] = useState(null);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const { language, t } = useLanguage();
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get('/courses/stats/'),
      api.get('/courses/progress/'),
    ]).then(([s, p]) => {
      setStats(s.data);
      setProgress(p.data);
    }).finally(() => setLoading(false));
  }, [language]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  const avg = stats?.avg_score || 0;
  const scoreInfo = getScoreEmoji(avg, t);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold stu-title mb-1">{t('Natijalarim')}</h1>
      <p className="stu-muted mb-6">{t('Umumiy bilim darajangiz statistikasi')}</p>

      {progress.length > 0 ? (
        <div className={`bg-gradient-to-r ${scoreInfo.color} rounded-2xl p-6 mb-8 text-white flex items-center gap-5 shadow-lg`}>
          <span className="text-5xl">{scoreInfo.emoji}</span>
          <div>
            <p className="text-2xl font-extrabold">{scoreInfo.label}</p>
            <p className="text-white/80 mt-0.5">{t('O‘rtacha ballingiz:')} <strong>{avg}%</strong></p>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 student-card mb-8">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-xl font-bold stu-title mb-2">{t("Hali natija yo'q")}</p>
          <p className="mb-6 stu-muted">{t('Birinchi darsni yakunlang va natijangizni ko‘ring!')}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 admin-btn-primary px-6 py-3"
          >
            {t('Darslarni boshlash')} <ArrowRight size={16} />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard icon={<BookOpen size={22} />}  value={stats?.total_started || 0}  label={t('Boshlangan')}  color="indigo" />
        <StatCard icon={<Trophy size={22} />}    value={stats?.completed || 0}       label={t('Yakunlangan')} color="emerald" />
        <StatCard icon={<Target size={22} />}    value={`${avg}%`}                   label={t("O'rtacha ball")} color="violet" />
      </div>

      {progress.length > 0 && (
        <div className="student-card overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="font-semibold stu-title flex items-center gap-2">
              <TrendingUp size={18} className="text-indigo-400" />
              {t("Darslar bo'yicha natijalar")}
            </h2>
          </div>
          <div className="divide-y divide-border">
            {progress.map((p) => {
              const isDone = p.status === 'completed';
              const score = p.score || 0;
              return (
                <div
                  key={p.id}
                  onClick={() => navigate(`/lessons/${p.lesson}`)}
                  className="px-6 py-4 flex items-center gap-4 cursor-pointer hover:bg-surface-200/40 transition"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium stu-title truncate">{formatLessonTitle(p.lesson_title)}</p>
                    <div className="flex items-center gap-3 mt-1.5">
                      <div className="flex-1 bg-surface-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-700 ${
                            isDone
                              ? 'bg-gradient-to-r from-emerald-400 to-green-500'
                              : 'bg-gradient-to-r from-indigo-400 to-violet-500'
                          }`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                      <span className={`w-10 shrink-0 text-right text-sm font-bold ${isDone ? 'text-emerald-600 dark:text-emerald-300' : 'text-indigo-600 dark:text-indigo-300'}`}>
                        {score}%
                      </span>
                    </div>
                  </div>
                  <span className={`text-xs px-3 py-1.5 rounded-full font-semibold shrink-0 ${
                    isDone ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300' : 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300'
                  }`}>
                    {isDone ? t('Yakunlandi') : t('Jarayonda')}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, value, label, color }) {
  const styles = {
    indigo:  { card: 'bg-indigo-500/10 border-indigo-500/20', text: 'text-indigo-700 dark:text-indigo-300', icon: 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300' },
    emerald: { card: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-700 dark:text-emerald-300', icon: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300' },
    violet:  { card: 'bg-violet-500/10 border-violet-500/20', text: 'text-violet-700 dark:text-violet-300', icon: 'bg-violet-500/15 text-violet-700 dark:text-violet-300' },
  };
  const s = styles[color];
  return (
    <div className={`rounded-2xl border p-5 flex items-center gap-4 ${s.card}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${s.icon}`}>
        {icon}
      </div>
      <div>
        <p className={`text-3xl font-extrabold ${s.text}`}>{value}</p>
        <p className="mt-0.5 text-sm font-medium stu-muted">{label}</p>
      </div>
    </div>
  );
}
