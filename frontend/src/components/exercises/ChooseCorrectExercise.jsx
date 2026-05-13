import { useState } from 'react';
import { CheckCircle2, XCircle, ChevronRight, RotateCcw } from 'lucide-react';

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
    return content.questions.map(q => ({
      before: q.question,
      options: q.options,
      after: "",
      correct: q.correct
    }));
  }
  return [];
}

export default function ChooseCorrectExercise({ exercise, onComplete }) {
  const sentences = normalizeItems(exercise.content);
  const [answers, setAnswers] = useState({});
  const [checked, setChecked] = useState(false);

  const select = (idx, optIdx) => {
    if (checked) return;
    setAnswers((a) => ({ ...a, [idx]: optIdx }));
  };

  const allAnswered = sentences.every((_, i) => answers[i] !== undefined);

  const handleCheck = () => {
    setChecked(true);
    const correct = sentences.filter((s, i) => answers[i] === s.correct).length;
    if (onComplete) onComplete(correct, sentences.length);
  };

  const handleRetry = () => {
    setAnswers({});
    setChecked(false);
  };

  const score = checked
    ? sentences.filter((s, i) => answers[i] === s.correct).length
    : null;

  return (
    <div className="max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="space-y-4 mb-8">
        {sentences.map((s, i) => {
          const chosen = answers[i];
          const isCorrect = checked && chosen === s.correct;
          const isWrong = checked && chosen !== s.correct && chosen !== undefined;
          
          return (
            <div
              key={i}
              className={`group relative overflow-hidden p-5 rounded-2xl border transition-all duration-300 ${
                isCorrect ? 'bg-emerald-50/50 border-emerald-200 shadow-sm shadow-emerald-100' :
                isWrong   ? 'bg-rose-50/50 border-rose-200 shadow-sm shadow-rose-100' :
                chosen !== undefined ? 'bg-indigo-50/30 border-indigo-200 shadow-sm' :
                            'bg-white/80 border-slate-200 hover:border-indigo-300 hover:shadow-md'
              } backdrop-blur-sm`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-500 text-[10px] font-bold mr-2 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                  {i + 1}
                </span>
                
                {s.before && <span className="text-slate-700 font-medium leading-relaxed">{s.before}</span>}
                
                <div className="inline-flex items-center gap-1.5 p-1 bg-slate-100/50 rounded-xl border border-slate-200/60 shadow-inner">
                  {s.options.map((opt, oi) => {
                    const isSelected = chosen === oi;
                    const isTheCorrectOne = checked && oi === s.correct;
                    const isTheWrongOne = checked && isSelected && oi !== s.correct;
                    
                    return (
                      <button
                        key={oi}
                        onClick={() => select(i, oi)}
                        className={`px-4 py-1.5 rounded-lg font-semibold text-xs transition-all duration-300 transform active:scale-95 ${
                          isTheCorrectOne
                            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-200 scale-105 z-10'
                            : isTheWrongOne
                              ? 'bg-rose-500 text-white shadow-lg shadow-rose-200'
                              : isSelected
                                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                                : checked
                                  ? 'bg-slate-50 text-slate-400 border-transparent cursor-default'
                                  : 'bg-white text-slate-600 hover:text-indigo-600 hover:shadow-sm'
                        }`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
                
                {s.after && <span className="text-slate-700 font-medium leading-relaxed">{s.after}</span>}
                
                {checked && (
                  <div className="ml-auto animate-in zoom-in duration-300">
                    {isCorrect
                      ? <CheckCircle2 size={20} className="text-emerald-500" />
                      : <XCircle size={20} className="text-rose-500" />
                    }
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-center border-t border-slate-100 pt-8">
        {!checked ? (
          <button
            onClick={handleCheck}
            disabled={!allAnswered}
            className="group flex items-center gap-2 px-8 py-3.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white rounded-2xl font-bold transition-all duration-300 shadow-xl shadow-indigo-100 hover:shadow-indigo-200 transform hover:-translate-y-0.5 active:translate-y-0"
          >
            Tekshirish
            <ChevronRight size={18} className="group-hover:translate-x-0.5 transition-transform" />
          </button>
        ) : (
          <div className="flex flex-col items-center gap-5 w-full">
            <div className="flex items-center gap-3 px-6 py-3 bg-white border border-slate-100 rounded-2xl shadow-sm">
              <div className={`text-2xl font-black ${score === sentences.length ? 'text-emerald-500' : 'text-amber-500'}`}>
                {score} / {sentences.length}
              </div>
              <div className="h-8 w-px bg-slate-100 mx-2" />
              <div className="text-sm text-slate-500 font-medium italic">
                {score === sentences.length ? "Ajoyib natija!" : "Yana urinib ko'ring"}
              </div>
            </div>
            
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-6 py-2.5 bg-slate-50 hover:bg-white border border-slate-200 text-slate-600 hover:text-indigo-600 rounded-xl text-xs font-bold transition-all duration-300 hover:shadow-md"
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

