import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useGame } from '../context/GameContext';
import api from '../api';
import { BookOpen, LayoutDashboard, BookMarked, BarChart2, Trophy, LogOut, Sun, Moon, Zap } from 'lucide-react';

const AVATAR_COLORS = [
  'from-violet-500 to-purple-600',
  'from-blue-500 to-cyan-500',
  'from-emerald-500 to-teal-500',
  'from-orange-400 to-rose-500',
  'from-pink-500 to-fuchsia-500',
  'from-yellow-400 to-orange-400',
];

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Bosh sahifa', exact: true },
  { to: '/my-lessons', icon: BookMarked, label: 'Darslarim' },
  { to: '/results', icon: BarChart2, label: 'Natijalar' },
  { to: '/leaderboard', icon: Trophy, label: 'Reyting' },
];

function getAvatarColor(username = '') {
  let sum = 0;
  for (let i = 0; i < username.length; i++) sum += username.charCodeAt(i);
  return AVATAR_COLORS[sum % AVATAR_COLORS.length];
}

function ProgressRing({ percent, size = 36, stroke = 2.5 }) {
  const r = (size - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percent / 100) * circ;
  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--ring-track)" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke="url(#navRing)" strokeWidth={stroke}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.6s ease' }}
      />
      <defs>
        <linearGradient id="navRing" x1="0%" y1="0%" x2="100%" y2="0%">
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
  const { xp } = useGame();
  const navigate = useNavigate();
  const location = useLocation();
  const [progressPct, setProgressPct] = useState(0);

  useEffect(() => {
    if (user && user.role !== 'admin') {
      api.get('/courses/stats/').then(({ data }) => {
        const total = data.total_started || 0;
        const done = data.completed || 0;
        setProgressPct(total > 0 ? Math.round((done / total) * 100) : 0);
      }).catch(() => {});
    }
  }, [user]);

  const handleLogout = () => { logout(); navigate('/login'); };

  if (!user || user.role === 'admin') return null;

  const initials = (user.full_name || user.username || '?')
    .split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase();
  const avatarGrad = getAvatarColor(user.username);

  return (
    <nav className="student-nav">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">

        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-2.5 shrink-0">
          <div className="bg-gradient-to-br from-indigo-500 to-violet-600 p-1.5 rounded-xl shadow-md shadow-indigo-500/25">
            <BookOpen className="text-white" size={18} />
          </div>
          <span className="font-extrabold stu-title text-base hidden sm:block tracking-tight">Learn English</span>
        </Link>

        {/* Desktop nav — markazda */}
        <div className="hidden md:flex flex-1 items-center justify-center">
          <div className="flex items-center gap-0.5 bg-surface-200/60 rounded-2xl p-1 border border-border">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = item.exact
                ? location.pathname === item.to
                : location.pathname.startsWith(item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold transition-all ${
                    active
                      ? 'bg-surface-100 text-indigo-600 shadow-sm border border-border'
                      : 'stu-muted hover:stu-body hover:bg-surface-100/60'
                  }`}
                >
                  <Icon size={15} />
                  <span className="hidden lg:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* O'ng panel */}
        <div className="flex items-center gap-1.5 ml-auto shrink-0">
          {/* XP */}
          <div className="hidden sm:flex items-center gap-1 bg-violet-500/10 text-violet-600 dark:text-violet-300 px-2.5 py-1 rounded-full text-xs font-bold border border-violet-500/20">
            <Zap size={12} />
            {xp}
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggle}
            className="p-2 rounded-xl stu-muted hover:stu-body hover:bg-surface-200 transition"
            title={dark ? 'Kunduzgi rejim' : 'Tungi rejim'}
          >
            {dark ? <Sun size={17} /> : <Moon size={17} />}
          </button>

          {/* Avatar + progress */}
          <div className="relative flex items-center" title={`Progress: ${progressPct}%`}>
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <ProgressRing percent={progressPct} />
            </div>
            <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${avatarGrad} flex items-center justify-center text-white font-bold text-[10px] shadow-sm select-none`}>
              {initials}
            </div>
          </div>

          <div className="text-right hidden lg:block min-w-0">
            <p className="text-sm font-semibold stu-title leading-tight truncate max-w-[120px]">
              {(user.full_name || user.username).split(' ')[0]}
            </p>
            <p className="text-[10px] stu-muted">{progressPct}% bajarildi</p>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-sm stu-muted hover:text-red-500 transition px-2.5 py-2 rounded-xl hover:bg-red-500/10"
          >
            <LogOut size={15} />
            <span className="hidden xl:inline">Chiqish</span>
          </button>
        </div>
      </div>
    </nav>
  );
}