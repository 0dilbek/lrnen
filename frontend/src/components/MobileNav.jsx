import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, BookMarked, BarChart2, Trophy } from 'lucide-react';

export default function MobileNav() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user || user.role === 'admin') return null;

  const studentLinks = [
    { to: '/dashboard',   icon: <LayoutDashboard size={22} />, label: 'Bosh'     },
    { to: '/my-lessons',  icon: <BookMarked size={22} />,      label: 'Darslar'  },
    { to: '/results',     icon: <BarChart2 size={22} />,       label: 'Natijalar'},
    { to: '/leaderboard', icon: <Trophy size={22} />,          label: 'Reyting'  },
  ];

  const links = studentLinks;

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 sm:hidden bg-surface-50/95 backdrop-blur-md border-t border-border">
      <div className="flex items-stretch">
        {links.map(({ to, icon, label }) => {
          const isActive = location.pathname === to || (to !== '/dashboard' && to !== '/admin' && location.pathname.startsWith(to));
          return (
            <Link
              key={to}
              to={to}
              className={`flex-1 flex flex-col items-center justify-center py-3 gap-0.5 transition-all ${
                isActive ? 'text-indigo-400' : 'text-slate-500'
              }`}
            >
              {isActive ? (
                <div className="bg-indigo-500/15 rounded-xl p-1.5">{icon}</div>
              ) : (
                <div className="p-1.5">{icon}</div>
              )}
              <span className={`text-[10px] font-semibold ${isActive ? 'text-indigo-400' : 'text-slate-500'}`}>
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
