import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, BookMarked, BarChart2, Trophy } from 'lucide-react';

export default function MobileNav() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user || user.role === 'admin') return null;

  const links = [
    { to: '/dashboard',   icon: LayoutDashboard, label: 'Bosh'      },
    { to: '/my-lessons',  icon: BookMarked,      label: 'Darslar'   },
    { to: '/results',     icon: BarChart2,        label: 'Natijalar' },
    { to: '/leaderboard', icon: Trophy,           label: 'Reyting'   },
  ];

  return (
    <nav className="student-mobile-nav fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div className="flex items-stretch">
        {links.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to
            || (to !== '/dashboard' && location.pathname.startsWith(to));
          return (
            <Link
              key={to}
              to={to}
              className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-all ${
                isActive ? 'text-indigo-600' : 'stu-muted'
              }`}
            >
              <div className={`rounded-xl p-1.5 transition ${isActive ? 'bg-indigo-500/15' : ''}`}>
                <Icon size={20} />
              </div>
              <span className={`text-[10px] font-semibold ${isActive ? 'text-indigo-600' : 'stu-muted'}`}>
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}