import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  ArrowLeft, Loader2, CheckCircle, Clock, User,
  KeyRound, Trash2, Eye, EyeOff, X, BookOpen,
} from 'lucide-react';
import { formatLessonTitle } from '../../utils/lessonDisplay';

const LEVEL_COLORS = {
  a1: 'bg-green-500/15 text-green-400 border-green-500/30',
  a2: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  b1: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  b2: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
  c1: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
  c2: 'bg-fuchsia-500/15 text-fuchsia-400 border-fuchsia-500/30',
  ielts: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
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
        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg px-4 py-2 mb-4 text-sm">{error}</div>}
        {success && <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg px-4 py-2 mb-4 text-sm">Saqlandi!</div>}
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

        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg px-4 py-2 mb-4 text-sm">{error}</div>}

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
  const [data, setData] = useState(null);
  const [allLevels, setAllLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showChangePass, setShowChangePass] = useState(false);
  const [showEditLevels, setShowEditLevels] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get(`/auth/students/${id}/`),
      api.get('/courses/levels/'),
    ]).then(([studentRes, levelsRes]) => {
      setData(studentRes.data);
      setAllLevels(levelsRes.data);
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

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="animate-spin text-indigo-400" size={40} /></div>;
  }
  if (!data) return <div className="text-center py-20 admin-text-muted">Topilmadi</div>;

  const { user, progress } = data;
  const completed = progress.filter((p) => p.status === 'completed').length;
  const avgScore = progress.length
    ? Math.round(progress.reduce((a, b) => a + (b.score || 0), 0) / progress.length)
    : 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
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
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xl shrink-0">
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
          <div className="flex gap-2 shrink-0">
            <button onClick={() => setShowChangePass(true)}
              className="flex items-center gap-1.5 text-sm text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/10 px-3 py-2 rounded-xl transition">
              <KeyRound size={15} /> Parol
            </button>
            <button onClick={handleDelete} disabled={deleting}
              className="flex items-center gap-1.5 text-sm text-red-400 border border-red-500/30 hover:bg-red-500/10 px-3 py-2 rounded-xl transition disabled:opacity-50">
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
              <div key={p.id} className="px-6 py-4 flex items-center gap-4">
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
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}