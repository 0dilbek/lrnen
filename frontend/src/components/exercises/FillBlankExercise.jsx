import { useState } from 'react';
import { CheckCircle2, XCircle, RotateCcw, ChevronRight, Type } from 'lucide-react';

/**
 * content: {
 *   sentences: [{ text: "We ___ Australian.", answer: "are" }],
 *   word_panel: ["are", "is", "am"]   // optional
 * }
 */
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
  const [inputs, setInputs] = useState({});
  const [checked, setChecked] = useState(false);

  const setInput = (i, val) => {
    if (checked) return;
    setInputs((p) => ({ ...p, [i]: val }));
  };

  const clickWord = (word) => {
    if (checked) return;
    const emptyIdx = sentences.findIndex((_, i) => !inputs[i]);
    if (emptyIdx !== -1) setInput(emptyIdx, word);
  };

  const isCorrect = (i) =>
    (inputs[i] || '').trim().toLowerCase() ===
    sentences[i].answer.trim().toLowerCase();

  const allFilled = sentences.length > 0 && sentences.every((_, i) => inputs[i]);

  const handleCheck = () => {
    setChecked(true);
    const correct = sentences.filter((_, i) => isCorrect(i)).length;
    if (onComplete) onComplete(correct, sentences.length);
  };

  const handleRetry = () => {
    setInputs({});
    setChecked(false);
  };

  const score = checked
    ? sentences.filter((_, i) => isCorrect(i)).length
    : null;

  return (
    <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {word_panel && (
        <div className="mb-10 group">
          <div className="flex items-center gap-2 mb-3 ml-2">
            <Type size={14} className="text-indigo-400" />
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Tanlash uchun so'zlar</span>
          </div>
          <div className="flex flex-wrap gap-2.5 p-5 bg-white border border-slate-100 rounded-[2rem] shadow-xl shadow-slate-100/50">
            {word_panel.map((w, i) => (
              <button
                key={i}
                onClick={() => clickWord(w)}
                disabled={checked}
                className="px-5 py-2 bg-slate-50 border-2 border-slate-100 text-slate-600 rounded-xl text-sm font-bold hover:bg-indigo-600 hover:text-white hover:border-indigo-600 hover:shadow-lg hover:shadow-indigo-100 transition-all duration-300 transform active:scale-90 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {w}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-4 mb-10">
        {sentences.map((s, i) => {
          const correct = checked && isCorrect(i);
          const wrong = checked && !isCorrect(i);
          const parts = s.text.split('___');
          
          return (
            <div
              key={i}
              className={`group flex flex-wrap items-center gap-3 p-5 rounded-2xl border-2 transition-all duration-500 ${
                correct ? 'bg-emerald-50/50 border-emerald-200' :
                wrong   ? 'bg-rose-50/50 border-rose-200' :
                          'bg-white border-slate-50 hover:border-indigo-100 hover:shadow-md'
              }`}
            >
              <div className="flex items-center justify-center w-6 h-6 rounded-lg bg-slate-100 text-slate-400 text-[10px] font-black group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                {i + 1}
              </div>
              
              <span className="text-slate-700 font-semibold text-lg">{parts[0]}</span>
              
              <div className="relative">
                <input
                  type="text"
                  value={inputs[i] || ''}
                  onChange={(e) => setInput(i, e.target.value)}
                  disabled={checked}
                  placeholder="..."
                  className={`min-w-[100px] px-2 py-1 text-center border-b-4 bg-transparent outline-none text-lg font-black transition-all duration-300 ${
                    correct ? 'border-emerald-500 text-emerald-600' :
                    wrong   ? 'border-rose-400 text-rose-500' :
                              'border-indigo-200 text-indigo-700 focus:border-indigo-500 focus:scale-105'
                  }`}
                  style={{ width: `${Math.max(4, (inputs[i]?.length || 4))}ch` }}
                />
              </div>
              
              {parts[1] && <span className="text-slate-700 font-semibold text-lg">{parts[1]}</span>}
              
              {checked && (
                <div className="ml-auto flex items-center gap-3 animate-in slide-in-from-right-4 duration-500">
                  {correct
                    ? <CheckCircle2 size={24} className="text-emerald-500" />
                    : (
                      <div className="flex items-center gap-2">
                        <XCircle size={24} className="text-rose-400" />
                        <div className="px-3 py-1 bg-emerald-500 text-white rounded-lg text-xs font-black shadow-lg shadow-emerald-100">
                          {s.answer}
                        </div>
                      </div>
                    )
                  }
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex flex-col items-center gap-6 border-t border-slate-100 pt-10">
        {!checked ? (
          <button
            onClick={handleCheck}
            disabled={!allFilled}
            className="group flex items-center gap-3 px-10 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white rounded-[1.5rem] font-black text-lg transition-all duration-300 shadow-2xl shadow-indigo-200 hover:shadow-indigo-300 transform hover:-translate-y-1 active:translate-y-0"
          >
            TEKSHIRISH
            <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </button>
        ) : (
          <div className="flex flex-col items-center gap-6 w-full">
            <div className="flex items-center gap-5 px-8 py-4 bg-white border border-slate-100 rounded-3xl shadow-xl">
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">To'g'ri javoblar</span>
                <div className={`text-3xl font-black ${score === sentences.length ? 'text-emerald-500' : 'text-amber-500'}`}>
                  {score} / {sentences.length}
                </div>
              </div>
              <div className="h-12 w-px bg-slate-100" />
              <div className="text-sm font-bold text-slate-500 max-w-[120px] leading-tight">
                {score === sentences.length ? "Mukammal natija!" : "Xatolarni o'rganing va yana ko'ring."}
              </div>
            </div>
            
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-6 py-3 bg-slate-50 hover:bg-white border border-slate-200 text-slate-500 hover:text-indigo-600 rounded-2xl text-xs font-black uppercase tracking-[0.1em] transition-all duration-300"
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

