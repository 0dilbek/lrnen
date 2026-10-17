import { createContext, useContext, useEffect, useMemo, useState } from 'react';

const MediaProtectionContext = createContext({ watermark: 'English LMS' });

export function MediaProtectionProvider({ identity, children }) {
  const [captureWarning, setCaptureWarning] = useState(false);
  const watermark = identity || 'English LMS';

  useEffect(() => {
    const isProtectedTarget = (target) => target?.closest?.('[data-protected-media]');
    const blockPointerAction = (event) => {
      if (isProtectedTarget(event.target)) event.preventDefault();
    };
    const blockShortcut = (event) => {
      const key = event.key.toLowerCase();
      if ((event.ctrlKey || event.metaKey) && ['s', 'p', 'u'].includes(key)) {
        event.preventDefault();
        setCaptureWarning(true);
      }
      if (event.key === 'PrintScreen') {
        event.preventDefault();
        setCaptureWarning(true);
      }
    };
    const hideWhenBackgrounded = () => {
      document.body.classList.toggle('protected-media-hidden', document.hidden);
    };
    const hideOnWindowBlur = () => document.body.classList.add('protected-media-hidden');
    const revealOnWindowFocus = () => document.body.classList.remove('protected-media-hidden');
    document.addEventListener('contextmenu', blockPointerAction);
    document.addEventListener('dragstart', blockPointerAction);
    document.addEventListener('keydown', blockShortcut);
    document.addEventListener('visibilitychange', hideWhenBackgrounded);
    window.addEventListener('blur', hideOnWindowBlur);
    window.addEventListener('focus', revealOnWindowFocus);
    return () => {
      document.removeEventListener('contextmenu', blockPointerAction);
      document.removeEventListener('dragstart', blockPointerAction);
      document.removeEventListener('keydown', blockShortcut);
      document.removeEventListener('visibilitychange', hideWhenBackgrounded);
      window.removeEventListener('blur', hideOnWindowBlur);
      window.removeEventListener('focus', revealOnWindowFocus);
      document.body.classList.remove('protected-media-hidden');
    };
  }, []);

  useEffect(() => {
    if (!captureWarning) return undefined;
    const timer = window.setTimeout(() => setCaptureWarning(false), 2200);
    return () => window.clearTimeout(timer);
  }, [captureWarning]);

  const value = useMemo(() => ({ watermark }), [watermark]);
  return (
    <MediaProtectionContext.Provider value={value}>
      {children}
      {captureWarning && (
        <div className="fixed inset-x-4 bottom-24 z-[200] mx-auto max-w-md rounded-2xl border border-amber-400/40 bg-slate-950/95 px-5 py-4 text-center text-sm font-bold text-amber-200 shadow-2xl">
          Dars materiallarini nusxalash va ekran tasviriga olish cheklangan.
        </div>
      )}
    </MediaProtectionContext.Provider>
  );
}

export function ProtectedMedia({ children, className = '', ...props }) {
  const { watermark } = useContext(MediaProtectionContext);
  return (
    <div {...props} className={`protected-media ${className}`} data-protected-media data-watermark={watermark}>
      {children}
      <div className="protected-media-watermark" aria-hidden="true">
        {Array.from({ length: 6 }, (_, index) => <span key={index}>{watermark}</span>)}
      </div>
    </div>
  );
}
