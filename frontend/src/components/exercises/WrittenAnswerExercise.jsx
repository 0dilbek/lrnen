import { useMemo, useState } from 'react';
import { CheckCircle2, ChevronRight, RotateCcw, XCircle } from 'lucide-react';
import BookPageViewer from './BookPageViewer';
import ExampleBadge from './ExampleBadge';
import { useLanguage } from '../../context/LanguageContext';

const normalize = (value) => String(value || '')
  .replace(/[‘’]/g, "'")
  .trim()
  .toLowerCase()
  .replace(/\s+/g, ' ')
  .replace(/[.!?]+$/, '');

export default function WrittenAnswerExercise({ exercise, onComplete }) {
  const { t } = useLanguage();
  const questions = useMemo(() => exercise.content?.questions || [], [exercise.content?.questions]);
  const hasExample = questions.length >= 2;
  const initial = useMemo(() => hasExample ? { 0: questions[0]?.answer || '' } : {}, [questions, hasExample]);
  const [answers, setAnswers] = useState(initial);
  const [checked, setChecked] = useState(false);
  const scorableIndices = questions.map((_, index) => index).filter((index) => !hasExample || index > 0);

  const correctFor = (index) => {
    const accepted = [questions[index].answer, ...(questions[index].alternatives || [])].map(normalize);
    return accepted.includes(normalize(answers[index]));
  };
  const allDone = scorableIndices.length > 0 && scorableIndices.every((index) => answers[index]?.trim());

  const submit = () => {
    setChecked(true);
    const correct = scorableIndices.filter(correctFor).length;
    onComplete?.(correct, scorableIndices.length, {
      answers: scorableIndices.map((index) => answers[index] || ''),
    });
  };

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      {!!exercise.content?.pages?.length && <BookPageViewer pages={exercise.content.pages} title={t('Course Book manbasi')} />}
      {hasExample && <p className="text-xs italic stu-muted">{t('Birinchi javob namuna. Qolgan javoblarni to‘liq gap bilan yozing.')}</p>}
      {questions.map((question, index) => {
        const isExample = hasExample && index === 0;
        const isCorrect = (checked || isExample) && correctFor(index);
        return (
          <div key={index} className={`rounded-2xl border-2 p-5 ${isExample ? 'border-amber-500/30 bg-amber-500/5' : checked ? (isCorrect ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-rose-500/40 bg-rose-500/10') : 'border-border bg-surface-100'}`}>
            <div className="mb-3 flex items-start gap-2">
              <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-surface-200 text-[10px] font-bold stu-muted">{index + 1}</span>
              {isExample && <ExampleBadge />}
              <p className="flex-1 font-semibold stu-body">{question.prompt}</p>
              {(checked || isExample) && (isCorrect ? <CheckCircle2 size={19} className="text-emerald-500" /> : <XCircle size={19} className="text-rose-500" />)}
            </div>
            <textarea value={answers[index] || ''} onChange={(event) => setAnswers((current) => ({ ...current, [index]: event.target.value }))} disabled={isExample || checked} rows={2} placeholder={t('Javobni inglizcha yozing...')} className="w-full resize-y rounded-xl border border-border bg-surface-50 px-4 py-3 text-sm stu-body outline-none focus:border-indigo-400 disabled:opacity-80" />
            {checked && !isCorrect && <p className="mt-3 text-sm font-semibold text-emerald-600">{t('To‘g‘ri javob:')} {question.answer}</p>}
          </div>
        );
      })}
      <div className="flex justify-center border-t border-border pt-6">
        {!checked ? <button type="button" onClick={submit} disabled={!allDone} className="admin-btn-primary px-8 py-3 disabled:opacity-40">{t('Tekshirish')} <ChevronRight size={18} /></button> : <button type="button" onClick={() => { setAnswers(initial); setChecked(false); }} className="flex items-center gap-2 rounded-xl border border-border px-6 py-3 font-bold stu-body"><RotateCcw size={16} /> {t('Qayta urinish')}</button>}
      </div>
    </div>
  );
}
