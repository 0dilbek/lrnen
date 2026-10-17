import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiErrorMessage } from '../../api';
import {
  Users, BookOpen, CheckCircle, BarChart2, Loader2, ArrowRight,
  Settings2, X, LockKeyhole, Check, Save,
} from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [releaseSettings, setReleaseSettings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get('/courses/stats/'),
      api.get('/courses/lesson-release-settings/'),
    ]).then(([statsResponse, settingsResponse]) => {
      setStats(statsResponse.data);
      setReleaseSettings(settingsResponse.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="animate-spin text-indigo-400" size={36} />
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Users size={22} />}
          value={stats?.total_students || 0}
          label="O'quvchilar"
          color="indigo"
          to="/admin/students"
        />
        <StatCard
          icon={<BookOpen size={22} />}
          value={stats?.total_lessons || 0}
          label="Darslar"
          color="violet"
          to="/admin/lessons"
        />
        <StatCard
          icon={<BarChart2 size={22} />}
          value={stats?.total_categories || 0}
          label="Kategoriyalar"
          color="cyan"
          to="/admin/lessons"
        />
        <StatCard
          icon={<CheckCircle size={22} />}
          value={stats?.completed || 0}
          label="Yakunlangan"
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="admin-card p-6 flex items-center gap-4 text-left group hover:border-indigo-500/30 transition-all md:col-span-2"
        >
          <div className="rounded-xl bg-amber-500/15 p-3 text-amber-600 transition group-hover:bg-amber-500/25 dark:text-amber-300">
            <Settings2 size={22} />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-semibold admin-text-title">Hozirgi darsni belgilash</p>
            <p className="text-sm admin-text-muted mt-0.5">Har bir darajada o‘quvchilar qaysi darsgacha kira olishini boshqaring</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {releaseSettings.map((level) => (
                <span key={level.id} className="rounded-full border border-border bg-surface-200/70 px-2.5 py-1 text-xs font-bold admin-text-muted">
                  {level.slug.toUpperCase()}: {lessonLabel(level)}
                </span>
              ))}
            </div>
          </div>
          <ArrowRight size={18} className="admin-text-muted transition group-hover:text-indigo-500" />
        </button>
        <QuickLink
          to="/admin/students"
          icon={<Users size={22} />}
          title="O'quvchilar boshqaruvi"
          desc="Yangi o'quvchi qo'shish, parol yangilash, levellar"
        />
        <QuickLink
          to="/admin/lessons"
          icon={<BookOpen size={22} />}
          title="Kontent boshqaruvi"
          desc="48 ta unit — darslar, mashqlar, lug'at, testlar"
        />
      </div>

      {modalOpen && (
        <LessonReleaseModal
          levels={releaseSettings}
          onClose={() => setModalOpen(false)}
          onUpdated={(updated) => setReleaseSettings((levels) => (
            levels.map((level) => level.id === updated.id ? updated : level)
          ))}
        />
      )}
    </div>
  );
}

function lessonLabel(level) {
  if (!level.current_lesson_id) return 'Dars yo‘q';
  const index = level.lessons.findIndex((lesson) => lesson.id === level.current_lesson_id);
  return `${index >= 0 ? index + 1 : '—'}-dars`;
}

