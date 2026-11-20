import { useState, useMemo } from 'react';
import { Check, CheckCircle2, XCircle, ChevronRight, RotateCcw } from 'lucide-react';
import ExampleBadge from './ExampleBadge';
import { useLanguage } from '../../context/LanguageContext';
import {
  answerMatches, correctIndices, exampleCountFor, isMultipleChoice, shuffledIndices,
} from '../../utils/exerciseChoices';

function normalizeItems(content) {
  const rows = content?.sentences || content?.items || content?.questions || [];
  return rows.map((row) => {
    if (row.before !== undefined || row.after !== undefined) return row;
    const sentence = row.question || row.sentence || row.text || '';
    const options = row.options || [];
    const combo = options.join(' / ');
    const position = combo ? sentence.indexOf(combo) : -1;
    return {
      ...row,
      before: position < 0 ? sentence : sentence.slice(0, position),
      options,
      after: position < 0 ? '' : sentence.slice(position + combo.length),
    };
  });
}

export default function ChooseCorrectExercise({ exercise, onComplete }) {
  const { t } = useLanguage();
  const sentences = useMemo(() => normalizeItems(exercise.content), [exercise.content]);
  const exampleCount = exampleCountFor(exercise.content, sentences.length);
  const exampleAnswers = useMemo(() => Object.fromEntries(
    sentences.slice(0, exampleCount).map((row, index) => [
      index, isMultipleChoice(row) ? correctIndices(row) : correctIndices(row)[0],
    ]),
  ), [sentences, exampleCount]);
  const [answers, setAnswers] = useState(() => ({ ...exampleAnswers }));
  const [checked, setChecked] = useState(false);
  const [optionOrders, setOptionOrders] = useState(() => sentences.map((row) => shuffledIndices(row.options || [])));
  const audioUrls = exercise.content?.audio_urls || [];

  const select = (rowIndex, originalIndex) => {
    if (checked || rowIndex < exampleCount) return;
    setAnswers((current) => {
      if (!isMultipleChoice(sentences[rowIndex])) return { ...current, [rowIndex]: originalIndex };
      const previous = Array.isArray(current[rowIndex]) ? current[rowIndex] : [];
      return {
        ...current,
        [rowIndex]: previous.includes(originalIndex)
          ? previous.filter((index) => index !== originalIndex)
          : [...previous, originalIndex],
      };
    });
  };

  const scorable = sentences.slice(exampleCount);
  const allAnswered = scorable.length > 0 && scorable.every((_, index) => {
    const answer = answers[index + exampleCount];
    return Array.isArray(answer) ? answer.length > 0 : answer !== undefined;
  });
  const score = scorable.filter((row, index) => answerMatches(row, answers[index + exampleCount])).length;

  const handleCheck = () => {
    if (!allAnswered) return;
    setChecked(true);
    onComplete?.(score, scorable.length, {
      // Always submit source indices, never shuffled display positions.
      answers: scorable.map((_, index) => answers[index + exampleCount]),
    });
  };

  const retry = () => {
    setAnswers({ ...exampleAnswers });
    setOptionOrders(sentences.map((row) => shuffledIndices(row.options || [])));
    setChecked(false);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      {exampleCount > 0 && <p className="text-xs italic stu-muted">{t('Belgilangani namuna. Qolgan savollarga javob bering.')}</p>}
      {sentences.map((row, rowIndex) => {
        const isExample = rowIndex < exampleCount;
        const multiple = isMultipleChoice(row);
        const selected = Array.isArray(answers[rowIndex]) ? answers[rowIndex] : [answers[rowIndex]];
        const rowCorrect = answerMatches(row, answers[rowIndex]);
        const correct = correctIndices(row);
        const audioUrl = audioUrls[rowIndex] || row.audio_url;
        return (
          <div key={rowIndex} className={`rounded-2xl border p-4 sm:p-5 ${isExample ? 'border-amber-500/30 bg-amber-500/5' : checked ? rowCorrect ? 'border-emerald-500/35 bg-emerald-500/10' : 'border-rose-500/35 bg-rose-500/10' : 'border-border bg-surface-100'}`}>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className="grid h-6 w-6 place-items-center rounded-full bg-surface-200 text-xs font-bold stu-muted">{rowIndex + 1}</span>
              {isExample && <ExampleBadge />}
              {row.before && <span className="whitespace-pre-line font-medium stu-body">{row.before}</span>}
              {(isExample || checked) && (rowCorrect ? <CheckCircle2 size={18} className="ml-auto text-emerald-500" /> : <XCircle size={18} className="ml-auto text-rose-500" />)}
            </div>
            {audioUrl && <audio src={audioUrl} controls controlsList="nodownload noremoteplayback" preload="metadata" disableRemotePlayback className="mb-3 h-9 w-full" />}
            {multiple && <p className="mb-2 text-xs font-semibold stu-muted">{t('Barcha to‘g‘ri javoblarni belgilang.')}</p>}
            <div className="flex flex-wrap gap-2" role="group" aria-label={t('Javob variantlari')}>
              {(optionOrders[rowIndex] || []).map((originalIndex) => {
                const chosen = selected.includes(originalIndex);
                const revealCorrect = (isExample || checked) && correct.includes(originalIndex);
                const revealWrong = checked && chosen && !correct.includes(originalIndex);
                return (
                  <button
                    key={originalIndex}
                    type="button"
                    role={multiple ? 'checkbox' : undefined}
                    aria-checked={multiple ? chosen : undefined}
                    aria-pressed={multiple ? undefined : chosen}
                    disabled={isExample || checked}
                    onClick={() => select(rowIndex, originalIndex)}
                    className={`flex min-h-11 max-w-full items-center gap-2 rounded-xl border px-3 py-2 text-left text-sm font-semibold transition ${revealCorrect ? 'border-emerald-500 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300' : revealWrong ? 'border-rose-500 bg-rose-500/15 text-rose-700 dark:text-rose-300' : chosen ? 'border-indigo-500 bg-indigo-500/15 text-indigo-700 dark:text-indigo-300' : 'border-border bg-surface-50 stu-body hover:border-indigo-400'} disabled:cursor-default`}
                  >
                    {multiple && <span className={`grid h-4 w-4 shrink-0 place-items-center rounded border ${chosen ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-current'}`}>{chosen && <Check size={12} />}</span>}
                    <span className="break-words">{row.options[originalIndex]}</span>
                  </button>
                );
              })}
            </div>
            {row.after && <p className="mt-3 font-medium stu-body">{row.after}</p>}
          </div>
        );
      })}
      <div className="flex flex-wrap items-center justify-center gap-4 border-t border-border pt-5">
        {!checked ? (
          <button type="button" onClick={handleCheck} disabled={!allAnswered} className="admin-btn-primary px-7 py-3 disabled:opacity-40">{t('Tekshirish')} <ChevronRight size={17} /></button>
        ) : (
          <>
            <p className={`text-xl font-black ${score === scorable.length ? 'text-emerald-500' : 'text-amber-500'}`}>{score} / {scorable.length}</p>
            <button type="button" onClick={retry} className="flex items-center gap-2 rounded-xl border border-border bg-surface-200 px-5 py-3 text-sm font-bold stu-body"><RotateCcw size={15} /> {t('Qayta urinish')}</button>
          </>
        )}
      </div>
    </div>
  );
}
