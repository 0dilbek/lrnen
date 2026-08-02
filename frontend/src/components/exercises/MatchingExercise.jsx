import { useState } from 'react';
import { CheckCircle2, XCircle, RotateCcw, Check, Sparkles } from 'lucide-react';
import ExampleBadge from './ExampleBadge';

function normalizeMatching(content) {
  if (content?.left && content?.right) return content;
  if (Array.isArray(content?.pairs) && content.pairs[0]?.left !== undefined) {
    const leftArr = content.pairs.map((p) => p.left);
    const rightArr = content.pairs.map((p) => p.right);
    const pairIndices = content.pairs.map((_, i) => i);
    return { left: leftArr, right: rightArr, pairs: pairIndices };
  }
  return { left: [], right: [], pairs: [] };
}

const PAIR_COLORS = [
  'border-blue-400 bg-blue-50 text-blue-700',
  'border-purple-400 bg-purple-50 text-purple-700',
  'border-amber-400 bg-amber-50 text-amber-700',
  'border-emerald-400 bg-emerald-50 text-emerald-700',
  'border-rose-400 bg-rose-50 text-rose-700',
  'border-indigo-400 bg-indigo-50 text-indigo-700',
  'border-orange-400 bg-orange-50 text-orange-700',
  'border-cyan-400 bg-cyan-50 text-cyan-700',
];

