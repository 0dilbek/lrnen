import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import api from '../../api';
import {
  ArrowLeft, Loader2, CheckCircle, Clock, User,
  ChevronRight, ClipboardList, KeyRound, Trash2, Eye, EyeOff, X, BookOpen,
} from 'lucide-react';
import { formatLessonTitle } from '../../utils/lessonDisplay';
import StudentActivityTimeline from '../../components/admin/StudentActivityTimeline';

const LEVEL_COLORS = {
  a1: 'bg-green-500/15 text-green-700 dark:text-green-300 border-green-500/30',
  a2: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30',
  b1: 'bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/30',
  b2: 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/30',
  c1: 'bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/30',
  c2: 'bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300 border-fuchsia-500/30',
  ielts: 'bg-orange-500/15 text-orange-700 dark:text-orange-300 border-orange-500/30',
};

function ChangePasswordModal({ student, onClose }) {
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 4) { setError("Kamida 4 ta belgi"); return; }
    setLoading(true); setError('');
    try {
      await api.patch(`/auth/students/${student.id}/`, { password });
      setSuccess(true);
      setTimeout(onClose, 1200);
    } catch { setError('Xatolik yuz berdi'); }
    finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="admin-modal rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold admin-text-title">Parolni yangilash</h2>
          <button onClick={onClose} className="admin-text-muted hover:admin-text-body transition"><X size={20} /></button>
        </div>
        <p className="text-sm admin-text-muted mb-4">
          <span className="font-medium admin-text-body">{student.full_name || student.username}</span> uchun yangi parol
        </p>
        {error && <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-700 dark:text-red-300">{error}</div>}
        {success && <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-700 dark:text-emerald-300">Saqlandi!</div>}
        <form onSubmit={handleSubmit} className="space-y-4 modal-form">
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Yangi parol"
              autoComplete="new-password"
              className="admin-input pr-12"
            />
            <button type="button" onClick={() => setShowPass(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 admin-text-muted hover:admin-text-body" tabIndex={-1}>
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <button type="submit" disabled={loading} className="w-full admin-btn-primary py-3 justify-center">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <KeyRound size={18} />}
            {loading ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
        </form>
      </div>
    </div>
  );
}

function EditLevelsModal({ student, allLevels, onClose, onSaved }) {
  const [selected, setSelected] = useState(student.levels.map((l) => l.id));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggle = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    try {
      await api.patch(`/auth/students/${student.id}/`, { level_ids: selected });
      onSaved(selected);
      onClose();
    } catch {
      setError('Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="admin-modal rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold admin-text-title">Daraja (level) biriktirish</h2>
          <button onClick={onClose} className="admin-text-muted hover:admin-text-body transition"><X size={20} /></button>
        </div>
        <p className="text-sm admin-text-muted mb-4">
          <span className="font-medium admin-text-body">{student.full_name || student.username}</span> uchun daraja tanlang
        </p>

        {error && <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-700 dark:text-red-300">{error}</div>}

        <div className="flex flex-wrap gap-2 mb-6">
          {allLevels.map((lvl) => {
            const active = selected.includes(lvl.id);
            const cls = LEVEL_COLORS[lvl.slug] || 'bg-surface-200 admin-text-body border-border';
            return (
              <button
                key={lvl.id}
                type="button"
                onClick={() => toggle(lvl.id)}
                className={`px-3 py-2 rounded-xl text-sm font-semibold border-2 transition-all ${
                  active
                    ? `${cls} scale-105 shadow-sm`
                    : 'admin-panel-alt admin-text-muted hover:border-indigo-500/40'
                }`}
              >
                {lvl.name}
              </button>
            );
          })}
        </div>

        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-border admin-text-muted text-sm font-semibold hover:bg-surface-200 transition">
            Bekor
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex-1 py-2.5 rounded-xl admin-btn-primary justify-center text-sm"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : null}
            Saqlash
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminStudentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [allLevels, setAllLevels] = useState([]);
  const [quizAttempts, setQuizAttempts] = useState([]);
  const [exerciseAttempts, setExerciseAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showChangePass, setShowChangePass] = useState(false);
  const [showEditLevels, setShowEditLevels] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [savingLanguage, setSavingLanguage] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get(`/auth/students/${id}/`),
      api.get('/courses/levels/'),
      api.get(`/quiz/attempts/?student_id=${id}`),
      api.get(`/quiz/exercise-attempts/?student_id=${id}`),
    ]).then(([studentRes, levelsRes, quizRes, exerciseRes]) => {
      setData(studentRes.data);
      setAllLevels(levelsRes.data);
      setQuizAttempts(quizRes.data);
      setExerciseAttempts(exerciseRes.data);
    }).finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm(`"${data.user.full_name || data.user.username}" o'chirilsinmi? Bu amalni qaytarib bo'lmaydi.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/auth/students/${id}/`);
      navigate('/admin/students');
    } catch {
      alert("O'chirishda xatolik");
      setDeleting(false);
    }
  };

  const handleLevelsSaved = (selectedIds) => {
    const updatedLevels = allLevels.filter((l) => selectedIds.includes(l.id));
    setData((prev) => ({ ...prev, user: { ...prev.user, levels: updatedLevels } }));
  };

  const handleLanguageChange = async (language) => {
    setSavingLanguage(true);
    try {
      const { data: updatedUser } = await api.patch(`/auth/students/${id}/`, { language });
      setData((previous) => ({ ...previous, user: updatedUser }));
    } catch {
      alert('Tilni saqlashda xatolik yuz berdi');
    } finally {
      setSavingLanguage(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="animate-spin text-indigo-400" size={40} /></div>;
  }
  if (!data) return <div className="text-center py-20 admin-text-muted">Topilmadi</div>;

  const { user, progress } = data;
  const selectedLessonId = Number(searchParams.get('lesson')) || null;
  const selectedProgress = progress.find((item) => item.lesson === selectedLessonId);
  const selectedQuizAttempts = quizAttempts.filter((item) => item.lesson === selectedLessonId);
  const selectedExerciseAttempts = exerciseAttempts.filter((item) => item.lesson === selectedLessonId);
  const selectedLessonTitle = selectedProgress?.lesson_title
    || selectedQuizAttempts[0]?.lesson_title
    || selectedExerciseAttempts[0]?.lesson_title;
  const completed = progress.filter((p) => p.status === 'completed').length;
  const avgScore = progress.length
    ? Math.round(progress.reduce((a, b) => a + (b.score || 0), 0) / progress.length)
    : 0;

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:py-8">
      {showChangePass && <ChangePasswordModal student={user} onClose={() => setShowChangePass(false)} />}
      {showEditLevels && (
        <EditLevelsModal
          student={user}
          allLevels={allLevels}
          onClose={() => setShowEditLevels(false)}
          onSaved={handleLevelsSaved}
        />
      )}

      <button onClick={() => navigate('/admin/students')}
        className="flex items-center gap-2 admin-text-muted hover:text-indigo-500 transition mb-6">
        <ArrowLeft size={18} /> Orqaga
      </button>

      <div className="admin-card p-6 mb-6">
        <div className="flex flex-wrap items-start gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-indigo-500/15 text-xl font-bold text-indigo-700 dark:text-indigo-300">
            {(user.full_name || user.username)[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold admin-text-title">{user.full_name || '—'}</h1>
            <p className="admin-text-muted flex items-center gap-1 text-sm mt-0.5">
              <User size={13} /> @{user.username}
            </p>
            <p className="text-xs admin-text-muted mt-0.5">
              Qo'shilgan: {new Date(user.created_at).toLocaleDateString('uz-UZ')}
            </p>
          </div>
          <div className="flex w-full gap-2 sm:w-auto sm:shrink-0">
            <button onClick={() => setShowChangePass(true)}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-indigo-500/30 px-3 py-2 text-sm text-indigo-600 transition hover:bg-indigo-500/10 dark:text-indigo-300 sm:flex-none">
              <KeyRound size={15} /> Parol
            </button>
            <button onClick={handleDelete} disabled={deleting}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-red-500/30 px-3 py-2 text-sm text-red-600 transition hover:bg-red-500/10 disabled:opacity-50 dark:text-red-300 sm:flex-none">
              {deleting ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
              O'chirish
            </button>
          </div>
        </div>

        <div className="mt-5 pt-5 border-t border-border">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold admin-text-body flex items-center gap-1.5">
              <BookOpen size={14} /> Darajalar
            </p>
            <button
              onClick={() => setShowEditLevels(true)}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition"
            >
              Tahrirlash
            </button>
          </div>
          {user.levels?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {user.levels.map((lvl) => {
                const cls = LEVEL_COLORS[lvl.slug] || 'bg-surface-200 admin-text-body border-border';
                return (
                  <span key={lvl.slug} className={`text-xs font-semibold px-3 py-1 rounded-full border ${cls}`}>
                    {lvl.name}
                  </span>
                );
              })}
            </div>
          ) : (
            <p className="text-sm admin-text-muted italic">
              Daraja biriktirilmagan —{' '}
              <button onClick={() => setShowEditLevels(true)} className="text-indigo-400 hover:underline">
                biriktirish
              </button>
            </p>
          )}
        </div>

        <div className="mt-5 flex items-center justify-between gap-4 border-t border-border pt-5">
          <div>
            <p className="text-sm font-semibold admin-text-body">Sayt va kontent tili</p>
            <p className="mt-0.5 text-xs admin-text-muted">Video, dars matni va lug‘atlar shu tilga mos chiqadi.</p>
          </div>
          <select
            value={user.language || 'kaa'}
            onChange={(event) => handleLanguageChange(event.target.value)}
            disabled={savingLanguage}
            className="admin-input !w-auto min-w-36 text-sm"
          >
            <option value="kaa">Qoraqalpoqcha</option>
            <option value="uz">O‘zbekcha</option>
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-5 pt-5 border-t border-border">
          <div className="text-center">
            <p className="text-2xl font-bold admin-text-title">{progress.length}</p>
            <p className="text-xs admin-text-muted mt-0.5">Boshlangan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-emerald-400">{completed}</p>
            <p className="text-xs admin-text-muted mt-0.5">Yakunlangan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-indigo-400">{avgScore}%</p>
            <p className="text-xs admin-text-muted mt-0.5">O'rtacha ball</p>
          </div>
        </div>
      </div>

      <h2 className="font-semibold admin-text-title mb-3">Darslar bo'yicha natijalar</h2>
      {progress.length === 0 ? (
        <div className="text-center py-10 admin-text-muted admin-card">
          Hali birorta dars boshlanmagan
        </div>
      ) : (
        <div className="admin-card overflow-hidden">
          <div className="divide-y divide-border">
            {progress.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setSearchParams({ lesson: String(p.lesson) })}
                className={`flex w-full items-center gap-4 px-4 py-4 text-left transition hover:bg-surface-200/50 sm:px-6 ${selectedLessonId === p.lesson ? 'bg-indigo-500/10' : ''}`}
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  p.status === 'completed' ? 'bg-emerald-500/15' : 'bg-amber-500/15'
                }`}>
                  {p.status === 'completed'
                    ? <CheckCircle size={16} className="text-emerald-400" />
                    : <Clock size={16} className="text-amber-400" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium admin-text-body truncate">{formatLessonTitle(p.lesson_title)}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-surface-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${p.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-400'}`}
                        style={{ width: `${p.score || 0}%` }}
                      />
                    </div>
                    <span className="text-xs admin-text-muted">{p.score || 0}%</span>
                  </div>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  p.status === 'completed' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'
                }`}>
                  {p.status === 'completed' ? 'Yakunlandi' : 'Jarayonda'}
                </span>
                <ChevronRight size={17} className="shrink-0 admin-text-muted" />
              </button>
            ))}
          </div>
        </div>
      )}

      <section className="mt-6">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h2 className="flex items-center gap-2 font-semibold admin-text-title"><ClipboardList size={18} /> Topshiriqlar tarixi</h2>
            <p className="mt-1 text-sm admin-text-muted">
              {selectedLessonId
                ? formatLessonTitle(selectedLessonTitle || 'Tanlangan dars')
                : 'Tekshirish uchun yuqoridagi darslardan birini tanlang.'}
            </p>
          </div>
          {selectedLessonId && (
            <button type="button" onClick={() => setSearchParams({})} className="admin-btn-ghost border border-border">
              <X size={16} /> Yopish
            </button>
          )}
        </div>
        <div className="admin-card p-4 sm:p-5">
          {selectedLessonId ? (
            <StudentActivityTimeline
              quizAttempts={selectedQuizAttempts}
              exerciseAttempts={selectedExerciseAttempts}
            />
          ) : (
            <div className="px-5 py-12 text-center">
              <ClipboardList className="mx-auto admin-text-muted opacity-40" size={38} />
              <p className="mt-3 font-bold admin-text-title">Darsni tanlang</p>
              <p className="mt-1 text-sm admin-text-muted">O‘quvchining bergan javoblari va urinish ballari shu yerda ko‘rinadi.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
