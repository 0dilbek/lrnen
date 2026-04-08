import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import { Users, BookOpen, CheckCircle, BarChart2, Loader2 } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/courses/stats/').then(({ data }) => setStats(data)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
      <p className="text-gray-500 mb-8">Platformaning umumiy ko'rinishi</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <AdminStat icon={<Users size={24} />} value={stats?.total_students || 0} label="O'quvchilar" color="blue" to="/admin/students" />
        <AdminStat icon={<BookOpen size={24} />} value={stats?.total_lessons || 0} label="Darslar" color="indigo" to="/admin/lessons" />
        <AdminStat icon={<BarChart2 size={24} />} value={stats?.total_categories || 0} label="Kategoriyalar" color="purple" to="/admin/lessons" />
        <AdminStat icon={<CheckCircle size={24} />} value={stats?.completed || 0} label="Yakunlangan" color="green" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <QuickAction to="/admin/students" icon={<Users size={20} />} title="O'quvchilar" desc="Ro'yxatdan o'tganlar va faollik" />
        <QuickAction to="/admin/lessons" icon={<BookOpen size={20} />} title="Kontent boshqaruvi" desc="Darslar, testlar, kategoriyalar" />
      </div>
    </div>
  );
}

function AdminStat({ icon, value, label, color, to }) {
  const colors = {
    blue: 'bg-blue-600',
    indigo: 'bg-indigo-600',
    purple: 'bg-purple-600',
    green: 'bg-green-600',
  };
  const content = (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
      <div className={`inline-flex p-2 rounded-xl ${colors[color]} mb-3`}>
        <span className="text-white">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
  return to ? <Link to={to}>{content}</Link> : content;
}

function QuickAction({ to, icon, title, desc }) {
  return (
    <Link to={to} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex items-start gap-4 hover:shadow-md transition group">
      <div className="bg-blue-50 p-3 rounded-xl group-hover:bg-blue-100 transition">
        <span className="text-blue-600">{icon}</span>
      </div>
      <div>
        <p className="font-semibold text-gray-900">{title}</p>
        <p className="text-sm text-gray-500 mt-0.5">{desc}</p>
      </div>
    </Link>
  );
}
