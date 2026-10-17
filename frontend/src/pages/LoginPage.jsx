import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, BookOpen, CheckCircle2, Eye, EyeOff, Loader2, Lock,
  ShieldCheck, Sparkles, User,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

const FEATURES = [
  'Shaxsiy darslar',
  'Interaktiv mashqlar',
  'Natijalarni kuzatish',
];

function BrandMark({ light = false }) {
  return (
    <div className="flex items-center gap-3">
      <span className={`flex h-11 w-11 items-center justify-center rounded-2xl ${light ? 'bg-white/15 text-white ring-1 ring-white/25 backdrop-blur' : 'bg-gradient-to-br from-blue-600 to-violet-600 text-white shadow-lg shadow-blue-200'}`}>
        <BookOpen size={22} strokeWidth={2.4} />
      </span>
      <span>
        <span className={`block text-[10px] font-black uppercase tracking-[0.24em] ${light ? 'text-blue-100' : 'text-blue-600'}`}>English LMS</span>
        <span className={`block text-lg font-black leading-5 tracking-tight ${light ? 'text-white' : 'text-slate-900'}`}>Learn English</span>
      </span>
    </div>
  );
}

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!username.trim() || !password) {
      setError(t('Login va parolni kiriting'));
      return;
    }
    setLoading(true);
    setError('');
    try {
      const user = await login(username.trim(), password);
      navigate(user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || t("Login yoki parol noto'g'ri"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="always-light min-h-[100svh] bg-[#eef3fb] p-0 text-slate-900 sm:p-4 lg:p-6">
      <div className="mx-auto grid min-h-[100svh] w-full max-w-[1480px] overflow-hidden bg-white shadow-[0_30px_100px_-40px_rgba(15,23,42,0.45)] sm:min-h-[calc(100svh-2rem)] sm:rounded-[32px] lg:min-h-[calc(100svh-3rem)] lg:grid-cols-[1.12fr_0.88fr]">
        <section className="relative min-h-[240px] overflow-hidden sm:min-h-[300px] lg:min-h-0">
          <img
            src="/assets/login-hero-v2.png"
            alt="Noutbuk orqali ingliz tilini o‘rganayotgan o‘quvchi"
            className="absolute inset-0 h-full w-full object-cover object-[50%_52%] lg:object-center"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#071b46]/95 via-[#092862]/25 to-[#071b46]/45 lg:bg-gradient-to-tr lg:from-[#071b46]/95 lg:via-[#092862]/20 lg:to-transparent" />
          <div className="absolute inset-0 opacity-30 [background-image:radial-gradient(circle_at_20%_20%,rgba(255,255,255,.32),transparent_24%)]" />

          <div className="relative flex h-full min-h-[240px] flex-col justify-between p-5 sm:min-h-[300px] sm:p-8 lg:min-h-full lg:p-10 xl:p-14">
            <div className="flex items-start justify-between gap-3">
              <BrandMark light />
              <div className="lg:hidden"><LanguageSwitcher compact light /></div>
            </div>

            <div className="max-w-2xl pt-14 sm:pt-20 lg:pb-4 lg:pt-32">
              <div className="mb-4 hidden w-fit items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-2 text-xs font-bold text-white backdrop-blur-md sm:inline-flex">
                <Sparkles size={14} className="text-cyan-300" />
                {t('Bilim sari yangi qadam')}
              </div>
              <h1 className="max-w-xl text-2xl font-black leading-[1.08] tracking-[-0.035em] text-white sm:text-4xl lg:text-5xl xl:text-[56px]">
                {t('Ingliz tilini ishonch bilan o‘rganing')}
              </h1>
              <p className="mt-3 max-w-lg text-sm leading-6 text-blue-100 sm:text-base lg:mt-5 lg:text-lg">
                {t('Har kuni yangi qadam, har darsda yangi imkoniyat.')}
              </p>
              <div className="mt-7 hidden flex-wrap gap-3 lg:flex">
                {FEATURES.map((feature) => (
                  <span key={feature} className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 py-2 text-xs font-extrabold text-white backdrop-blur-md">
                    <CheckCircle2 size={15} className="text-cyan-300" /> {t(feature)}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="relative flex items-center justify-center bg-white px-5 py-8 sm:px-10 sm:py-12 lg:px-12 xl:px-20">
          <div className="absolute right-8 top-8 z-20 hidden lg:block"><LanguageSwitcher light /></div>
          <div className="w-full max-w-[440px]">
            <div className="mb-8 hidden lg:block"><BrandMark /></div>

            <div className="mb-7">
              <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 ring-1 ring-blue-100 lg:hidden">
                <ShieldCheck size={22} />
              </div>
              <h2 className="text-2xl font-black tracking-[-0.025em] text-slate-900 sm:text-3xl">
                {t('Hisobingizga kiring')}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                {t('Darslaringizni davom ettirish uchun ma’lumotlaringizni kiriting.')}
              </p>
            </div>

            {error && (
              <div role="alert" className="mb-5 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm font-semibold text-red-700">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-[11px]">!</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="login-username" className="mb-2 block text-sm font-extrabold text-slate-700">Login</label>
                <div className="group relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 transition group-focus-within:text-blue-600" size={19} />
                  <input
                    id="login-username"
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder={t('Loginingizni kiriting')}
                    autoComplete="username"
                    className="h-14 w-full rounded-2xl border border-slate-200 bg-slate-50/80 pl-12 pr-4 text-[15px] font-semibold text-slate-900 outline-none transition placeholder:font-medium placeholder:text-slate-400 hover:border-slate-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="login-password" className="mb-2 block text-sm font-extrabold text-slate-700">{t('Parol')}</label>
                <div className="group relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 transition group-focus-within:text-blue-600" size={19} />
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder={t('Parolingizni kiriting')}
                    autoComplete="current-password"
                    className="h-14 w-full rounded-2xl border border-slate-200 bg-slate-50/80 pl-12 pr-12 text-[15px] font-semibold text-slate-900 outline-none transition placeholder:font-medium placeholder:text-slate-400 hover:border-slate-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={t(showPassword ? 'Parolni yashirish' : 'Parolni ko‘rsatish')}
                    className="absolute right-3 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-xl text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  >
                    {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group flex h-14 w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 px-5 text-[15px] font-black text-white shadow-lg shadow-blue-500/20 transition hover:-translate-y-0.5 hover:shadow-xl hover:shadow-blue-500/25 active:translate-y-0 disabled:pointer-events-none disabled:opacity-65"
              >
                {loading ? (
                  <><Loader2 className="animate-spin" size={19} /> {t('Kirish...')}</>
                ) : (
                  <>{t('Kirish')} <ArrowRight size={19} className="transition-transform group-hover:translate-x-1" /></>
                )}
              </button>
            </form>

            <div className="mt-7 flex items-center justify-center gap-2 text-center text-xs font-semibold text-slate-400">
              <ShieldCheck size={15} className="text-emerald-500" />
              {t("Login va parol o'qituvchi tomonidan beriladi")}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