export default function MatchingExercise({ exercise, onComplete }) {
  const { left, right, pairs } = normalizeMatching(exercise.content);
  const hasExample = left.length >= 2 && pairs.length >= 1;

  const exampleMatches = hasExample ? { 0: pairs[0] } : {};

  const shuffledRight = (() => {
    const indexed = right.map((text, i) => ({ text, origIdx: i }));
    // Stable shuffle: re-renders do not move answers while the student is matching.
    return indexed.sort((a, b) => {
      const score = (item) => [...String(item.text)].reduce((sum, char) => sum + char.charCodeAt(0), item.origIdx * 97) % 101;
      return score(a) - score(b);
    });
  })();

  const [selected, setSelected] = useState(null);
  const [matches, setMatches] = useState(() => ({ ...exampleMatches }));
  const [checked, setChecked] = useState(false);

  const handleClick = (side, idx) => {
    if (checked) return;
    if (hasExample && side === 'left' && idx === 0) return;
    if (hasExample && side === 'right') {
      const orig = shuffledRight[idx].origIdx;
      if (orig === pairs[0] || matches[0] === orig) return;
    }

    if (!selected) {
      setSelected({ side, idx });
      return;
    }

    if (selected.side === side) {
      setSelected({ side, idx });
      return;
    }

    const leftIdx = side === 'left' ? idx : selected.idx;
    const rightShuffledIdx = side === 'right' ? idx : selected.idx;
    const rightOrigIdx = shuffledRight[rightShuffledIdx].origIdx;

    if (hasExample && leftIdx === 0) {
      setSelected(null);
      return;
    }

    const newMatches = { ...matches };
    if (hasExample) newMatches[0] = pairs[0];
    delete newMatches[leftIdx];
    Object.keys(newMatches).forEach((k) => {
      if (Number(k) !== 0 && newMatches[k] === rightOrigIdx) delete newMatches[k];
    });
    newMatches[leftIdx] = rightOrigIdx;
    if (hasExample) newMatches[0] = pairs[0];

    setMatches(newMatches);
    setSelected(null);
  };

  const scorableIdxs = hasExample
    ? left.map((_, i) => i).filter((i) => i > 0)
    : left.map((_, i) => i);

  const allMatched = scorableIdxs.length > 0 && scorableIdxs.every((i) => matches[i] !== undefined);

  const handleCheck = () => {
    setChecked(true);
    const correct = scorableIdxs.filter((i) => matches[i] === pairs[i]).length;
    if (onComplete) onComplete(correct, scorableIdxs.length);
  };

  const handleRetry = () => {
    setMatches({ ...exampleMatches });
    setSelected(null);
    setChecked(false);
  };

  const score = checked
    ? scorableIdxs.filter((i) => matches[i] === pairs[i]).length
    : null;

  return (
    <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {hasExample && (
        <p className="text-xs stu-muted mb-4 italic">
          1-juftlik namuna — shunday moslashtiriladi. Siz 2-savoldan boshlang.
        </p>
      )}

      <div className="grid grid-cols-2 gap-8 mb-8 relative">
        <div className="space-y-3">
          <div className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2 ml-1">Savollar</div>
          {left.map((text, i) => {
            const isExample = hasExample && i === 0;
            const isActive = selected?.side === 'left' && selected.idx === i;
            const rightOrigIdx = matches[i];
            const isMatched = rightOrigIdx !== undefined;

            let statusClass = 'bg-surface-100 border-border stu-body hover:border-indigo-400 hover:shadow-md';
            if (checked || isExample) {
              statusClass = rightOrigIdx === pairs[i]
                ? 'bg-emerald-50 border-emerald-500 text-emerald-700'
                : 'bg-rose-50 border-rose-500 text-rose-700';
            } else if (isActive) {
              statusClass = 'bg-indigo-600 border-indigo-600 text-white shadow-lg ring-2 ring-indigo-100 scale-105 z-10';
            } else if (isMatched) {
              statusClass = PAIR_COLORS[i % PAIR_COLORS.length] + ' shadow-sm opacity-90';
            }
            if (isExample) statusClass += ' cursor-default opacity-95';

            return (
              <button
                key={i}
                onClick={() => handleClick('left', i)}
                disabled={isExample}
                className={`w-full text-left p-4 rounded-2xl border-2 text-sm font-semibold transition-all duration-300 relative group transform active:scale-95 ${statusClass}`}
              >
                <div className="flex items-center gap-3">
                  <span className={`flex items-center justify-center w-5 h-5 rounded-full text-[9px] font-bold ${isActive ? 'bg-indigo-400/30' : 'bg-surface-200 text-slate-400'}`}>
                    {i + 1}
                  </span>
                  {isExample && <ExampleBadge />}
                  <span className="flex-1">{text}</span>
                  {isMatched && !checked && !isExample && (
                    <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
                  )}
                  {(checked || isExample) && (
                    rightOrigIdx === pairs[i]
                      ? <CheckCircle2 size={16} className="text-emerald-500" />
                      : <XCircle size={16} className="text-rose-500" />
                  )}
                </div>
              </button>
            );
          })}
        </div>

        <div className="space-y-3">
          <div className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2 ml-1 text-right">Javoblar</div>
          {shuffledRight.map((item, shIdx) => {
            const isExampleRight = hasExample && item.origIdx === pairs[0];
            const isActive = selected?.side === 'right' && selected.idx === shIdx;
            const leftIdxMatch = Object.keys(matches).find((k) => matches[k] === item.origIdx);
            const isMatched = leftIdxMatch !== undefined;

            let statusClass = 'bg-surface-100 border-border stu-body hover:border-indigo-400 hover:shadow-md';
            if (checked || isExampleRight) {
              const isCorrect = leftIdxMatch !== undefined && matches[leftIdxMatch] === pairs[Number(leftIdxMatch)];
              statusClass = isCorrect
                ? 'bg-emerald-50 border-emerald-500 text-emerald-700'
                : 'bg-rose-50 border-rose-500 text-rose-700';
            } else if (isActive) {
              statusClass = 'bg-indigo-600 border-indigo-600 text-white shadow-lg ring-2 ring-indigo-100 scale-105 z-10';
            } else if (isMatched) {
              statusClass = PAIR_COLORS[Number(leftIdxMatch) % PAIR_COLORS.length] + ' shadow-sm opacity-90';
            }
            if (isExampleRight) statusClass += ' cursor-default';

            return (
              <button
                key={shIdx}
                onClick={() => handleClick('right', shIdx)}
                disabled={isExampleRight}
                className={`w-full text-right p-4 rounded-2xl border-2 text-sm font-semibold transition-all duration-300 transform active:scale-95 ${statusClass}`}
              >
                <div className="flex items-center justify-end gap-3">
                  {isExampleRight && <ExampleBadge />}
                  {isMatched && !checked && (
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/40 text-[9px] font-black uppercase tracking-tighter">
                      <Check size={10} strokeWidth={4} /> Juftlandi
                    </div>
                  )}
                  <span className="flex-1">{item.text}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex flex-col items-center gap-6 mt-12 pt-8 border-t border-border">
        {!checked ? (
          <div className="flex flex-col items-center gap-4">
            {selected && (
              <div className="flex items-center gap-2 px-4 py-1.5 bg-indigo-50 text-indigo-600 rounded-full text-xs font-bold animate-bounce">
                <Sparkles size={12} />
                Endi ikkinchi tomondan mosini tanlang
              </div>
            )}
            <button
              onClick={handleCheck}
              disabled={!allMatched}
              className="px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl font-black transition-all shadow-xl"
            >
              TEKSHIRISH
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-6 w-full animate-in zoom-in duration-500">
            <div className="relative flex items-center gap-4 px-8 py-4 student-card">
              <div className={`text-3xl font-black ${score === scorableIdxs.length ? 'text-emerald-500' : 'text-amber-500'}`}>
                {score} / {scorableIdxs.length}
              </div>
              <div className="h-10 w-px bg-border" />
              <div className="flex flex-col">
                <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Natija</span>
                <span className="text-sm font-bold stu-muted italic">
                  {score === scorableIdxs.length ? 'Mukammal!' : 'Yaxshi urinish!'}
                </span>
              </div>
            </div>
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-6 py-3 bg-surface-200 hover:bg-surface-100 border border-border stu-muted hover:text-indigo-600 rounded-xl text-xs font-black uppercase tracking-widest transition-all"
            >
              <RotateCcw size={14} strokeWidth={3} />
              QAYTA BOSHLASH
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
