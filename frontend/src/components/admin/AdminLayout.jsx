import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  BookOpen, LayoutDashboard, Users, BookMarked, LogOut,
  Bell, ChevronRight, Shield, Sun, Moon, Menu, X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import api from '../../api';
import LanguageSwitcher from '../LanguageSwitcher';
import { useLanguage } from '../../context/LanguageContext';

const NAV = [
  { to: '/admin', icon: LayoutDashboard, label: 'Dashboard', exact: true },
  { to: '/admin/students', icon: Users, label: "O‘quvchilar" },
  { to: '/admin/notifications', icon: Bell, label: 'Notificationlar', notification: true },
  { to: '/admin/lessons', icon: BookMarked, label: 'Kontent' },
];

export default function AdminLayout({ children, title, subtitle }) {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);

  useEffect(() => setSidebarOpen(false), [location.pathname]);

  useEffect(() => {
    let active = true;
    const loadCount = () => {
      api.get('/quiz/notifications/?status=unread').then(({ data }) => {
        if (active) setNotificationCount(data.unread_count || 0);
      }).catch(() => {});
    };
    const handleUpdate = (event) => setNotificationCount(Number(event.detail) || 0);
    loadCount();
    const timer = window.setInterval(loadCount, 20000);
    window.addEventListener('admin-notifications-updated', handleUpdate);
    return () => {
      active = false;
      window.clearInterval(timer);
      window.removeEventListener('admin-notifications-updated', handleUpdate);
    };
  }, []);

  const isActive = (item) => (
    item.exact ? location.pathname === item.to : location.pathname.startsWith(item.to)
  );

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="admin-shell flex min-h-screen" data-admin-theme={dark ? 'dark' : 'light'}>
      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-[60] bg-slate-950/55 backdrop-blur-sm md:hidden"
          aria-label="Menyuni yopish"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`admin-sidebar fixed inset-y-0 left-0 z-[70] flex w-72 shrink-0 flex-col border-r shadow-2xl transition-transform duration-200 md:sticky md:top-0 md:z-auto md:h-screen md:w-60 md:translate-x-0 md:shadow-none ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between border-b border-inherit px-5 py-5">
          <Link to="/admin" className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/20">
              <BookOpen className="text-white" size={19} />
            </span>
            <span>
              <span className="block text-sm font-black leading-tight admin-text-title">Learn English</span>
              <span className="block text-[10px] font-bold uppercase tracking-[.18em] admin-text-muted">Admin panel</span>
            </span>
          </Link>
          <button type="button" onClick={() => setSidebarOpen(false)} className="grid h-9 w-9 place-items-center rounded-xl admin-text-muted hover:bg-surface-200 md:hidden" aria-label="Menyuni yopish">
            <X size={19} />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Admin navigatsiya">
          {NAV.map((item) => {
            const active = isActive(item);
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                aria-current={active ? 'page' : undefined}
                className={`admin-nav-item flex items-center gap-3 rounded-xl border px-3 py-3 text-sm font-bold transition-all ${active ? 'admin-nav-active' : 'admin-text-muted border-transparent'}`}
              >
                <span className={`grid h-8 w-8 place-items-center rounded-lg ${active ? 'bg-indigo-500/15' : 'bg-surface-200/60'}`}>
                  <Icon size={17} />
                </span>
                {t(item.label)}
                {item.notification && notificationCount > 0 && (
                  <span className="ml-auto min-w-5 rounded-full bg-red-500 px-1.5 py-0.5 text-center text-[10px] font-black text-white">
                    {notificationCount > 99 ? '99+' : notificationCount}
                  </span>
                )}
                {active && (!item.notification || notificationCount === 0) && <ChevronRight size={14} className="ml-auto opacity-60" />}
              </Link>
            );
          })}
        </nav>

        <div className="space-y-1 border-t border-inherit px-4 py-4">
          <LanguageSwitcher />
          <button type="button" onClick={toggle} className="admin-nav-item flex w-full items-center gap-2 rounded-xl border border-transparent px-3 py-2.5 text-sm font-semibold admin-text-muted transition">
            {dark ? <Sun size={17} /> : <Moon size={17} />}
            {dark ? t('Kunduzgi rejim') : t('Tungi rejim')}
          </button>
          <div className="my-1 flex items-center gap-3 rounded-xl bg-surface-200/50 px-3 py-3">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-indigo-500/30 bg-indigo-500/15">
              <Shield size={15} className="text-indigo-500" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-bold admin-text-title">{user?.full_name || user?.username}</span>
              <span className="block text-xs admin-text-muted">{t('Administrator')}</span>
            </span>
          </div>
          <button type="button" onClick={handleLogout} className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold admin-text-muted transition hover:bg-red-500/10 hover:text-red-500">
            <LogOut size={17} /> {t('Chiqish')}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className={`admin-header sticky top-0 z-40 shrink-0 border-b px-4 py-3 backdrop-blur-xl md:px-8 md:py-5 ${(title || subtitle) ? '' : 'md:hidden'}`}>
          <div className="flex items-center gap-3">
            <button type="button" onClick={() => setSidebarOpen(true)} className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-border admin-text-title hover:bg-surface-200 md:hidden" aria-label="Menyuni ochish">
              <Menu size={20} />
            </button>
            <div className="min-w-0">
              <h1 className="truncate text-lg font-black admin-text-title md:text-xl">{t(title || 'Boshqaruv')}</h1>
              {subtitle && <p className="mt-0.5 hidden truncate text-sm admin-text-muted sm:block">{t(subtitle)}</p>}
            </div>
            <Link to="/admin/notifications" className="relative ml-auto grid h-10 w-10 shrink-0 place-items-center rounded-xl admin-text-muted hover:bg-surface-200 md:hidden" aria-label="Notificationlar">
              <Bell size={18} />
              {notificationCount > 0 && (
                <span className="absolute right-0.5 top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-red-500 px-1 text-[8px] font-black text-white">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </Link>
            <div className="ml-auto md:hidden"><LanguageSwitcher compact /></div>
            <button type="button" onClick={toggle} className="grid h-10 w-10 shrink-0 place-items-center rounded-xl admin-text-muted hover:bg-surface-200 md:hidden" aria-label={dark ? 'Kunduzgi rejim' : 'Tungi rejim'}>
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </header>
        <main className="admin-main min-w-0 flex-1 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
