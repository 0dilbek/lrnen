import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Loader2, Trophy, Target, BookOpen, TrendingUp, ArrowRight } from 'lucide-react';

function getScoreEmoji(avg) {
  if (avg >= 90) return { emoji: '🏆', label: 'Ajoyib natija!',    color: 'from-yellow-400 to-orange-500' };
  if (avg >= 70) return { emoji: '⭐', label: 'Yaxshi natija!',    color: 'from-blue-500 to-violet-600' };
  if (avg >= 50) return { emoji: '💪', label: 'Davom eting!',       color: 'from-emerald-400 to-teal-500' };
  if (avg > 0)   return { emoji: '📚', label: 'Ko\'proq o\'rganing!', color: 'from-pink-500 to-rose-500' };
  return           { emoji: '🚀', label: 'Boshlang!',              color: 'from-gray-400 to-gray-500' };
}

export default function ResultsPage() {
  const [stats, setStats] = useState(null);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get('/courses/stats/'),
      api.get('/courses/progress/'),
    ]).then(([s, p]) => {
      setStats(s.data);
      setProgress(p.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  const avg = stats?.avg_score || 0;
  const scoreInfo = getScoreEmoji(avg);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Natijalarim</h1>
      <p className="text-gray-500 mb-6">Umumiy bilim darajangiz statistikasi</p>

      {/* Score banner */}
      {progress.length > 0 ? (
        <div className={`bg-gradient-to-r ${scoreInfo.color} rounded-2xl p-6 mb-8 text-white flex items-center gap-5 shadow-lg`}>
          <span className="text-5xl">{scoreInfo.emoji}</span>
          <div>
            <p className="text-2xl font-extrabold">{scoreInfo.label}</p>
            <p className="text-white/80 mt-0.5">O'rtacha ballingiz: <strong>{avg}%</strong></p>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100 shadow-sm mb-8">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-xl font-bold text-gray-800 mb-2">Hali natija yo'q</p>
          <p className="text-gray-400 mb-6">Birinchi darsni yakunlang va natijangizni ko'ring!</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-violet-600 text-white px-6 py-3 rounded-2xl font-semibold hover:shadow-lg transition-all hover:-translate-y-0.5 shadow-md shadow-blue-200"
          >
            Darslarni boshlash <ArrowRight size={16} />
          </button>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard icon={<BookOpen size={22} />}  value={stats?.total_started || 0}  label="Boshlangan"  color="blue"   />
        <StatCard icon={<Trophy size={22} />}    value={stats?.completed || 0}       label="Yakunlangan" color="green"  />
        <StatCard icon={<Target size={22} />}    value={`${avg}%`}                   label="O'rtacha ball" color="purple" />
      </div>

      {/* Progress list */}
      {progress.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <TrendingUp size={18} className="text-blue-600" />
              Darslar bo'yicha natijalar
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {progress.map((p) => {
              const isDone = p.status === 'completed';
              const score = p.score || 0;
              return (
                <div
                  key={p.id}
                  onClick={() => navigate(`/lessons/${p.lesson}`)}
                  className="px-6 py-4 flex items-center gap-4 cursor-pointer hover:bg-gray-50 transition"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-800 truncate">{p.lesson_title}</p>
                    <div className="flex items-center gap-3 mt-1.5">
                      <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-700 ${
                            isDone
                              ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                              : 'bg-gradient-to-r from-blue-400 to-violet-500'
                          }`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                      <span className={`text-sm font-bold w-10 text-right shrink-0 ${isDone ? 'text-green-600' : 'text-blue-600'}`}>
                        {score}%
                      </span>
                    </div>
                  </div>
                  <span className={`text-xs px-3 py-1.5 rounded-full font-semibold shrink-0 ${
                    isDone ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {isDone ? '✅ Yakunlandi' : '⏳ Jarayonda'}
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
    blue:   { card: 'bg-blue-50 border-blue-100',   text: 'text-blue-700',   icon: 'bg-blue-100 text-blue-600'   },
    green:  { card: 'bg-green-50 border-green-100', text: 'text-green-700',  icon: 'bg-green-100 text-green-600' },
    purple: { card: 'bg-violet-50 border-violet-100', text: 'text-violet-700', icon: 'bg-violet-100 text-violet-600' },
  };
  const s = styles[color];
  return (
    <div className={`rounded-2xl border p-5 flex items-center gap-4 ${s.card}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${s.icon}`}>
        {icon}
      </div>
      <div>
        <p className={`text-3xl font-extrabold ${s.text}`}>{value}</p>
        <p className={`text-sm font-medium opacity-80 mt-0.5 ${s.text}`}>{label}</p>
      </div>
    </div>
  );
}
