import { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

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
    <div>
      <div className="space-y-3 mb-5">
        {sentences.map((s, i) => {
          const chosen = answers[i];
          const isCorrect = checked && chosen === s.correct;
          const isWrong = checked && chosen !== s.correct && chosen !== undefined;
          return (
            <div
              key={i}
              className={`flex flex-wrap items-center gap-1 p-3 rounded-xl border transition text-sm ${
                isCorrect ? 'bg-green-50 border-green-200' :
                isWrong   ? 'bg-red-50 border-red-200' :
                            'bg-white border-gray-200'
              }`}
            >
              <span className="text-gray-500 font-medium mr-1">{i + 1}.</span>
              {s.before && <span className="text-gray-800">{s.before}</span>}
              <span className="inline-flex gap-1">
                {s.options.map((opt, oi) => (
                  <button
                    key={oi}
                    onClick={() => select(i, oi)}
                    className={`px-2.5 py-0.5 rounded-lg border font-medium transition text-sm ${
                      checked
                        ? oi === s.correct
                          ? 'bg-green-500 text-white border-green-500'
                          : oi === chosen
                            ? 'bg-red-400 text-white border-red-400'
                            : 'bg-gray-100 text-gray-400 border-gray-200'
                        : chosen === oi
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:text-blue-600'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </span>
              {s.after && <span className="text-gray-800">{s.after}</span>}
              {checked && (
                <span className="ml-auto">
                  {isCorrect
                    ? <CheckCircle size={16} className="text-green-500" />
                    : <XCircle size={16} className="text-red-400" />
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
          disabled={!allAnswered}
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
