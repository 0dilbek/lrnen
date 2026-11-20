import { useMemo, useState } from 'react';
import { CheckCircle2, ChevronRight, RotateCcw, XCircle } from 'lucide-react';
import BookPageViewer from './BookPageViewer';
import ExampleBadge from './ExampleBadge';
import { useLanguage } from '../../context/LanguageContext';
import { exampleCountFor, shuffledIndices } from '../../utils/exerciseChoices';

const normalize = (value) => String(value || '')
  .replace(/[‘’]/g, "'")
  .trim()
  .toLowerCase()
  .replace(/\s+/g, ' ')
  .replace(/[.!?]+$/, '');

export default function WordOrderExercise({ exercise, onComplete }) {
  const { t } = useLanguage();
  const items = useMemo(() => exercise.content?.items || [], [exercise.content?.items]);
  const exampleCount = exampleCountFor(exercise.content, items.length);
  const hasExample = exampleCount > 0;
  const initial = useMemo(() => Object.fromEntries(items.map((item, index) => [
    index,
    index < exampleCount ? item.tokens.map((_, tokenIndex) => tokenIndex) : [],
  ])), [items, exampleCount]);
  const [shuffled, setShuffled] = useState(() => items.map((item) => shuffledIndices(item.tokens || [])));
  const [selected, setSelected] = useState(initial);
  const [checked, setChecked] = useState(false);

  const sentenceFor = (index) => (selected[index] || []).map((tokenIndex) => items[index].tokens[tokenIndex]).join(' ');
  const correctFor = (index) => normalize(sentenceFor(index)) === normalize(items[index].answer);
  const scorableIndices = items.map((_, index) => index).filter((index) => index >= exampleCount);
  const allDone = scorableIndices.length > 0 && scorableIndices.every((index) => selected[index]?.length === items[index].tokens.length);

  const addToken = (rowIndex, tokenIndex) => {
    if (checked || rowIndex < exampleCount || selected[rowIndex].includes(tokenIndex)) return;
    setSelected((current) => ({ ...current, [rowIndex]: [...current[rowIndex], tokenIndex] }));
  };

  const removeToken = (rowIndex, position) => {
    if (checked || rowIndex < exampleCount) return;
    setSelected((current) => ({
      ...current,
      [rowIndex]: current[rowIndex].filter((_, index) => index !== position),
    }));
  };

  const submit = () => {
    setChecked(true);
    const correct = scorableIndices.filter(correctFor).length;
    onComplete?.(correct, scorableIndices.length, {
      answers: scorableIndices.map(sentenceFor),
    });
  };

  const reset = () => {
    setSelected(initial);
    setShuffled(items.map((item) => shuffledIndices(item.tokens || [])));
    setChecked(false);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      {!!exercise.content?.pages?.length && <BookPageViewer pages={exercise.content.pages} title={t('Course Book manbasi')} />}
      {hasExample && <p className="text-xs italic stu-muted">{t('Birinchi gap namuna. So‘zlarni bosib to‘g‘ri gap tuzing.')}</p>}
      {items.map((item, rowIndex) => {
        const isExample = rowIndex < exampleCount;
        const isCorrect = (checked || isExample) && correctFor(rowIndex);
        return (
          <div key={rowIndex} className={`rounded-2xl border-2 p-4 ${isExample ? 'border-amber-500/30 bg-amber-500/5' : checked ? (isCorrect ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-rose-500/40 bg-rose-500/10') : 'border-border bg-surface-100'}`}>
            <div className="mb-3 flex items-center gap-2 text-xs font-bold stu-muted">
              <span>{rowIndex + 1}</span>{isExample && <ExampleBadge />}
              {(checked || isExample) && (isCorrect ? <CheckCircle2 size={16} className="text-emerald-500" /> : <XCircle size={16} className="text-rose-500" />)}
            </div>
            <div className="mb-3 flex min-h-14 flex-wrap gap-2 rounded-xl border border-dashed border-indigo-400/40 bg-indigo-500/5 p-3">
              {(selected[rowIndex] || []).map((tokenIndex, position) => (
                <button key={`${tokenIndex}-${position}`} type="button" onClick={() => removeToken(rowIndex, position)} disabled={isExample || checked} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-bold text-white shadow-sm disabled:cursor-default">
                  {item.tokens[tokenIndex]}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {shuffled[rowIndex].filter((tokenIndex) => !selected[rowIndex]?.includes(tokenIndex)).map((tokenIndex) => (
                <button key={tokenIndex} type="button" onClick={() => addToken(rowIndex, tokenIndex)} disabled={isExample || checked} className="rounded-lg border border-border bg-surface-200 px-3 py-2 text-sm font-semibold stu-body hover:border-indigo-400 disabled:opacity-40">
                  {item.tokens[tokenIndex]}
                </button>
              ))}
            </div>
            {checked && !isCorrect && <p className="mt-3 text-sm font-semibold text-emerald-600">{t('To‘g‘ri javob:')} {item.answer}</p>}
          </div>
        );
      })}
      <div className="flex justify-center border-t border-border pt-6">
        {!checked ? (
          <button type="button" onClick={submit} disabled={!allDone} className="admin-btn-primary px-8 py-3 disabled:opacity-40">{t('Tekshirish')} <ChevronRight size={18} /></button>
        ) : (
          <button type="button" onClick={reset} className="flex items-center gap-2 rounded-xl border border-border px-6 py-3 font-bold stu-body"><RotateCcw size={16} /> {t('Qayta urinish')}</button>
        )}
      </div>
    </div>
  );
}
