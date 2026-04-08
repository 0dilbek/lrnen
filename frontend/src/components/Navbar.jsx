import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import api from '../api';
import { BookOpen, LayoutDashboard, BookMarked, BarChart2, Trophy, LogOut, Shield, Sun, Moon } from 'lucide-react';

// Avatar ranglari — username bo'yicha deterministik
const AVATAR_COLORS = [
  'from-violet-500 to-purple-600',
  'from-blue-500 to-cyan-500',
  'from-emerald-500 to-teal-500',
  'from-orange-400 to-rose-500',
  'from-pink-500 to-fuchsia-500',
  'from-yellow-400 to-orange-400',
];

function getAvatarColor(username = '') {
  let sum = 0;
  for (let i = 0; i < username.length; i++) sum += username.charCodeAt(i);
  return AVATAR_COLORS[sum % AVATAR_COLORS.length];
}

// Mini doira progress (SVG)
function ProgressRing({ percent, size = 40, stroke = 3 }) {
  const r = (size - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percent / 100) * circ;
  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e5e7eb" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke="url(#pg)" strokeWidth={stroke}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.6s ease' }}
      />
      <defs>
        <linearGradient id="pg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#06b6d4" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [progressPct, setProgressPct] = useState(0);

  useEffect(() => {
    if (user && user.role !== 'admin') {
      api.get('/courses/stats/').then(({ data }) => {
        // overall progress: yakunlangan / boshlangan
        const total = data.total_started || 0;
        const done = data.completed || 0;
        setProgressPct(total > 0 ? Math.round((done / total) * 100) : 0);
      }).catch(() => {});
    }
  }, [user]);

  const handleLogout = () => { logout(); navigate('/login'); };
  const isActive = (path) => location.pathname.startsWith(path);

  if (!user) return null;

  const initials = (user.full_name || user.username || '?')
    .split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase();
  const avatarGrad = getAvatarColor(user.username);

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to={user.role === 'admin' ? '/admin' : '/dashboard'} className="flex items-center gap-2 shrink-0">
          <div className="bg-gradient-to-br from-blue-500 to-violet-600 p-1.5 rounded-xl shadow-sm">
            <BookOpen className="text-white" size={20} />
          </div>
          <span className="font-extrabold text-gray-900 text-lg hidden sm:block">Learn English</span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {user.role === 'admin' ? (
            <>
              <NavLink to="/admin" icon={<LayoutDashboard size={17} />} label="Dashboard" active={location.pathname === '/admin'} />
              <NavLink to="/admin/students" icon={<BarChart2 size={17} />} label="O'quvchilar" active={isActive('/admin/students')} />
              <NavLink to="/admin/lessons" icon={<BookMarked size={17} />} label="Darslar" active={isActive('/admin/lessons')} />
            </>
          ) : (
            <>
              <NavLink to="/dashboard" icon={<LayoutDashboard size={17} />} label="Bosh sahifa" active={location.pathname === '/dashboard'} />
              <NavLink to="/my-lessons" icon={<BookMarked size={17} />} label="Darslarim" active={isActive('/my-lessons')} />
              <NavLink to="/results" icon={<BarChart2 size={17} />} label="Natijalar" active={isActive('/results')} />
              <NavLink to="/leaderboard" icon={<Trophy size={17} />} label="Reyting" active={isActive('/leaderboard')} />
            </>
          )}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Dark mode toggle */}
          <button
            onClick={toggle}
            className="p-2 rounded-xl text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition"
            title={dark ? 'Kunduzgi mavzu' : 'Tungi mavzu'}
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Avatar + progress ring */}
          <div className="relative flex items-center" title={`Progress: ${progressPct}%`}>
            {user.role !== 'admin' && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <ProgressRing percent={progressPct} size={40} stroke={3} />
              </div>
            )}
            <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${avatarGrad} flex items-center justify-center text-white font-bold text-xs shadow-sm select-none`}>
              {user.role === 'admin' ? <Shield size={14} /> : initials}
            </div>
          </div>

          {/* Name */}
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-gray-800 leading-tight">{user.full_name || user.username}</p>
            <p className="text-xs text-gray-400">
              {user.role === 'admin' ? '👑 Admin' : `⭐ ${progressPct}%`}
            </p>
          </div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-500 transition px-3 py-2 rounded-xl hover:bg-red-50"
          >
            <LogOut size={16} />
            <span className="hidden sm:inline">Chiqish</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, icon, label, active }) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-semibold transition ${
        active
          ? 'bg-gradient-to-r from-blue-50 to-violet-50 text-blue-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      {icon}
      <span className="hidden md:inline">{label}</span>
    </Link>
  );
}
