import { useState } from 'react';
import { ChevronLeft, ChevronRight, Maximize2, X, ZoomIn, ZoomOut } from 'lucide-react';

function normalizePages(pages = []) {
  return pages
    .map((page, index) => typeof page === 'string'
      ? { url: page, page_number: index + 1, caption: '' }
      : page)
    .filter((page) => page?.url);
}

export default function BookPageViewer({ pages, title = "O'qish sahifalari" }) {
  const normalized = normalizePages(pages);
  const [active, setActive] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);

  if (!normalized.length) return null;
  const activeIndex = Math.min(active, normalized.length - 1);
  const page = normalized[activeIndex];
  const move = (direction) => {
    setActive((value) => (value + direction + normalized.length) % normalized.length);
    setZoom(1);
  };

  return (
    <div className="rounded-2xl border border-border bg-surface-200/50 overflow-hidden">
      <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-border">
        <div className="min-w-0">
          <p className="text-sm font-bold stu-title">{title}</p>
          <p className="text-xs stu-muted">
            {normalized.length > 1 ? `${activeIndex + 1} / ${normalized.length} sahifa` : '1 sahifa'}
            {page.page_number ? ` · Kitobdagi ${page.page_number}-sahifa` : ''}
          </p>
        </div>
        <button type="button" onClick={() => setFullscreen(true)} className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-surface-100 border border-border stu-body text-xs font-semibold hover:border-indigo-400 transition">
          <Maximize2 size={14} /> Kattalashtirish
        </button>
      </div>

      <div className="relative bg-slate-950/5 dark:bg-black/20 p-3 sm:p-5 flex justify-center">
        {normalized.length > 1 && <button type="button" onClick={() => move(-1)} aria-label="Oldingi sahifa" className="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-black/65 text-white flex items-center justify-center hover:bg-indigo-600 transition"><ChevronLeft size={20} /></button>}
        <button type="button" onClick={() => setFullscreen(true)} className="cursor-zoom-in">
          <img src={page.url} alt={page.caption || `${page.page_number || activeIndex + 1}-sahifa`} className="max-h-[70vh] w-auto max-w-full rounded-xl shadow-xl object-contain" />
        </button>
        {normalized.length > 1 && <button type="button" onClick={() => move(1)} aria-label="Keyingi sahifa" className="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-black/65 text-white flex items-center justify-center hover:bg-indigo-600 transition"><ChevronRight size={20} /></button>}
      </div>

      {normalized.length > 1 && (
        <div className="flex gap-2 p-3 border-t border-border overflow-x-auto">
          {normalized.map((item, index) => (
            <button key={`${item.url}-${index}`} type="button" onClick={() => setActive(index)} className={`shrink-0 rounded-lg overflow-hidden border-2 transition ${activeIndex === index ? 'border-indigo-500 ring-2 ring-indigo-500/20' : 'border-border opacity-65 hover:opacity-100'}`}>
              <img src={item.url} alt="" className="w-14 h-20 object-cover" />
            </button>
          ))}
        </div>
      )}

      {fullscreen && (
        <div className="fixed inset-0 z-[100] bg-black/95 flex flex-col" role="dialog" aria-modal="true">
          <div className="flex items-center justify-between px-4 py-3 text-white bg-black/50">
            <span className="text-sm font-semibold">{page.caption || `Sahifa ${page.page_number || activeIndex + 1}`}</span>
            <div className="flex items-center gap-2">
              <button type="button" onClick={() => setZoom((value) => Math.max(.5, value - .25))} className="p-2 rounded-lg hover:bg-white/10"><ZoomOut size={20} /></button>
              <span className="w-14 text-center text-xs font-bold">{Math.round(zoom * 100)}%</span>
              <button type="button" onClick={() => setZoom((value) => Math.min(4, value + .25))} className="p-2 rounded-lg hover:bg-white/10"><ZoomIn size={20} /></button>
              <button type="button" onClick={() => { setFullscreen(false); setZoom(1); }} className="p-2 rounded-lg hover:bg-red-500"><X size={22} /></button>
            </div>
          </div>
          <div className="flex-1 overflow-auto p-6 flex items-start justify-center">
            <img src={page.url} alt={page.caption || ''} style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }} className="max-w-full h-auto transition-transform" />
          </div>
        </div>
      )}
    </div>
  );
}
