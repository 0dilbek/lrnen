import { useState } from 'react';
import { CheckCircle2, XCircle, RotateCcw, ChevronRight, Type } from 'lucide-react';
import ExampleBadge from './ExampleBadge';

function normalizeContent(content) {
  if (content?.sentences) return { sentences: content.sentences, word_panel: content.word_panel };
  if (content?.items) {
    return {
      sentences: content.items.map((item) => ({
        text: item.sentence || item.text || '',
        answer: item.answer || '',
      })),
      word_panel: content.word_panel,
    };
  }
  return { sentences: [], word_panel: undefined };
}

export default function FillBlankExercise({ exercise, onComplete }) {
  const { sentences, word_panel } = normalizeContent(exercise.content);
  const hasExample = sentences.length >= 2;
  const answersFor = (sentence) => Array.isArray(sentence.answer) ? sentence.answer : [sentence.answer];
  const inputKey = (sentenceIndex, answerIndex) => `${sentenceIndex}:${answerIndex}`;
  const exampleInputs = hasExample
    ? Object.fromEntries(answersFor(sentences[0]).map((answer, index) => [inputKey(0, index), answer]))
    : {};

  const [inputs, setInputs] = useState(() => ({ ...exampleInputs }));
  const [checked, setChecked] = useState(false);

  const setInput = (i, answerIndex, val) => {
    if (checked || (hasExample && i === 0)) return;
    setInputs((p) => ({ ...p, [inputKey(i, answerIndex)]: val }));
  };

  const clickWord = (word) => {
    if (checked) return;
    for (let i = 0; i < sentences.length; i += 1) {
      if (hasExample && i === 0) continue;
      const answerIndex = answersFor(sentences[i]).findIndex((_, index) => !inputs[inputKey(i, index)]);
      if (answerIndex !== -1) {
        setInput(i, answerIndex, word);
        break;
      }
    }
  };

  const normalize = (value) => String(value || '')
    .replace(/[‘’]/g, "'")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[.!?]+$/, '');
  const acceptedFor = (sentence, answerIndex) => {
    const primary = answersFor(sentence)[answerIndex];
    const alternatives = (sentence.alternatives || []).flatMap((alternative) =>
      Array.isArray(alternative) ? [alternative[answerIndex]] : (answerIndex === 0 ? [alternative] : []));
    return [primary, ...alternatives].filter((value) => value !== undefined && value !== null).map(normalize);
  };
  const isCorrect = (i) => answersFor(sentences[i]).every((_, answerIndex) =>
    acceptedFor(sentences[i], answerIndex).includes(normalize(inputs[inputKey(i, answerIndex)])));

  const scorable = hasExample ? sentences.slice(1) : sentences;
  const allFilled = scorable.length > 0 && scorable.every((_, i) => {
    const idx = hasExample ? i + 1 : i;
    return answersFor(sentences[idx]).every((_, answerIndex) => !!inputs[inputKey(idx, answerIndex)]);
  });

  const handleCheck = () => {
    setChecked(true);
    const correct = scorable.filter((_, i) => isCorrect(hasExample ? i + 1 : i)).length;
    if (onComplete) onComplete(correct, scorable.length, {
      answers: scorable.map((_, i) => {
        const sentenceIndex = hasExample ? i + 1 : i;
        const values = answersFor(sentences[sentenceIndex]).map((_, answerIndex) => inputs[inputKey(sentenceIndex, answerIndex)] || '');
        return values.length === 1 ? values[0] : values;
      }),
    });
  };

  const handleRetry = () => {
    setInputs({ ...exampleInputs });
    setChecked(false);
  };

  const score = checked
    ? scorable.filter((_, i) => isCorrect(hasExample ? i + 1 : i)).length
    : null;

  return (
    <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {hasExample && (
        <p className="text-xs stu-muted mb-4 italic">
          1-savol namuna — shunday yechiladi. Siz 2-savoldan boshlang.
        </p>
      )}

      {word_panel && (
        <div className="mb-10 group">
          <div className="flex items-center gap-2 mb-3 ml-2">
            <Type size={14} className="text-indigo-400" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em] stu-muted">Tanlash uchun so'zlar</span>
          </div>
          <div className="flex flex-wrap gap-2.5 p-5 student-panel">
            {word_panel.map((w, i) => (
              <button
                key={i}
                onClick={() => clickWord(w)}
                disabled={checked}
                className="px-5 py-2 bg-surface-200 border-2 border-border stu-body rounded-xl text-sm font-bold hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {w}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-4 mb-10">
        {sentences.map((s, i) => {
          const isExample = hasExample && i === 0;
          const correct = (checked || isExample) && isCorrect(i);
          const wrong = checked && !isExample && !isCorrect(i);
          const answers = answersFor(s);
          const parts = s.text.split('___');

          return (
            <div
              key={i}
              className={`group flex flex-wrap items-center gap-3 p-5 rounded-2xl border-2 transition-all duration-500 ${
                isExample ? 'bg-amber-500/5 border-amber-500/30' :
                correct ? 'bg-emerald-500/10 border-emerald-500/35' :
                wrong   ? 'bg-rose-500/10 border-rose-500/35' :
                          'bg-surface-100 border-border hover:border-indigo-200'
              }`}
            >
              <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-surface-200 text-[10px] font-black stu-muted">
                {i + 1}
              </div>
              {isExample && <ExampleBadge />}

              {answers.map((_, answerIndex) => {
                const key = inputKey(i, answerIndex);
                return (
                  <span key={key} className="contents">
                    {parts[answerIndex] && <span className="stu-body font-semibold text-lg">{parts[answerIndex]}</span>}
                    <span className="relative">
                      <input
                        type="text"
                        value={inputs[key] || ''}
                        onChange={(e) => setInput(i, answerIndex, e.target.value)}
                        disabled={checked || isExample}
                        placeholder="..."
                        className={`min-w-[100px] px-2 py-1 text-center border-b-4 bg-transparent outline-none text-lg font-black transition-all duration-300 ${
                          correct ? 'border-emerald-500 text-emerald-700 dark:text-emerald-300' :
                          wrong   ? 'border-rose-400 text-rose-600 dark:text-rose-300' :
                                    'border-indigo-400 text-indigo-700 dark:text-indigo-300 focus:border-indigo-500'
                        } ${isExample ? 'cursor-default' : ''}`}
                        style={{ width: `${Math.max(4, (inputs[key]?.length || 4))}ch` }}
                      />
                    </span>
                  </span>
                );
              })}
              {parts[answers.length] && <span className="stu-body font-semibold text-lg">{parts[answers.length]}</span>}

              {(checked || isExample) && (
                <div className="ml-auto flex items-center gap-3">
                  {correct
                    ? <CheckCircle2 size={24} className="text-emerald-500" />
                    : wrong && (
                      <div className="flex items-center gap-2">
                        <XCircle size={24} className="text-rose-400" />
                        <div className="px-3 py-1 bg-emerald-500 text-white rounded-lg text-xs font-black">
                          {answers.join(' · ')}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex flex-col items-center gap-6 border-t border-border pt-10">
        {!checked ? (
          <button
            onClick={handleCheck}
            disabled={!allFilled || scorable.length === 0}
            className="group flex items-center gap-3 px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-[1.5rem] font-black text-lg transition-all shadow-xl"
          >
            TEKSHIRISH
            <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </button>
        ) : (
          <div className="flex flex-col items-center gap-6 w-full">
            <div className="flex items-center gap-5 px-8 py-4 student-card">
              <div className="flex flex-col">
                <span className="text-[10px] font-black uppercase tracking-widest stu-muted">To'g'ri javoblar</span>
                <div className={`text-3xl font-black ${score === scorable.length ? 'text-emerald-500' : 'text-amber-500'}`}>
                  {score} / {scorable.length}
                </div>
              </div>
              <div className="h-12 w-px bg-border" />
              <div className="text-sm font-bold stu-muted max-w-[120px] leading-tight">
                {score === scorable.length ? 'Mukammal natija!' : "Xatolarni o'rganing va yana ko'ring."}
              </div>
            </div>
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-6 py-3 bg-surface-200 hover:bg-surface-100 border border-border stu-muted hover:text-indigo-600 rounded-2xl text-xs font-black uppercase tracking-[0.1em] transition-all"
            >
              <RotateCcw size={14} strokeWidth={3} />
              QAYTA URINISH
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
