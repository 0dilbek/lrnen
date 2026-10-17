import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, BookMarked, BarChart2, Trophy } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

const LINKS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Bosh', exact: true },
  { to: '/my-lessons', icon: BookMarked, label: 'Darslar', lessonRoute: true },
  { to: '/results', icon: BarChart2, label: 'Natijalar' },
  { to: '/leaderboard', icon: Trophy, label: 'Reyting' },
];

export default function MobileNav() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();

  if (!user || user.role === 'admin') return null;

  return (
    <nav className="student-mobile-nav fixed inset-x-0 bottom-0 z-50 md:hidden" aria-label="Mobil navigatsiya">
      <div className="mx-auto grid max-w-lg grid-cols-4 px-1 pb-[max(.35rem,env(safe-area-inset-bottom))] pt-1">
        {LINKS.map(({ to, icon: Icon, label, exact, lessonRoute }) => {
          const active = exact
            ? location.pathname === to
            : location.pathname.startsWith(to)
              || (lessonRoute && location.pathname.startsWith('/lessons/'));
          return (
            <Link
              key={to}
              to={to}
              aria-current={active ? 'page' : undefined}
              className={`relative flex min-w-0 flex-col items-center justify-center gap-0.5 rounded-xl px-1 py-1.5 transition ${active ? 'text-indigo-600 dark:text-indigo-300' : 'stu-muted'}`}
            >
              {active && <span className="absolute -top-1 h-1 w-7 rounded-b-full bg-indigo-500" />}
              <span className={`grid h-8 w-10 place-items-center rounded-xl transition ${active ? 'bg-indigo-500/15' : ''}`}>
                <Icon size={20} strokeWidth={active ? 2.5 : 2} />
              </span>
              <span className="max-w-full truncate text-[10px] font-bold">{t(label)}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
