import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import api from '../api';
import { Search, BookOpen, CheckCircle, Clock, Loader2, Zap, Flame } from 'lucide-react';

// Har bir kategoriya indeksiga qarab rang va emoji
const CARD_THEMES = [
  { gradient: 'from-violet-500 to-purple-600',  pill: 'bg-violet-100 text-violet-700',  emoji: '📚' },
  { gradient: 'from-blue-500 to-cyan-500',       pill: 'bg-blue-100 text-blue-700',      emoji: '✏️' },
  { gradient: 'from-emerald-500 to-teal-500',    pill: 'bg-emerald-100 text-emerald-700',emoji: '🌱' },
  { gradient: 'from-orange-400 to-rose-500',     pill: 'bg-orange-100 text-orange-700',  emoji: '🔥' },
  { gradient: 'from-pink-500 to-fuchsia-500',    pill: 'bg-pink-100 text-pink-700',      emoji: '⭐' },
  { gradient: 'from-yellow-400 to-orange-400',   pill: 'bg-yellow-100 text-yellow-700',  emoji: '🏆' },
  { gradient: 'from-sky-500 to-indigo-500',      pill: 'bg-sky-100 text-sky-700',        emoji: '💡' },
  { gradient: 'from-red-500 to-pink-500',        pill: 'bg-red-100 text-red-700',        emoji: '🎯' },
];

