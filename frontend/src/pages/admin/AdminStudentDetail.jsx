import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  ArrowLeft, Loader2, CheckCircle, Clock, User,
  KeyRound, Trash2, Eye, EyeOff, X,
} from 'lucide-react';

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
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Parolni yangilash</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition"><X size={20} /></button>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          <span className="font-medium text-gray-700">{student.full_name || student.username}</span> uchun yangi parol
        </p>
        {error && <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 mb-4 text-sm">{error}</div>}
        {success && <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-2 mb-4 text-sm">Saqlandi!</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Yangi parol"
              autoComplete="new-password"
              className="w-full pr-12 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
            <button type="button" onClick={() => setShowPass(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <KeyRound size={18} />}
            {loading ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function AdminStudentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showChangePass, setShowChangePass] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    api.get(`/auth/students/${id}/`).then(({ data }) => setData(data)).finally(() => setLoading(false));
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

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="animate-spin text-blue-600" size={40} /></div>;
  }
  if (!data) return <div className="text-center py-20 text-gray-400">Topilmadi</div>;

  const { user, progress } = data;
  const completed = progress.filter((p) => p.status === 'completed').length;
  const avgScore = progress.length
    ? Math.round(progress.reduce((a, b) => a + (b.score || 0), 0) / progress.length)
    : 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {showChangePass && <ChangePasswordModal student={user} onClose={() => setShowChangePass(false)} />}

      <button onClick={() => navigate('/admin/students')}
        className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition mb-6">
        <ArrowLeft size={18} /> Orqaga
      </button>

      {/* Profile */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xl shrink-0">
            {(user.full_name || user.username)[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-gray-900">{user.full_name || '—'}</h1>
            <p className="text-gray-500 flex items-center gap-1 text-sm mt-0.5">
              <User size={13} /> @{user.username}
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              Qo'shilgan: {new Date(user.created_at).toLocaleDateString('uz-UZ')}
            </p>
          </div>
          {/* Actions */}
          <div className="flex gap-2 shrink-0">
            <button onClick={() => setShowChangePass(true)}
              className="flex items-center gap-1.5 text-sm text-blue-600 border border-blue-200 hover:bg-blue-50 px-3 py-2 rounded-xl transition">
              <KeyRound size={15} /> Parol
            </button>
            <button onClick={handleDelete} disabled={deleting}
              className="flex items-center gap-1.5 text-sm text-red-600 border border-red-200 hover:bg-red-50 px-3 py-2 rounded-xl transition disabled:opacity-50">
              {deleting ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
              O'chirish
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-100">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{progress.length}</p>
            <p className="text-xs text-gray-500 mt-0.5">Boshlangan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-700">{completed}</p>
            <p className="text-xs text-gray-500 mt-0.5">Yakunlangan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-700">{avgScore}%</p>
            <p className="text-xs text-gray-500 mt-0.5">O'rtacha ball</p>
          </div>
        </div>
      </div>

      {/* Progress */}
      <h2 className="font-semibold text-gray-800 mb-3">Darslar bo'yicha natijalar</h2>
      {progress.length === 0 ? (
        <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-gray-100">
          Hali birorta dars boshlanmagan
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-50">
            {progress.map((p) => (
              <div key={p.id} className="px-6 py-4 flex items-center gap-4">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  p.status === 'completed' ? 'bg-green-100' : 'bg-yellow-100'
                }`}>
                  {p.status === 'completed'
                    ? <CheckCircle size={16} className="text-green-600" />
                    : <Clock size={16} className="text-yellow-600" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{p.lesson_title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${p.status === 'completed' ? 'bg-green-500' : 'bg-yellow-400'}`}
                        style={{ width: `${p.score || 0}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{p.score || 0}%</span>
                  </div>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  p.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
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
