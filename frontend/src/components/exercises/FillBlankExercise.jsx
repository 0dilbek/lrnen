import { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

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
    // Bo'sh qolgan birinchi satrga qo'yish
    const emptyIdx = sentences.findIndex((_, i) => !inputs[i]);
    if (emptyIdx !== -1) setInput(emptyIdx, word);
  };

  const isCorrect = (i) =>
    (inputs[i] || '').trim().toLowerCase() ===
    sentences[i].answer.trim().toLowerCase();

  const allFilled = sentences.every((_, i) => inputs[i]);

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
    <div>
      {word_panel && (
        <div className="flex flex-wrap gap-2 mb-4 p-3 bg-blue-50 border border-blue-100 rounded-xl">
          {word_panel.map((w, i) => (
            <button
              key={i}
              onClick={() => clickWord(w)}
              disabled={checked}
              className="px-3 py-1 bg-white border border-blue-200 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-600 hover:text-white hover:border-blue-600 transition disabled:opacity-50"
            >
              {w}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-3 mb-5">
        {sentences.map((s, i) => {
          const correct = checked && isCorrect(i);
          const wrong = checked && !isCorrect(i);
          const parts = s.text.split('___');
          return (
            <div
              key={i}
              className={`flex flex-wrap items-center gap-1 p-3 rounded-xl border text-sm transition ${
                correct ? 'bg-green-50 border-green-200' :
                wrong   ? 'bg-red-50 border-red-200' :
                          'bg-white border-gray-200'
              }`}
            >
              <span className="text-gray-500 font-medium mr-1">{i + 1}.</span>
              <span className="text-gray-800">{parts[0]}</span>
              <input
                type="text"
                value={inputs[i] || ''}
                onChange={(e) => setInput(i, e.target.value)}
                disabled={checked}
                className={`w-28 text-center border-b-2 bg-transparent outline-none text-sm font-semibold transition ${
                  correct ? 'border-green-500 text-green-700' :
                  wrong   ? 'border-red-400 text-red-600' :
                            'border-blue-400 text-blue-700'
                }`}
              />
              {parts[1] && <span className="text-gray-800">{parts[1]}</span>}
              {checked && (
                <span className="ml-auto flex items-center gap-1">
                  {correct
                    ? <CheckCircle size={16} className="text-green-500" />
                    : <>
                        <XCircle size={16} className="text-red-400" />
                        <span className="text-xs text-green-600 font-medium">({s.answer})</span>
                      </>
                  }
                </span>
              )}
            </div>
          );
        })}
      </div>

      {!checked ? (
        <button
          onClick={handleCheck}
          disabled={!allFilled}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl text-sm font-medium transition"
        >
          Tekshirish
        </button>
      ) : (
        <div className="flex items-center gap-4">
          <span className={`text-sm font-semibold ${score === sentences.length ? 'text-green-600' : 'text-orange-500'}`}>
            {score}/{sentences.length} to'g'ri
          </span>
          <button
            onClick={handleRetry}
            className="px-5 py-2 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 transition"
          >
            Qayta urinish
          </button>
        </div>
      )}
    </div>
  );
}
