import { useEffect, useRef, useState } from 'react';
import { Check, ChevronDown, Loader2 } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const LANGUAGES = [
  { value: 'kaa', short: 'QQ', label: 'Qaraqalpaqsha' },
  { value: 'uz', short: 'UZ', label: 'O‘zbekcha' },
];

function Flag({ language, className = '' }) {
  if (language === 'kaa') {
    return (
      <svg viewBox="0 0 30 20" aria-hidden="true" className={`shrink-0 overflow-hidden rounded-[5px] ${className}`}>
        <rect width="30" height="20" fill="#1595d3" />
        <rect y="7" width="30" height="1" fill="#e52332" />
        <rect y="8" width="30" height="1" fill="#fff" />
        <rect y="9" width="30" height="2" fill="#f5d21f" />
        <rect y="11" width="30" height="1" fill="#fff" />
        <rect y="12" width="30" height="1" fill="#e52332" />
        <rect y="13" width="30" height="7" fill="#20a64a" />
        <circle cx="7" cy="3.8" r="2.3" fill="#fff" />
        <circle cx="8.1" cy="3.5" r="2.2" fill="#1595d3" />
        {[11.2, 13.6, 16, 18.4, 20.8].map((x) => <circle key={x} cx={x} cy="3.8" r="0.55" fill="#fff" />)}
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 30 20" aria-hidden="true" className={`shrink-0 overflow-hidden rounded-[5px] ${className}`}>
      <rect width="30" height="20" fill="#1595d3" />
      <rect y="6" width="30" height="1" fill="#e52332" />
      <rect y="7" width="30" height="6" fill="#fff" />
      <rect y="13" width="30" height="1" fill="#e52332" />
      <rect y="14" width="30" height="6" fill="#20a64a" />
      <circle cx="5.4" cy="3.2" r="2.1" fill="#fff" />
      <circle cx="6.25" cy="2.85" r="1.9" fill="#1595d3" />
      {[9.4, 11.7, 14, 10.55, 12.85].map((x, index) => (
        <circle key={`${x}-${index}`} cx={x} cy={index < 3 ? 2.25 : 4.25} r="0.48" fill="#fff" />
      ))}
    </svg>
  );
}

export default function LanguageSwitcher({ compact = false, light = false }) {
  const { language, changeLanguage } = useLanguage();
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const rootRef = useRef(null);
  const current = LANGUAGES.find((item) => item.value === language) || LANGUAGES[0];

  useEffect(() => {
    const closeOnOutsideClick = (event) => {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    };
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('pointerdown', closeOnOutsideClick);
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsideClick);
      document.removeEventListener('keydown', closeOnEscape);
    };
  }, []);

  const selectLanguage = async (nextLanguage) => {
    if (nextLanguage === language) {
      setOpen(false);
      return;
    }
    setSaving(true);
    try {
      await changeLanguage(nextLanguage);
      setOpen(false);
    } catch {
      // LanguageContext restores the previous value when saving fails.
    } finally {
      setSaving(false);
    }
  };

  const surface = light
    ? 'border-slate-200/90 bg-white/90 text-slate-700 shadow-sm hover:border-blue-300 hover:bg-white'
    : 'border-border bg-surface-200/90 stu-body shadow-sm hover:border-blue-500/40';

  return (
    <div ref={rootRef} className="relative inline-flex">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label="Interfeys tilini tanlash"
        aria-haspopup="listbox"
        aria-expanded={open}
        className={`group inline-flex h-10 items-center rounded-2xl border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 ${compact ? 'gap-1.5 px-2' : 'min-w-[168px] gap-2.5 px-3'} ${surface}`}
      >
        <span className="rounded-lg bg-white p-0.5 shadow-sm ring-1 ring-black/5">
          <Flag language={current.value} className="h-[18px] w-[27px]" />
        </span>
        {!compact && (
          <span className="min-w-0 flex-1 text-left">
            <span className="block text-[9px] font-black uppercase tracking-[0.14em] opacity-50">{current.short}</span>
            <span className="block truncate text-xs font-extrabold leading-3.5">{current.label}</span>
          </span>
        )}
        {saving
          ? <Loader2 size={14} className="animate-spin opacity-60" />
          : <ChevronDown size={14} className={`opacity-50 transition-transform duration-200 group-hover:opacity-80 ${open ? 'rotate-180' : ''}`} />}
      </button>

      {open && (
        <div
          role="listbox"
          aria-label="Interfeys tili"
          className="absolute right-0 top-[calc(100%+8px)] z-[100] w-52 overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-1.5 text-slate-800 shadow-[0_18px_50px_-12px_rgba(15,23,42,0.35)] dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        >
          <div className="px-2.5 pb-1.5 pt-1 text-[10px] font-black uppercase tracking-[0.16em] text-slate-400">
            Tilni tanlang
          </div>
          {LANGUAGES.map((item) => {
            const selected = item.value === language;
            return (
              <button
                key={item.value}
                type="button"
                role="option"
                aria-selected={selected}
                disabled={saving}
                onClick={() => selectLanguage(item.value)}
                className={`flex w-full items-center gap-3 rounded-xl px-2.5 py-2.5 text-left transition ${selected ? 'bg-blue-50 text-blue-700 dark:bg-blue-500/15 dark:text-blue-300' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}`}
              >
                <span className="rounded-lg bg-white p-0.5 shadow-sm ring-1 ring-black/5">
                  <Flag language={item.value} className="h-5 w-[30px]" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-extrabold">{item.label}</span>
                  <span className="block text-[10px] font-bold uppercase tracking-wider opacity-45">{item.short}</span>
                </span>
                {selected && <Check size={17} strokeWidth={3} />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
