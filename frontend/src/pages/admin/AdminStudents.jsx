import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  Loader2, Users, Search, ChevronRight, UserPlus,
  X, Eye, EyeOff, Trash2, KeyRound,
} from 'lucide-react';

const LEVEL_COLORS = {
  a1: 'bg-green-100 text-green-700',
  a2: 'bg-emerald-100 text-emerald-700',
  b1: 'bg-blue-100 text-blue-700',
  b2: 'bg-indigo-100 text-indigo-700',
  c1: 'bg-purple-100 text-purple-700',
  c2: 'bg-fuchsia-100 text-fuchsia-700',
  ielts: 'bg-orange-100 text-orange-700',
};

function LevelBadge({ level }) {
  const cls = LEVEL_COLORS[level.slug] || 'bg-gray-100 text-gray-700';
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}>
      {level.name}
    </span>
  );
}

// ── Level multi-select component ──────────────────────────────────────────────
function LevelSelect({ levels, selected, onChange }) {
  const toggle = (id) => {
    if (selected.includes(id)) {
      onChange(selected.filter((x) => x !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {levels.map((lvl) => {
        const active = selected.includes(lvl.id);
        const cls = LEVEL_COLORS[lvl.slug] || 'bg-gray-100 text-gray-700';
        return (
          <button
            key={lvl.id}
            type="button"
            onClick={() => toggle(lvl.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border-2 transition-all ${
              active
                ? `${cls} border-current scale-105 shadow-sm`
                : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'
            }`}
          >
            {lvl.name}
          </button>
        );
      })}
    </div>
  );
}

// ── Modal: O'quvchi qo'shish ──────────────────────────────────────────────────
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
      const { data } = await api.post('/auth/students/', {
        ...form,
        level_ids: selectedLevels,
      });
      onCreated(data);
      onClose();
    } catch (err) {
      const detail = err.response?.data;
      if (typeof detail === 'object') {
        const msg = Object.values(detail).flat().join(' ');
        setError(msg);
      } else {
        setError('Xatolik yuz berdi');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-gray-900">Yangi o'quvchi qo'shish</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition">
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ism-familiya <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.full_name}
              onChange={set('full_name')}
              placeholder="Masalan: Alibek Karimov"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Login (username) <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.username}
              onChange={set('username')}
              placeholder="Masalan: alibek2024"
              autoComplete="off"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parol <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={form.password}
                onChange={set('password')}
                placeholder="Kamida 4 ta belgi"
                autoComplete="new-password"
                className="w-full pr-12 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                required
              />
              <button
                type="button"
                onClick={() => setShowPass((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                tabIndex={-1}
              >
                {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {form.password && (
              <div className="mt-1.5 flex gap-1">
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    className={`h-1 flex-1 rounded-full transition-colors ${
                      form.password.length > i * 2
                        ? form.password.length >= 8
                          ? 'bg-green-500'
                          : form.password.length >= 6
                          ? 'bg-yellow-400'
                          : 'bg-red-400'
                        : 'bg-gray-200'
                    }`}
                  />
                ))}
                <span className="text-xs text-gray-400 ml-1">
                  {form.password.length >= 8 ? 'Kuchli' : form.password.length >= 6 ? "O'rta" : 'Zaif'}
                </span>
              </div>
            )}
          </div>

          {/* Level tanlov */}
          {levels.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daraja (level)
                {selectedLevels.length > 0 && (
                  <span className="ml-2 text-xs text-blue-600 font-normal">
                    {selectedLevels.length} ta tanlandi
                  </span>
                )}
              </label>
              <LevelSelect
                levels={levels}
                selected={selectedLevels}
                onChange={setSelectedLevels}
              />
              <p className="text-xs text-gray-400 mt-2">
                Tanlangan levellar bo'yicha darslar ko'rsatiladi
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <UserPlus size={18} />}
            {loading ? 'Saqlanmoqda...' : "O'quvchi qo'shish"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Modal: Parol yangilash ────────────────────────────────────────────────────
function ChangePasswordModal({ student, onClose, onUpdated }) {
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 4) {
      setError('Parol kamida 4 ta belgi bo\'lishi kerak');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await api.patch(`/auth/students/${student.id}/`, { password });
      onUpdated();
      onClose();
    } catch {
      setError('Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Parolni yangilash</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition">
            <X size={20} />
          </button>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          <span className="font-medium text-gray-700">{student.full_name || student.username}</span> uchun yangi parol
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Yangi parol"
              autoComplete="new-password"
              className="w-full pr-12 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              required
            />
            <button
              type="button"
              onClick={() => setShowPass((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
              tabIndex={-1}
            >
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <KeyRound size={18} />}
            {loading ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Asosiy sahifa ─────────────────────────────────────────────────────────────
export default function AdminStudents() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [changePassFor, setChangePassFor] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  const fetchStudents = () => {
    api.get('/auth/students/').then(({ data }) => setStudents(data)).finally(() => setLoading(false));
  };

  useEffect(() => { fetchStudents(); }, []);

  const handleDelete = async (student) => {
    if (!window.confirm(`"${student.full_name || student.username}" o'chirilsinmi?`)) return;
    setDeletingId(student.id);
    try {
      await api.delete(`/auth/students/${student.id}/`);
      setStudents((prev) => prev.filter((s) => s.id !== student.id));
    } catch {
      alert('O\'chirishda xatolik yuz berdi');
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = students.filter(
    (s) =>
      (s.username || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.full_name || '').toLowerCase().includes(search.toLowerCase()),
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {showAdd && (
        <AddStudentModal
          onClose={() => setShowAdd(false)}
          onCreated={(s) => setStudents((prev) => [s, ...prev])}
        />
      )}
      {changePassFor && (
        <ChangePasswordModal
          student={changePassFor}
          onClose={() => setChangePassFor(null)}
          onUpdated={() => {}}
        />
      )}

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">O'quvchilar</h1>
          <p className="text-gray-500">Jami: {students.length} ta o'quvchi</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2.5 rounded-xl transition shadow-sm"
        >
          <UserPlus size={18} />
          O'quvchi qo'shish
        </button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Ism yoki login bo'yicha qidirish..."
          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Users size={48} className="mx-auto mb-3 opacity-50" />
          <p>O'quvchilar topilmadi</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-50">
            {filtered.map((student) => (
              <div key={student.id} className="px-6 py-4 flex items-center gap-4 hover:bg-gray-50 transition">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm shrink-0">
                  {(student.full_name || student.username)[0].toUpperCase()}
                </div>

                {/* Info — click to detail */}
                <div
                  className="flex-1 min-w-0 cursor-pointer"
                  onClick={() => navigate(`/admin/students/${student.id}`)}
                >
                  <p className="font-medium text-gray-900">{student.full_name || '—'}</p>
                  <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                    <p className="text-sm text-gray-500">@{student.username}</p>
                    {student.levels?.length > 0 && (
                      <div className="flex gap-1 flex-wrap">
                        {student.levels.map((lvl) => (
                          <LevelBadge key={lvl.slug} level={lvl} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <p className="text-xs text-gray-400 hidden sm:block shrink-0">
                  {new Date(student.created_at).toLocaleDateString('uz-UZ')}
                </p>

                {/* Actions */}
                <div className="flex items-center gap-1 shrink-0">
                  <button
                    onClick={() => setChangePassFor(student)}
                    title="Parolni yangilash"
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                  >
                    <KeyRound size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(student)}
                    disabled={deletingId === student.id}
                    title="O'chirish"
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                  >
                    {deletingId === student.id
                      ? <Loader2 size={16} className="animate-spin" />
                      : <Trash2 size={16} />
                    }
                  </button>
                  <button
                    onClick={() => navigate(`/admin/students/${student.id}`)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
