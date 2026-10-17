import { useEffect, useRef, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  BookOpen, LayoutDashboard, BookMarked, BarChart2, Trophy,
  LogOut, Sun, Moon, Zap, ChevronDown, UserRound,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useGame } from '../context/GameContext';
import api from '../api';
import LanguageSwitcher from './LanguageSwitcher';
import { useLanguage } from '../context/LanguageContext';

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
  { to: '/my-lessons', icon: BookMarked, label: 'Darslarim', lessonRoute: true },
  { to: '/results', icon: BarChart2, label: 'Natijalar' },
  { to: '/leaderboard', icon: Trophy, label: 'Reyting' },
];

function getAvatarColor(username = '') {
  let sum = 0;
  for (let i = 0; i < username.length; i += 1) sum += username.charCodeAt(i);
  return AVATAR_COLORS[sum % AVATAR_COLORS.length];
}

function ProgressRing({ percent, size = 38, stroke = 2.5 }) {
  const radius = (size - stroke * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;
  return (
    <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--ring-track)" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#6366f1"
        strokeWidth={stroke}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.6s ease' }}
      />
    </svg>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const { xp } = useGame();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const menuRef = useRef(null);
  const [progressPct, setProgressPct] = useState(0);
  const [profileOpen, setProfileOpen] = useState(false);

  useEffect(() => {
    if (user && user.role !== 'admin') {
      api.get('/courses/stats/').then(({ data }) => {
        const total = data.total_started || 0;
        const done = data.completed || 0;
        setProgressPct(total > 0 ? Math.round((done / total) * 100) : 0);
      }).catch(() => {});
    }
  }, [user, location.pathname]);

  useEffect(() => {
    setProfileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const closeOnOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) setProfileOpen(false);
    };
    document.addEventListener('pointerdown', closeOnOutside);
    return () => document.removeEventListener('pointerdown', closeOnOutside);
  }, []);

  if (!user || user.role === 'admin') return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  const initials = (user.full_name || user.username || '?')
    .split(' ').map((word) => word[0]).slice(0, 2).join('').toUpperCase();
  const avatarGrad = getAvatarColor(user.username);

  return (
    <nav className="student-nav" aria-label={t('Bosh sahifa')}>
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-3 sm:px-5">
        <Link to="/dashboard" className="group flex shrink-0 items-center gap-2.5 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-md shadow-indigo-500/25 transition-transform group-hover:-rotate-3 group-hover:scale-105">
            <BookOpen className="text-white" size={19} />
          </span>
          <span className="hidden sm:block">
            <span className="block text-sm font-black leading-tight stu-title">Learn English</span>
            <span className="block text-[10px] font-bold uppercase tracking-[.16em] text-indigo-500 dark:text-indigo-300">{t('O‘quv platformasi')}</span>
          </span>
        </Link>

        <div className="hidden min-w-0 flex-1 items-center justify-center md:flex">
          <div className="flex items-center gap-1 rounded-2xl border border-border bg-surface-200/70 p-1.5 shadow-inner">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = item.exact
                ? location.pathname === item.to
                : location.pathname.startsWith(item.to)
                  || (item.lessonRoute && location.pathname.startsWith('/lessons/'));
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  aria-current={active ? 'page' : undefined}
                  className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold transition-all lg:px-4 ${
                    active
                      ? 'bg-surface-100 text-indigo-600 shadow-card ring-1 ring-indigo-500/10 dark:text-indigo-300'
                      : 'stu-muted hover:bg-surface-100/80 hover:text-[color:var(--text-primary)]'
                  }`}
                >
                  <Icon size={17} />
                  <span>{t(item.label)}</span>
                </Link>
              );
            })}
          </div>
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-1.5">
          <LanguageSwitcher compact />
          <div className="flex items-center gap-1.5 rounded-xl border border-violet-500/20 bg-violet-500/10 px-2.5 py-2 text-xs font-black text-violet-700 dark:text-violet-300" title="Tajriba ballari">
            <Zap size={14} />
            <span>{xp}</span>
            <span className="hidden sm:inline">XP</span>
          </div>

          <button
            type="button"
            onClick={toggle}
            className="grid h-10 w-10 place-items-center rounded-xl stu-muted transition hover:bg-surface-200 hover:text-[color:var(--text-primary)] focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            title={dark ? t('Kunduzgi rejim') : t('Tungi rejim')}
            aria-label={dark ? t('Kunduzgi rejim') : t('Tungi rejim')}
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setProfileOpen((open) => !open)}
              className="flex h-11 items-center gap-2 rounded-2xl border border-transparent px-1.5 transition hover:border-border hover:bg-surface-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 sm:pr-2.5"
              aria-expanded={profileOpen}
              aria-haspopup="menu"
            >
              <span className="relative grid h-9 w-9 place-items-center">
                <span className="absolute inset-0 grid place-items-center"><ProgressRing percent={progressPct} /></span>
                <span className={`grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br ${avatarGrad} text-[10px] font-black text-white shadow-sm`}>
                  {initials}
                </span>
              </span>
              <span className="hidden max-w-28 text-left lg:block">
                <span className="block truncate text-sm font-bold leading-tight stu-title">{user.full_name || user.username}</span>
                <span className="block text-[10px] font-semibold stu-muted">{progressPct}% {t('bajarildi')}</span>
              </span>
              <ChevronDown size={14} className={`hidden stu-muted transition-transform sm:block ${profileOpen ? 'rotate-180' : ''}`} />
            </button>

            {profileOpen && (
              <div className="absolute right-0 top-[calc(100%+.6rem)] z-[80] w-64 overflow-hidden rounded-2xl border border-border bg-surface-100 p-2 shadow-2xl" role="menu">
                <div className="mb-1 flex items-center gap-3 rounded-xl bg-surface-200/70 p-3">
                  <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${avatarGrad} text-xs font-black text-white`}>
                    {initials}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-bold stu-title">{user.full_name || user.username}</span>
                    <span className="block truncate text-xs stu-muted">@{user.username}</span>
                  </span>
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-xs">
                  <span className="flex items-center gap-1.5 font-bold text-violet-600 dark:text-violet-300"><Zap size={13} /> {xp} XP</span>
                  <span className="font-semibold stu-muted">{t('Progress')} {progressPct}%</span>
                </div>
                <Link to="/results" role="menuitem" className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold stu-body hover:bg-surface-200">
                  <UserRound size={16} /> {t('Natijalarim')}
                </Link>
                <button type="button" onClick={handleLogout} role="menuitem" className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-500/10">
                  <LogOut size={16} /> {t('Chiqish')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
