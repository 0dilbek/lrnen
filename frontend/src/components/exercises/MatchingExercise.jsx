import { useState, useMemo } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

/**
 * content: {
 *   left:  ["What are you eating?", "Where are you going?"],
 *   right: ["A sandwich.", "To the library."],
 *   pairs: [0, 1]   // pairs[i] = right index matching left[i]
 * }
 */
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

export default function MatchingExercise({ exercise, onComplete }) {
  const { left, right, pairs } = normalizeMatching(exercise.content);

  // right tomonni aralashtirish
  const shuffledRight = useMemo(() => {
    const indexed = right.map((text, i) => ({ text, origIdx: i }));
    return indexed.sort(() => Math.random() - 0.5);
  }, []);

  const [selected, setSelected] = useState(null); // { side: 'left'|'right', idx }
  const [matches, setMatches] = useState({});     // { leftIdx: rightOrigIdx }
  const [checked, setChecked] = useState(false);

  const matchedRightOrigIdxs = new Set(Object.values(matches));
  const matchedLeftIdxs = new Set(Object.keys(matches).map(Number));

  const handleClick = (side, idx) => {
    if (checked) return;

    if (!selected) {
      setSelected({ side, idx });
      return;
    }

    if (selected.side === side) {
      setSelected({ side, idx });
      return;
    }

    // Pair aniqlash
    const leftIdx = side === 'left' ? idx : selected.idx;
    const rightShuffledIdx = side === 'right' ? idx : selected.idx;
    const rightOrigIdx = shuffledRight[rightShuffledIdx].origIdx;

    // Agar allaqachon matched bo'lsa, o'chirish
    const newMatches = { ...matches };
    // Remove any previous match for this leftIdx
    delete newMatches[leftIdx];
    // Remove any previous match where rightOrigIdx was used
    Object.keys(newMatches).forEach((k) => {
      if (newMatches[k] === rightOrigIdx) delete newMatches[k];
    });
    newMatches[leftIdx] = rightOrigIdx;

    setMatches(newMatches);
    setSelected(null);
  };

  const allMatched = left.every((_, i) => matches[i] !== undefined);

  const handleCheck = () => {
    setChecked(true);
    const correct = left.filter((_, i) => matches[i] === pairs[i]).length;
    if (onComplete) onComplete(correct, left.length);
  };

  const handleRetry = () => {
    setMatches({});
    setSelected(null);
    setChecked(false);
  };

  const getLeftStatus = (i) => {
    if (!checked) return null;
    return matches[i] === pairs[i] ? 'correct' : 'wrong';
  };

  const getRightStatus = (shIdx) => {
    if (!checked) return null;
    const origIdx = shuffledRight[shIdx].origIdx;
    const leftIdx = Object.keys(matches).find((k) => matches[k] === origIdx);
    if (leftIdx === undefined) return 'wrong';
    return Number(leftIdx) !== undefined && matches[Number(leftIdx)] === pairs[Number(leftIdx)]
      ? 'correct' : 'wrong';
  };

  const score = checked ? left.filter((_, i) => matches[i] === pairs[i]).length : null;

  const isLeftSelected = selected?.side === 'left';
  const isRightSelected = selected?.side === 'right';

  return (
    <div>
      <div className="grid grid-cols-2 gap-3 mb-5">
        {/* Left column */}
        <div className="space-y-2">
          {left.map((text, i) => {
            const isActive = isLeftSelected && selected.idx === i;
            const isMatched = matchedLeftIdxs.has(i);
            const status = getLeftStatus(i);
            return (
              <button
                key={i}
                onClick={() => handleClick('left', i)}
                className={`w-full text-left px-3 py-2.5 rounded-xl border text-sm transition ${
                  status === 'correct' ? 'bg-green-50 border-green-300 text-green-800' :
                  status === 'wrong'   ? 'bg-red-50 border-red-300 text-red-700' :
                  isActive ? 'bg-blue-600 text-white border-blue-600 shadow-md' :
                  isMatched ? 'bg-blue-50 border-blue-300 text-blue-800' :
                  'bg-white border-gray-200 text-gray-800 hover:border-blue-400'
                }`}
              >
                <span className="font-medium text-xs opacity-60 mr-1">{i + 1}.</span>
                {text}
              </button>
            );
          })}
        </div>

        {/* Right column */}
        <div className="space-y-2">
          {shuffledRight.map((item, shIdx) => {
            const isActive = isRightSelected && selected.idx === shIdx;
            const isMatched = matchedRightOrigIdxs.has(item.origIdx);
            const status = getRightStatus(shIdx);
            return (
              <button
                key={shIdx}
                onClick={() => handleClick('right', shIdx)}
                className={`w-full text-left px-3 py-2.5 rounded-xl border text-sm transition ${
                  status === 'correct' ? 'bg-green-50 border-green-300 text-green-800' :
                  status === 'wrong'   ? 'bg-red-50 border-red-300 text-red-700' :
                  isActive ? 'bg-purple-600 text-white border-purple-600 shadow-md' :
                  isMatched ? 'bg-purple-50 border-purple-300 text-purple-800' :
                  'bg-white border-gray-200 text-gray-800 hover:border-purple-400'
                }`}
              >
                {item.text}
              </button>
            );
          })}
        </div>
      </div>

      {selected && !checked && (
        <p className="text-xs text-blue-600 mb-3">
          ↑ Tanlandi — endi ikkinchi tomoni bosing
        </p>
      )}

      {!checked ? (
        <button
          onClick={handleCheck}
          disabled={!allMatched}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl text-sm font-medium transition"
        >
          Tekshirish
        </button>
      ) : (
        <div className="flex items-center gap-4">
          <span className={`text-sm font-semibold flex items-center gap-1.5 ${score === left.length ? 'text-green-600' : 'text-orange-500'}`}>
            {score === left.length
              ? <CheckCircle size={16} />
              : <XCircle size={16} />
            }
            {score}/{left.length} to'g'ri
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
