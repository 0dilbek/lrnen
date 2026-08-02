import { useState, useMemo } from 'react';
import { CheckCircle2, XCircle, ChevronRight, RotateCcw } from 'lucide-react';
import ExampleBadge from './ExampleBadge';

/**
 * content: {
 *   sentences: [
 *     { before: "Jack ", options: ["are","is"], after: " 27 years old.", correct: 1 }
 *   ]
 * }
 */
function normalizeItems(content) {
  if (content?.sentences) return content.sentences;
  if (content?.items) {
    return content.items.map((item) => {
      const opts = item.options || [];
      const sentence = item.sentence || '';
      const combo = opts.join(' / ');
      const idx = sentence.indexOf(combo);
      if (idx !== -1) {
        return {
          before: sentence.substring(0, idx),
          options: opts,
          after: sentence.substring(idx + combo.length),
          correct: item.correct_index ?? 0,
        };
      }
      return { before: sentence, options: opts, after: '', correct: item.correct_index ?? 0 };
    });
  }
  if (content?.questions) {
    return content.questions.map((q) => ({
      before: q.question,
      options: q.options,
      after: '',
      correct: q.correct,
    }));
  }
  return [];
}

export default function ChooseCorrectExercise({ exercise, onComplete }) {
  const sentences = normalizeItems(exercise.content);
  const hasExample = sentences.length >= 2;
  const exampleAnswer = useMemo(
    () => (hasExample ? { 0: sentences[0].correct } : {}),
    [hasExample, sentences]
  );

  const [answers, setAnswers] = useState(() => ({ ...exampleAnswer }));
  const [checked, setChecked] = useState(false);

  const select = (idx, optIdx) => {
    if (checked || (hasExample && idx === 0)) return;
    setAnswers((a) => ({ ...a, [idx]: optIdx }));
  };

  const scorable = hasExample ? sentences.slice(1) : sentences;
  const allAnswered = scorable.every((_, i) => {
    const idx = hasExample ? i + 1 : i;
    return answers[idx] !== undefined;
  });

  const handleCheck = () => {
    setChecked(true);
    const correct = scorable.filter((s, i) => {
      const idx = hasExample ? i + 1 : i;
      return answers[idx] === s.correct;
    }).length;
    if (onComplete) onComplete(correct, scorable.length);
  };

  const handleRetry = () => {
    setAnswers({ ...exampleAnswer });
    setChecked(false);
  };

  const score = checked
    ? scorable.filter((s, i) => {
        const idx = hasExample ? i + 1 : i;
        return answers[idx] === s.correct;
      }).length
    : null;

  return (
    <div className="max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {hasExample && (
        <p className="text-xs stu-muted mb-4 italic">
          1-savol namuna — shunday yechiladi. Siz 2-savoldan boshlang.
        </p>
      )}
      <div className="space-y-4 mb-8">
        {sentences.map((s, i) => {
          const isExample = hasExample && i === 0;
          const chosen = answers[i];
          const isCorrect = checked && chosen === s.correct;
          const isWrong = checked && !isExample && chosen !== s.correct && chosen !== undefined;

          return (
            <div
              key={i}
              className={`group relative overflow-hidden p-5 rounded-2xl border transition-all duration-300 ${
                isExample
                  ? 'bg-amber-500/5 border-amber-500/30'
                  : isCorrect
                    ? 'bg-emerald-50/50 border-emerald-200 shadow-sm'
                    : isWrong
                      ? 'bg-rose-50/50 border-rose-200 shadow-sm'
                      : chosen !== undefined
                        ? 'bg-indigo-50/30 border-indigo-200 shadow-sm'
                        : 'bg-surface-100 border-border hover:border-indigo-300 hover:shadow-md'
              }`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-surface-200 text-slate-500 text-[10px] font-bold mr-1">
                  {i + 1}
                </span>
                {isExample && <ExampleBadge />}

                {s.before && <span className="stu-body font-medium leading-relaxed">{s.before}</span>}

                <div className="inline-flex items-center gap-1.5 p-1 bg-surface-200/60 rounded-xl border border-border shadow-inner">
                  {s.options.map((opt, oi) => {
                    const isSelected = chosen === oi;
                    const isTheCorrectOne = (checked || isExample) && oi === s.correct;
                    const isTheWrongOne = checked && !isExample && isSelected && oi !== s.correct;

                    return (
                      <button
                        key={oi}
                        onClick={() => select(i, oi)}
                        disabled={isExample || checked}
                        className={`px-4 py-1.5 rounded-lg font-semibold text-xs transition-all duration-300 transform active:scale-95 ${
                          isTheCorrectOne
                            ? 'bg-emerald-500 text-white shadow-lg scale-105 z-10'
                            : isTheWrongOne
                              ? 'bg-rose-500 text-white shadow-lg'
                              : isSelected
                                ? 'bg-indigo-600 text-white shadow-md'
                                : checked
                                  ? 'bg-surface-100 text-slate-400 cursor-default'
                                  : 'bg-surface-50 stu-body hover:text-indigo-600 hover:shadow-sm'
                        } ${isExample ? 'cursor-default' : ''}`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>

                {s.after && <span className="stu-body font-medium leading-relaxed">{s.after}</span>}

                {(checked || isExample) && (
                  <div className="ml-auto">
                    {isExample || isCorrect
                      ? <CheckCircle2 size={20} className="text-emerald-500" />
                      : isWrong
                        ? <XCircle size={20} className="text-rose-500" />
                        : null}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-center border-t border-border pt-8">
        {!checked ? (
          <button
            onClick={handleCheck}
            disabled={!allAnswered || scorable.length === 0}
            className="group flex items-center gap-2 px-8 py-3.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl font-bold transition-all shadow-lg"
          >
            Tekshirish
            <ChevronRight size={18} className="group-hover:translate-x-0.5 transition-transform" />
          </button>
        ) : (
          <div className="flex flex-col items-center gap-5 w-full">
            <div className="flex items-center gap-3 px-6 py-3 student-card">
              <div className={`text-2xl font-black ${score === scorable.length ? 'text-emerald-500' : 'text-amber-500'}`}>
                {score} / {scorable.length}
              </div>
              <div className="h-8 w-px bg-border mx-2" />
              <div className="text-sm stu-muted font-medium italic">
                {score === scorable.length ? 'Ajoyib natija!' : "Yana urinib ko'ring"}
              </div>
            </div>
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-6 py-2.5 bg-surface-200 hover:bg-surface-100 border border-border stu-body hover:text-indigo-600 rounded-xl text-xs font-bold transition-all"
            >
              <RotateCcw size={14} />
              Qayta urinish
            </button>
          </div>
        )}
      </div>
    </div>
  );
}