function LessonReleaseModal({ levels, onClose, onUpdated }) {
  const firstLevel = levels.find((level) => level.lessons.length) || levels[0];
  const [activeId, setActiveId] = useState(firstLevel?.id || null);
  const activeLevel = levels.find((level) => level.id === activeId) || firstLevel;
  const [selectedId, setSelectedId] = useState(activeLevel?.current_lesson_id || null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setSelectedId(activeLevel?.current_lesson_id || null);
    setError('');
  }, [activeLevel?.id, activeLevel?.current_lesson_id]);

  useEffect(() => {
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [onClose]);

  const save = async () => {
    if (!activeLevel || !selectedId) return;
    setSaving(true);
    setError('');
    try {
      const { data } = await api.patch('/courses/lesson-release-settings/', {
        level_id: activeLevel.id,
        current_lesson_id: selectedId,
      });
      onUpdated(data);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Hozirgi darsni saqlab bo‘lmadi.'));
    } finally {
      setSaving(false);
    }
  };

  const changed = activeLevel && selectedId !== activeLevel.current_lesson_id;

  return (
    <div className="fixed inset-0 z-[100] flex items-end justify-center bg-slate-950/65 p-0 backdrop-blur-sm sm:items-center sm:p-5" role="dialog" aria-modal="true" aria-labelledby="release-modal-title">
      <button type="button" className="absolute inset-0" onClick={onClose} aria-label="Oynani yopish" />
      <div className="admin-card relative flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-t-[1.75rem] shadow-2xl sm:rounded-[1.75rem]">
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-5 sm:px-7">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-xs font-black uppercase tracking-wider text-amber-600 dark:text-amber-300">
              <LockKeyhole size={13} /> Dars chegarasi
            </div>
            <h2 id="release-modal-title" className="text-xl font-black admin-text-title">Hozirgi darsni tanlang</h2>
            <p className="mt-1 text-sm admin-text-muted">Tanlangan dars va undan oldingi mavzular o‘quvchilarga ochiq bo‘ladi.</p>
          </div>
          <button type="button" onClick={onClose} className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-surface-200 admin-text-muted transition hover:text-red-500" aria-label="Yopish">
            <X size={19} />
          </button>
        </div>

        <div className="flex gap-2 overflow-x-auto border-b border-border px-5 py-3 sm:px-7" role="tablist" aria-label="Darajalar">
          {levels.map((level) => (
            <button
              key={level.id}
              type="button"
              role="tab"
              aria-selected={level.id === activeLevel?.id}
              onClick={() => setActiveId(level.id)}
              className={`shrink-0 rounded-xl px-4 py-2 text-sm font-black transition ${level.id === activeLevel?.id ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'bg-surface-200 admin-text-muted hover:text-indigo-500'}`}
            >
              {level.slug.toUpperCase()}
            </button>
          ))}
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-7">
          {!activeLevel?.lessons.length ? (
            <div className="py-12 text-center admin-text-muted">Bu darajaga hali dars biriktirilmagan.</div>
          ) : (
            <div className="grid gap-2 sm:grid-cols-2">
              {activeLevel.lessons.map((lesson, index) => {
                const selected = lesson.id === selectedId;
                const released = index <= activeLevel.lessons.findIndex((item) => item.id === selectedId);
                return (
                  <button
                    key={lesson.id}
                    type="button"
                    onClick={() => setSelectedId(lesson.id)}
                    className={`flex items-center gap-3 rounded-2xl border p-3.5 text-left transition ${selected ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/20' : 'border-border bg-surface-100 hover:border-indigo-500/40'}`}
                  >
                    <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl text-sm font-black ${selected ? 'bg-indigo-600 text-white' : released ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-300' : 'bg-surface-200 admin-text-muted'}`}>
                      {selected ? <Check size={18} strokeWidth={3} /> : index + 1}
                    </span>
                    <span className="min-w-0">
                      <span className="block text-xs font-bold uppercase tracking-wide admin-text-muted">{index + 1}-dars</span>
                      <span className="mt-0.5 block truncate text-sm font-bold admin-text-title">{lesson.title}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          )}
          {error && <p className="mt-4 rounded-xl bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-600 dark:text-red-300">{error}</p>}
        </div>

        <div className="flex items-center justify-between gap-3 border-t border-border px-5 py-4 sm:px-7">
          <p className="hidden text-xs admin-text-muted sm:block">O‘zgarish shu darajadagi barcha o‘quvchilarga darhol ta’sir qiladi.</p>
          <button
            type="button"
            onClick={save}
            disabled={!changed || saving}
            className="ml-auto inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 text-sm font-black text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? <Loader2 size={17} className="animate-spin" /> : <Save size={17} />}
            Saqlash
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, value, label, color, to }) {
  const gradients = {
    indigo: 'from-indigo-500/20 to-indigo-600/5 border-indigo-500/20 text-indigo-700 dark:text-indigo-300',
    violet: 'from-violet-500/20 to-violet-600/5 border-violet-500/20 text-violet-700 dark:text-violet-300',
    cyan: 'from-cyan-500/20 to-cyan-600/5 border-cyan-500/20 text-cyan-700 dark:text-cyan-300',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20 text-emerald-700 dark:text-emerald-300',
  };

  const inner = (
    <div className={`stat-card bg-gradient-to-br ${gradients[color]} border`}>
      <div className={`inline-flex p-2.5 rounded-xl bg-surface-200 mb-4 ${gradients[color].split(' ').pop()}`}>
        {icon}
      </div>
      <p className="text-3xl font-bold admin-text-title">{value}</p>
      <p className="text-sm admin-text-muted mt-1">{label}</p>
    </div>
  );

  return to ? <Link to={to} className="block">{inner}</Link> : inner;
}

function QuickLink({ to, icon, title, desc }) {
  return (
    <Link
      to={to}
      className="admin-card p-6 flex items-center gap-4 group hover:border-indigo-500/30 transition-all"
    >
      <div className="rounded-xl bg-indigo-500/15 p-3 text-indigo-700 transition group-hover:bg-indigo-500/25 dark:text-indigo-300">
        {icon}
      </div>
      <div className="flex-1">
        <p className="font-semibold admin-text-title">{title}</p>
        <p className="text-sm admin-text-muted mt-0.5">{desc}</p>
      </div>
      <ArrowRight size={18} className="admin-text-muted transition group-hover:text-indigo-500" />
    </Link>
  );
}
