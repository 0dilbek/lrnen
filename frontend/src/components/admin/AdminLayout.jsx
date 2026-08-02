import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import {
  BookOpen, LayoutDashboard, Users, BookMarked,
  LogOut, ChevronRight, Shield, Sun, Moon,
} from 'lucide-react';

const NAV = [
  { to: '/admin', icon: LayoutDashboard, label: 'Dashboard', exact: true },
  { to: '/admin/students', icon: Users, label: "O'quvchilar" },
  { to: '/admin/lessons', icon: BookMarked, label: 'Kontent' },
];

export default function AdminLayout({ children, title, subtitle }) {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (item) =>
    item.exact ? location.pathname === item.to : location.pathname.startsWith(item.to);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const theme = dark ? 'dark' : 'light';

  return (
    <div className="admin-shell min-h-screen flex" data-admin-theme={theme}>
      <aside className="admin-sidebar w-60 shrink-0 border-r flex flex-col">
        <div className="px-5 py-5 border-b border-inherit">
          <Link to="/admin" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <BookOpen className="text-white" size={18} />
            </div>
            <div>
              <p className="admin-text-title font-bold text-sm leading-tight">Learn English</p>
              <p className="admin-text-muted text-[10px] uppercase tracking-widest">Admin</p>
            </div>
          </Link>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((item) => {
            const active = isActive(item);
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`admin-nav-item flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all border ${
                  active
                    ? 'admin-nav-active'
                    : 'admin-text-muted border-transparent'
                }`}
              >
                <Icon size={18} />
                {item.label}
                {active && <ChevronRight size={14} className="ml-auto opacity-50" />}
              </Link>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t border-inherit space-y-1">
          <button
            onClick={toggle}
            className="admin-nav-item w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm admin-text-muted border border-transparent transition"
          >
            {dark ? <Sun size={16} /> : <Moon size={16} />}
            {dark ? 'Kunduzgi rejim' : 'Tungi rejim'}
          </button>
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
              <Shield size={14} className="text-indigo-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium admin-text-title truncate">
                {user?.full_name || user?.username}
              </p>
              <p className="text-xs admin-text-muted">Administrator</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm admin-text-muted hover:text-red-500 hover:bg-red-500/10 transition"
          >
            <LogOut size={16} />
            Chiqish
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        {(title || subtitle) && (
          <header className="admin-header shrink-0 px-8 py-6 border-b flex items-center justify-between">
            <div>
              {title && <h1 className="text-xl font-bold admin-text-title">{title}</h1>}
              {subtitle && <p className="text-sm admin-text-muted mt-0.5">{subtitle}</p>}
            </div>
          </header>
        )}
        <main className="admin-main flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}