import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, Eye, EyeOff, Loader2 } from 'lucide-react';

const EMOJIS = ['📚', '✏️', '🌍', '🏆', '⭐', '🎯', '💡', '🔥'];

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Login va parolni kiriting');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const user = await login(username.trim(), password);
      navigate(user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login yoki parol noto\'g\'ri');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="always-light min-h-screen bg-gradient-to-br from-violet-100 via-blue-50 to-cyan-100 flex items-center justify-center p-4 relative overflow-hidden">

      {/* Floating emoji background */}
      {EMOJIS.map((emoji, i) => (
        <span
          key={i}
          className="absolute select-none pointer-events-none opacity-20 text-4xl"
          style={{
            top: `${10 + (i * 11) % 80}%`,
            left: `${5 + (i * 13) % 90}%`,
            animation: `float ${3 + (i % 3)}s ease-in-out infinite alternate`,
            animationDelay: `${i * 0.4}s`,
          }}
        >
          {emoji}
        </span>
      ))}

      <style>{`
        @keyframes float {
          from { transform: translateY(0px) rotate(-5deg); }
          to   { transform: translateY(-16px) rotate(5deg); }
        }
      `}</style>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-violet-600 rounded-3xl mb-4 shadow-xl shadow-blue-200">
            <span className="text-4xl">🌍</span>
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Learn English</h1>
          <p className="text-gray-500 mt-2 text-base">Ingliz tilini o'rganishning eng qiziqarli usuli!</p>
        </div>

        {/* Card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl shadow-blue-100 p-8 border border-white">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Xush kelibsiz! 👋</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-4 py-3 mb-5 text-sm flex items-center gap-2">
              <span>❌</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Login</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Loginингizni kiriting"
                  autoComplete="username"
                  className="w-full pl-11 pr-4 py-3.5 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition bg-gray-50 focus:bg-white text-gray-900"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Parol</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Parolingizni kiriting"
                  autoComplete="current-password"
                  className="w-full pl-11 pr-12 py-3.5 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition bg-gray-50 focus:bg-white text-gray-900"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 disabled:opacity-60 text-white font-bold py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 hover:shadow-xl hover:shadow-blue-300 hover:-translate-y-0.5 active:translate-y-0 mt-2"
            >
              {loading ? (
                <><Loader2 className="animate-spin" size={18} /> Kirish...</>
              ) : (
                <>Kirish 🚀</>
              )}
            </button>
          </form>

          <p className="text-center text-xs text-gray-400 mt-6">
            Login va parol o'qituvchi tomonidan beriladi
          </p>
        </div>
      </div>
    </div>
  );
}
