import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  BookOpen,
  CheckCheck,
  ChevronRight,
  Circle,
  EyeOff,
  Loader2,
  RefreshCw,
  UserRound,
} from 'lucide-react';
import api from '../../api';
import StudentActivityTimeline from '../../components/admin/StudentActivityTimeline';
import { formatLessonTitle } from '../../utils/lessonDisplay';

const STUDENT_COLORS = [
  { card: 'border-l-indigo-500', avatar: 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300' },
  { card: 'border-l-emerald-500', avatar: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300' },
  { card: 'border-l-amber-500', avatar: 'bg-amber-500/15 text-amber-700 dark:text-amber-300' },
  { card: 'border-l-rose-500', avatar: 'bg-rose-500/15 text-rose-700 dark:text-rose-300' },
  { card: 'border-l-cyan-500', avatar: 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-300' },
  { card: 'border-l-violet-500', avatar: 'bg-violet-500/15 text-violet-700 dark:text-violet-300' },
  { card: 'border-l-orange-500', avatar: 'bg-orange-500/15 text-orange-700 dark:text-orange-300' },
  { card: 'border-l-fuchsia-500', avatar: 'bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300' },
];

function formatDate(value) {
  return new Intl.DateTimeFormat('uz-UZ', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function initials(notification) {
  return (notification.student_name || notification.student_username || '?')
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

function announceCount(count) {
  window.dispatchEvent(new CustomEvent('admin-notifications-updated', { detail: count }));
}

export default function AdminNotifications() {
  const navigate = useNavigate();
  const detailRef = useRef(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [quizAttempts, setQuizAttempts] = useState([]);
  const [exerciseAttempts, setExerciseAttempts] = useState([]);
  const [activityLoading, setActivityLoading] = useState(false);

  const loadNotifications = useCallback(async (quiet = false) => {
    if (!quiet) setLoading(true);
    setError('');
    try {
      const query = filter === 'all' ? '' : `?status=${filter}`;
      const { data } = await api.get(`/quiz/notifications/${query}`);
      setNotifications(data.results || []);
      setUnreadCount(data.unread_count || 0);
      announceCount(data.unread_count || 0);
    } catch {
      setError('Notificationlarni yuklab bo‘lmadi.');
    } finally {
      if (!quiet) setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadNotifications();
    const timer = window.setInterval(() => loadNotifications(true), 20000);
    return () => window.clearInterval(timer);
  }, [loadNotifications]);

  const openNotification = async (notification) => {
    const opened = { ...notification, is_read: true };
    setSelected(opened);
    setActivityLoading(true);
    setQuizAttempts([]);
    setExerciseAttempts([]);

    if (!notification.is_read) {
      try {
        await api.patch(`/quiz/notifications/${notification.id}/`, { is_read: true });
        setNotifications((rows) => rows.map((row) => (
          row.id === notification.id ? { ...row, is_read: true } : row
        )));
        const nextCount = Math.max(0, unreadCount - 1);
        setUnreadCount(nextCount);
        announceCount(nextCount);
      } catch {
        setSelected(notification);
      }
    }

    try {
      const [quizResponse, exerciseResponse] = await Promise.all([
        api.get(`/quiz/attempts/?student_id=${notification.student}&lesson_id=${notification.lesson}`),
        api.get(`/quiz/exercise-attempts/?student_id=${notification.student}&lesson_id=${notification.lesson}`),
      ]);
      setQuizAttempts(quizResponse.data);
      setExerciseAttempts(exerciseResponse.data);
      window.setTimeout(() => detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
    } catch {
      setError('O‘quvchi faolligi tarixini yuklab bo‘lmadi.');
    } finally {
      setActivityLoading(false);
    }
  };

  const markAllRead = async () => {
    try {
      await api.post('/quiz/notifications/read-all/');
      setNotifications((rows) => rows.map((row) => ({ ...row, is_read: true })));
      setUnreadCount(0);
      announceCount(0);
      if (filter === 'unread') setNotifications([]);
    } catch {
      setError('Notificationlarni o‘qilgan deb belgilab bo‘lmadi.');
    }
  };

  const markSelectedUnread = async () => {
    if (!selected?.is_read) return;
    try {
      const { data } = await api.patch(`/quiz/notifications/${selected.id}/`, { is_read: false });
      setSelected(data);
      setNotifications((rows) => rows.map((row) => row.id === data.id ? data : row));
      const nextCount = unreadCount + 1;
      setUnreadCount(nextCount);
      announceCount(nextCount);
    } catch {
      setError('Notification holatini yangilab bo‘lmadi.');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-300"><Bell size={20} /></span>
            <div>
              <p className="font-extrabold admin-text-title">Dars yakunlari</p>
              <p className="text-sm admin-text-muted">{unreadCount} ta ko‘rilmagan notification</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={() => loadNotifications()} className="admin-btn-ghost border border-border" title="Yangilash">
            <RefreshCw size={16} /> Yangilash
          </button>
          <button type="button" onClick={markAllRead} disabled={!unreadCount} className="admin-btn-primary disabled:cursor-not-allowed disabled:opacity-50">
            <CheckCheck size={17} /> Hammasini ko‘rildi
          </button>
        </div>
      </div>

      {error && <div className="mb-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-300">{error}</div>}

      <div className="mb-5 inline-flex rounded-xl border border-border bg-surface-100 p-1">
        {[
          ['all', 'Barchasi'],
          ['unread', `Ko‘rilmagan (${unreadCount})`],
          ['read', 'Ko‘rilgan'],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`rounded-lg px-3 py-2 text-xs font-bold transition ${filter === value ? 'bg-indigo-600 text-white shadow-sm' : 'admin-text-muted hover:bg-surface-200'}`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="grid items-start gap-6 xl:grid-cols-[minmax(320px,.8fr)_minmax(480px,1.2fr)]">
        <section className="space-y-3">
          {loading ? (
            <div className="grid min-h-56 place-items-center"><Loader2 className="animate-spin text-indigo-500" size={32} /></div>
          ) : notifications.length === 0 ? (
            <div className="admin-card px-5 py-14 text-center">
              <CheckCheck className="mx-auto text-emerald-500" size={38} />
              <p className="mt-3 font-extrabold admin-text-title">Notificationlar yo‘q</p>
              <p className="mt-1 text-sm admin-text-muted">Tanlangan filtr bo‘yicha yangi dars yakuni topilmadi.</p>
            </div>
          ) : notifications.map((notification) => {
            const color = STUDENT_COLORS[notification.student_color] || STUDENT_COLORS[0];
            const active = selected?.id === notification.id;
            return (
              <button
                key={notification.id}
                type="button"
                onClick={() => openNotification(notification)}
                className={`w-full rounded-2xl border border-l-4 bg-surface-100 p-4 text-left shadow-card transition hover:-translate-y-0.5 hover:shadow-card-hover ${color.card} ${active ? 'ring-2 ring-indigo-500/30' : ''} ${notification.is_read ? 'opacity-75' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl text-sm font-black ${color.avatar}`}>{initials(notification)}</span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center gap-2">
                      <strong className="truncate text-sm admin-text-title">{notification.student_name}</strong>
                      {!notification.is_read && <Circle size={8} fill="currentColor" className="shrink-0 text-indigo-500" />}
                    </span>
                    <span className="mt-1 block text-sm admin-text-body">
                      <strong>{notification.score}%</strong> bilan darsni yakunladi
                    </span>
                    <span className="mt-1 block truncate text-xs admin-text-muted">{formatLessonTitle(notification.lesson_title)}</span>
                    <span className="mt-2 block text-[11px] admin-text-muted">{formatDate(notification.created_at)}</span>
                  </span>
                  <ChevronRight size={17} className="mt-3 shrink-0 admin-text-muted" />
                </div>
              </button>
            );
          })}
        </section>

        <section ref={detailRef} className="scroll-mt-24">
          {!selected ? (
            <div className="admin-card grid min-h-80 place-items-center p-8 text-center">
              <div>
                <Bell className="mx-auto admin-text-muted opacity-40" size={42} />
                <p className="mt-4 font-extrabold admin-text-title">Notificationni tanlang</p>
                <p className="mt-1 max-w-sm text-sm admin-text-muted">Dars davomida bajarilgan mashqlar va test javoblari shu yerda ochiladi.</p>
              </div>
            </div>
          ) : (
            <div className="admin-card overflow-hidden">
              <div className="border-b border-border bg-surface-200/40 p-5">
                <div className="flex flex-wrap items-start gap-4">
                  <span className={`grid h-12 w-12 place-items-center rounded-2xl text-sm font-black ${STUDENT_COLORS[selected.student_color]?.avatar || STUDENT_COLORS[0].avatar}`}>{initials(selected)}</span>
                  <div className="min-w-0 flex-1">
                    <p className="font-black admin-text-title">{selected.student_name}</p>
                    <p className="mt-0.5 text-sm admin-text-muted">@{selected.student_username}</p>
                    <div className="mt-3 flex items-start gap-2 text-sm admin-text-body">
                      <BookOpen size={16} className="mt-0.5 shrink-0 text-indigo-500" />
                      <span>{formatLessonTitle(selected.lesson_title)} · <strong>{selected.score}%</strong></span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={markSelectedUnread} className="admin-btn-ghost border border-border" title="Ko‘rilmagan deb belgilash">
                      <EyeOff size={16} /> <span className="hidden sm:inline">Ko‘rilmagan</span>
                    </button>
                    <button type="button" onClick={() => navigate(`/admin/students/${selected.student}?lesson=${selected.lesson}`)} className="admin-btn-primary">
                      <UserRound size={16} /> Profil
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-4 sm:p-5">
                <StudentActivityTimeline
                  quizAttempts={quizAttempts}
                  exerciseAttempts={exerciseAttempts}
                  loading={activityLoading}
                />
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
