import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import { Users, BookOpen, CheckCircle, BarChart2, Loader2, ArrowRight } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/courses/stats/').then(({ data }) => setStats(data)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="animate-spin text-indigo-400" size={36} />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Users size={22} />}
          value={stats?.total_students || 0}
          label="O'quvchilar"
          color="indigo"
          to="/admin/students"
        />
        <StatCard
          icon={<BookOpen size={22} />}
          value={stats?.total_lessons || 0}
          label="Darslar"
          color="violet"
          to="/admin/lessons"
        />
        <StatCard
          icon={<BarChart2 size={22} />}
          value={stats?.total_categories || 0}
          label="Kategoriyalar"
          color="cyan"
          to="/admin/lessons"
        />
        <StatCard
          icon={<CheckCircle size={22} />}
          value={stats?.completed || 0}
          label="Yakunlangan"
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <QuickLink
          to="/admin/students"
          icon={<Users size={22} />}
          title="O'quvchilar boshqaruvi"
          desc="Yangi o'quvchi qo'shish, parol yangilash, levellar"
        />
        <QuickLink
          to="/admin/lessons"
          icon={<BookOpen size={22} />}
          title="Kontent boshqaruvi"
          desc="48 ta unit — darslar, mashqlar, lug'at, testlar"
        />
      </div>
    </div>
  );
}

function StatCard({ icon, value, label, color, to }) {
  const gradients = {
    indigo: 'from-indigo-500/20 to-indigo-600/5 border-indigo-500/20 text-indigo-400',
    violet: 'from-violet-500/20 to-violet-600/5 border-violet-500/20 text-violet-400',
    cyan: 'from-cyan-500/20 to-cyan-600/5 border-cyan-500/20 text-cyan-400',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
  };

  const inner = (
    <div className={`stat-card bg-gradient-to-br ${gradients[color]} border`}>
      <div className={`inline-flex p-2.5 rounded-xl bg-surface-200 mb-4 ${gradients[color].split(' ').pop()}`}>
        {icon}
      </div>
      <p className="text-3xl font-bold admin-text-title">{value}</p>
      <p className="text-sm admin-text-muted mt-1">{label}</p>
    </div>
  );

  return to ? <Link to={to} className="block">{inner}</Link> : inner;
}

function QuickLink({ to, icon, title, desc }) {
  return (
    <Link
      to={to}
      className="admin-card p-6 flex items-center gap-4 group hover:border-indigo-500/30 transition-all"
    >
      <div className="p-3 rounded-xl bg-indigo-500/15 text-indigo-400 group-hover:bg-indigo-500/25 transition">
        {icon}
      </div>
      <div className="flex-1">
        <p className="font-semibold admin-text-title">{title}</p>
        <p className="text-sm admin-text-muted mt-0.5">{desc}</p>
      </div>
      <ArrowRight size={18} className="text-slate-600 group-hover:text-indigo-400 transition" />
    </Link>
  );
}