import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, BookMarked, BarChart2, Trophy, Users, BookOpen, LayoutGrid } from 'lucide-react';

export default function MobileNav() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const studentLinks = [
    { to: '/dashboard',   icon: <LayoutDashboard size={22} />, label: 'Bosh'     },
    { to: '/my-lessons',  icon: <BookMarked size={22} />,      label: 'Darslar'  },
    { to: '/results',     icon: <BarChart2 size={22} />,       label: 'Natijalar'},
    { to: '/leaderboard', icon: <Trophy size={22} />,          label: 'Reyting'  },
  ];

  const adminLinks = [
    { to: '/admin',          icon: <LayoutGrid size={22} />,  label: 'Dashboard' },
    { to: '/admin/students', icon: <Users size={22} />,       label: 'O\'quvchilar' },
    { to: '/admin/lessons',  icon: <BookOpen size={22} />,    label: 'Darslar'   },
  ];

  const links = user.role === 'admin' ? adminLinks : studentLinks;

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 sm:hidden bg-white border-t border-gray-100 shadow-2xl shadow-black/10">
      <div className="flex items-stretch">
        {links.map(({ to, icon, label }) => {
          const isActive = location.pathname === to || (to !== '/dashboard' && to !== '/admin' && location.pathname.startsWith(to));
          return (
            <Link
              key={to}
              to={to}
              className={`flex-1 flex flex-col items-center justify-center py-3 gap-0.5 transition-all ${
                isActive
                  ? 'text-blue-600'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              {isActive ? (
                <div className="bg-blue-50 rounded-xl p-1.5">{icon}</div>
              ) : (
                <div className="p-1.5">{icon}</div>
              )}
              <span className={`text-[10px] font-semibold ${isActive ? 'text-blue-600' : 'text-gray-400'}`}>
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