function getTheme(categoryId) {
  return CARD_THEMES[(categoryId ?? 0) % CARD_THEMES.length];
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { xp, streak, badges } = useGame();
  const [categories, setCategories] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get('/courses/categories/'),
      api.get('/courses/lessons/'),
      api.get('/courses/progress/'),
    ]).then(([cats, lsns, prog]) => {
      setCategories(cats.data);
      setLessons(lsns.data);
      const progressMap = {};
      prog.data.forEach((p) => { progressMap[p.lesson] = p; });
      setProgress(progressMap);
    }).finally(() => setLoading(false));
  }, []);

  const [selectedDifficulty, setSelectedDifficulty] = useState('');

  const filtered = lessons.filter((l) => {
    const matchSearch =
      l.title.toLowerCase().includes(search.toLowerCase()) ||
      l.description.toLowerCase().includes(search.toLowerCase());
    const matchCat = !selectedCategory || l.category === Number(selectedCategory);
    const matchDiff = !selectedDifficulty || l.difficulty === selectedDifficulty;
    return matchSearch && matchCat && matchDiff;
  });

  const completedCount = Object.values(progress).filter((p) => p.status === 'completed').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          Salom, {(user?.full_name || user?.username || 'O\'quvchi').split(' ')[0]}! 👋
        </h1>
        <p className="text-gray-500 mb-4">Bugun qaysi darsni o'rganamiz?</p>

        {/* XP / Streak / Badge panel */}
        <div className="flex gap-3 flex-wrap">
          {/* XP */}
          <div className="flex items-center gap-2 bg-violet-50 text-violet-700 px-3 py-1.5 rounded-full text-sm font-semibold border border-violet-100">
            <Zap size={14} className="text-violet-500" />
            {xp} XP
          </div>

          {/* Streak */}
          {streak > 0 && (
            <div className="flex items-center gap-2 bg-orange-50 text-orange-700 px-3 py-1.5 rounded-full text-sm font-semibold border border-orange-100">
              <Flame size={14} className="text-orange-500" />
              {streak} kunlik seria
            </div>
          )}

          {/* Completed */}
          {completedCount > 0 && (
            <div className="flex items-center gap-2 bg-green-50 text-green-700 px-3 py-1.5 rounded-full text-sm font-semibold border border-green-100">
              <CheckCircle size={14} />
              {completedCount} yakunlandi
            </div>
          )}

          {/* In progress */}
          {Object.keys(progress).length - completedCount > 0 && (
            <div className="flex items-center gap-2 bg-yellow-50 text-yellow-700 px-3 py-1.5 rounded-full text-sm font-semibold border border-yellow-100">
              <Clock size={14} />
              {Object.keys(progress).length - completedCount} jarayonda
            </div>
          )}
        </div>

        {/* Badges */}
        {badges.length > 0 && (
          <div className="flex gap-2 mt-3 flex-wrap">
            {badges.map(b => (
              <span
                key={b.id}
                title={b.desc}
                className="inline-flex items-center gap-1.5 bg-white border border-gray-200 text-gray-700 text-xs font-semibold px-2.5 py-1 rounded-full shadow-sm cursor-default"
              >
                {b.emoji} {b.label}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Dars qidirish..."
          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
        />
      </div>

      {/* Category pills */}
      {categories.length > 0 && (
        <div className="flex gap-2 flex-wrap mb-8">
          <button
            onClick={() => setSelectedCategory('')}
            className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all ${
              !selectedCategory
                ? 'bg-gray-900 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Hammasi
          </button>
          {categories.map((c) => {
            const theme = getTheme(c.id);
            const active = selectedCategory === String(c.id);
            return (
              <button
                key={c.id}
                onClick={() => setSelectedCategory(active ? '' : String(c.id))}
                className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all flex items-center gap-1.5 ${
                  active
                    ? `bg-gradient-to-r ${theme.gradient} text-white shadow-sm scale-105`
                    : `${theme.pill} hover:scale-105`
                }`}
              >
                <span>{theme.emoji}</span>
                {c.name}
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${active ? 'bg-white/20' : 'bg-white/60'}`}>
                  {c.lesson_count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Difficulty filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {[
          { val: '',       label: 'Barcha daraja' },
          { val: 'easy',   label: '⭐ Oson'       },
          { val: 'medium', label: '⭐⭐ O\'rta'    },
          { val: 'hard',   label: '⭐⭐⭐ Qiyin'   },
        ].map(({ val, label }) => (
          <button
            key={val}
            onClick={() => setSelectedDifficulty(val)}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all border ${
              selectedDifficulty === val
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-500 border-gray-200 hover:border-gray-400'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Lessons Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-500 text-lg font-medium">Dars topilmadi</p>
          <p className="text-gray-400 text-sm mt-1">Boshqa kalit so'z yoki kategoriya tanlang</p>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-400 mb-4">{filtered.length} ta dars</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((lesson) => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                progress={progress[lesson.id]}
                onClick={() => navigate(`/lessons/${lesson.id}`)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function LessonCard({ lesson, progress, onClick }) {
  const theme = getTheme(lesson.category);
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in-progress';
  const score = progress?.score || 0;

  return (
    <div
      onClick={onClick}
      className="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden hover:-translate-y-1"
    >
      {/* Top banner */}
      <div className={`bg-gradient-to-br ${theme.gradient} h-24 relative flex items-center justify-center`}>
        <span className="text-5xl drop-shadow-sm select-none">{theme.emoji}</span>
        {isCompleted && (
          <div className="absolute top-2 right-2 bg-white/90 rounded-full p-1 shadow-sm">
            <CheckCircle size={16} className="text-green-500" />
          </div>
        )}
        {isInProgress && (
          <div className="absolute top-2 right-2 bg-white/90 rounded-full p-1 shadow-sm">
            <Clock size={16} className="text-yellow-500" />
          </div>
        )}
      </div>

      <div className="p-4">
        {/* Category + difficulty badges */}
        <div className="flex items-center gap-1.5 flex-wrap mb-2">
          <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${theme.pill}`}>
            {lesson.category_name || 'Umumiy'}
          </span>
          {lesson.difficulty && (
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              lesson.difficulty === 'easy'   ? 'bg-green-100 text-green-700' :
              lesson.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                              'bg-red-100 text-red-700'
            }`}>
              {lesson.difficulty === 'easy' ? '⭐' : lesson.difficulty === 'medium' ? '⭐⭐' : '⭐⭐⭐'}
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="font-bold text-gray-900 group-hover:text-blue-700 transition line-clamp-2 text-base leading-snug mb-1">
          {lesson.title}
        </h3>

        {lesson.description && (
          <p className="text-sm text-gray-500 line-clamp-2 mb-3">{lesson.description}</p>
        )}

        {/* Progress */}
        {progress ? (
          <div className="mt-auto">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-500 font-medium">
                {isCompleted ? 'Yakunlandi' : 'Jarayonda'}
              </span>
              <span className={`text-xs font-bold ${isCompleted ? 'text-green-600' : 'text-yellow-600'}`}>
                {score}%
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  isCompleted
                    ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                    : 'bg-gradient-to-r from-yellow-400 to-orange-400'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-1 text-xs text-gray-400 mt-auto">
            <BookOpen size={12} />
            Boshlash uchun bosing
          </div>
        )}
      </div>
    </div>
  );
}
