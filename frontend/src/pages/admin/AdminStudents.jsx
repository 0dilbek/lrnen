import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  Loader2, Users, Search, ChevronRight, UserPlus,
  X, Eye, EyeOff, Trash2, KeyRound,
} from 'lucide-react';

const LEVEL_COLORS = {
  a1: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  a2: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
  b1: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  b2: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  c1: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  c2: 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30',
  ielts: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
};

function LevelBadge({ level }) {
  const cls = LEVEL_COLORS[level.slug] || 'bg-surface-200 text-slate-400 border-border';
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {level.name}
    </span>
  );
}

function LevelSelect({ levels, selected, onChange }) {
  const toggle = (id) => {
    onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id]);
  };
  return (
    <div className="flex flex-wrap gap-2">
      {levels.map((lvl) => {
        const active = selected.includes(lvl.id);
        const cls = LEVEL_COLORS[lvl.slug] || 'bg-surface-200 text-slate-400 border-border';
        return (
          <button
            key={lvl.id}
            type="button"
            onClick={() => toggle(lvl.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              active ? cls : 'bg-surface-200 text-slate-500 border-border hover:border-slate-500'
            }`}
          >
            {lvl.name}
          </button>
        );
      })}
    </div>
  );
}

function DarkModal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface-100 border border-border rounded-2xl shadow-2xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-white">{title}</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition">
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function AddStudentModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ full_name: '', username: '', password: '' });
  const [selectedLevels, setSelectedLevels] = useState([]);
  const [levels, setLevels] = useState([]);
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/courses/levels/').then(({ data }) => setLevels(data));
  }, []);

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.full_name.trim() || !form.username.trim() || form.password.length < 4) {
      setError('Barcha maydonlarni to\'ldiring (parol kamida 4 ta belgi)');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const { data } = await api.post('/auth/students/', { ...form, level_ids: selectedLevels });
      onCreated(data);
      onClose();
    } catch (err) {
      const detail = err.response?.data;
      setError(typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DarkModal title="Yangi o'quvchi qo'shish" onClose={onClose}>
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl px-4 py-2 mb-4 text-sm">{error}</div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Ism-familiya *</label>
          <input type="text" value={form.full_name} onChange={set('full_name')} placeholder="Alibek Karimov" className="admin-input" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Login *</label>
          <input type="text" value={form.username} onChange={set('username')} placeholder="alibek2024" autoComplete="off" className="admin-input" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Parol *</label>
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              value={form.password}
              onChange={set('password')}
              placeholder="Kamida 4 ta belgi"
              autoComplete="new-password"
              className="admin-input pr-12"
              required
            />
            <button type="button" onClick={() => setShowPass((v) => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300" tabIndex={-1}>
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>
        {levels.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Daraja</label>
            <LevelSelect levels={levels} selected={selectedLevels} onChange={setSelectedLevels} />
          </div>
        )}
        <button type="submit" disabled={loading} className="admin-btn-primary w-full justify-center !py-3">
          {loading ? <Loader2 className="animate-spin" size={18} /> : <UserPlus size={18} />}
          {loading ? 'Saqlanmoqda...' : "O'quvchi qo'shish"}
        </button>
      </form>
    </DarkModal>
  );
}

function ChangePasswordModal({ student, onClose }) {
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 4) { setError('Parol kamida 4 ta belgi'); return; }
    setLoading(true);
    try {
      await api.patch(`/auth/students/${student.id}/`, { password });
      onClose();
    } catch { setError('Xatolik yuz berdi'); }
    finally { setLoading(false); }
  };

  return (
    <DarkModal title="Parolni yangilash" onClose={onClose}>
      <p className="text-sm text-slate-400 mb-4">
        <span className="text-slate-200">{student.full_name || student.username}</span> uchun yangi parol
      </p>
      {error && <div className="bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl px-4 py-2 mb-4 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input type={showPass ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Yangi parol" className="admin-input pr-12" required />
          <button type="button" onClick={() => setShowPass((v) => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500" tabIndex={-1}>
            {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        <button type="submit" disabled={loading} className="admin-btn-primary w-full justify-center !py-3">
          {loading ? <Loader2 className="animate-spin" size={18} /> : <KeyRound size={18} />}
          Saqlash
        </button>
      </form>
    </DarkModal>
  );
}

export default function AdminStudents() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [changePassFor, setChangePassFor] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/auth/students/').then(({ data }) => setStudents(data)).finally(() => setLoading(false));
  }, []);

  const handleDelete = async (student) => {
    if (!window.confirm(`"${student.full_name || student.username}" o'chirilsinmi?`)) return;
    setDeletingId(student.id);
    try {
      await api.delete(`/auth/students/${student.id}/`);
      setStudents((prev) => prev.filter((s) => s.id !== student.id));
    } catch { alert('O\'chirishda xatolik'); }
    finally { setDeletingId(null); }
  };

  const filtered = students.filter(
    (s) =>
      (s.username || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.full_name || '').toLowerCase().includes(search.toLowerCase()),
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="animate-spin text-indigo-400" size={36} />
      </div>
    );
  }

  return (
    <div className="p-8">
      {showAdd && <AddStudentModal onClose={() => setShowAdd(false)} onCreated={(s) => setStudents((p) => [s, ...p])} />}
      {changePassFor && <ChangePasswordModal student={changePassFor} onClose={() => setChangePassFor(null)} />}

      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-slate-400">Jami: <span className="text-white font-semibold">{students.length}</span> ta</p>
        <button onClick={() => setShowAdd(true)} className="admin-btn-primary">
          <UserPlus size={18} /> O'quvchi qo'shish
        </button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Ism yoki login bo'yicha qidirish..."
          className="admin-input pl-10"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Users size={48} className="mx-auto mb-3 opacity-30" />
          <p>O'quvchilar topilmadi</p>
        </div>
      ) : (
        <div className="admin-card overflow-hidden divide-y divide-border">
          {filtered.map((student) => (
            <div key={student.id} className="px-5 py-4 flex items-center gap-4 hover:bg-surface-200/50 transition group">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-300 font-bold text-sm shrink-0">
                {(student.full_name || student.username)[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0 cursor-pointer" onClick={() => navigate(`/admin/students/${student.id}`)}>
                <p className="font-medium text-white">{student.full_name || '—'}</p>
                <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                  <p className="text-sm text-slate-500">@{student.username}</p>
                  {student.levels?.map((lvl) => <LevelBadge key={lvl.slug} level={lvl} />)}
                </div>
              </div>
              <p className="text-xs text-slate-600 hidden sm:block shrink-0">
                {new Date(student.created_at).toLocaleDateString('uz-UZ')}
              </p>
              <div className="flex items-center gap-1 shrink-0 opacity-60 group-hover:opacity-100 transition">
                <button onClick={() => setChangePassFor(student)} className="admin-btn-ghost !p-2" title="Parol"><KeyRound size={16} /></button>
                <button onClick={() => handleDelete(student)} disabled={deletingId === student.id} className="admin-btn-danger !p-2" title="O'chirish">
                  {deletingId === student.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                </button>
                <button onClick={() => navigate(`/admin/students/${student.id}`)} className="admin-btn-ghost !p-2"><ChevronRight size={16} /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}