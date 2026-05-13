import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw, CheckCircle, XCircle, ArrowRight, Volume2 } from 'lucide-react';

const STAGE_INFO = [
  { label: '1. Tanishish', emoji: '👀', color: 'from-violet-500 to-purple-600' },
  { label: '2. EN → UZ',   emoji: '🇺🇿', color: 'from-blue-500 to-cyan-500'    },
  { label: '3. UZ → EN',   emoji: '🇬🇧', color: 'from-emerald-500 to-teal-500' },
  { label: '4. Yozish',    emoji: '✍️',  color: 'from-orange-400 to-rose-500'  },
];

const speak = (text) => {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
};

export default function VocabStudy({ words }) {
  const [stage, setStage] = useState(0);

  if (!words || words.length === 0) return null;

  return (
    <div>
      {/* Stage stepper */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {STAGE_INFO.map((s, i) => (
          <div
            key={i}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
              stage === i
                ? `bg-gradient-to-r ${s.color} text-white shadow-sm scale-105`
                : stage > i
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-400'
            }`}
          >
            {stage > i ? <CheckCircle size={12} /> : <span>{s.emoji}</span>}
            {s.label}
          </div>
        ))}
      </div>

      {stage === 0 && <Flashcards words={words} onComplete={() => setStage(1)} />}
      {stage === 1 && <MCQQuiz words={words} mode="en_to_uz" onComplete={() => setStage(2)} />}
      {stage === 2 && <MCQQuiz words={words} mode="uz_to_en" onComplete={() => setStage(3)} />}
      {stage === 3 && <TypingQuiz words={words} onComplete={() => setStage(4)} />}
      {stage === 4 && <CompletionScreen onRestart={() => setStage(0)} />}
    </div>
  );
}

/* ── 1. FLASHCARDS ──────────────────────────────────────────────────── */
const CARD_COLORS = [
  'from-violet-400 to-purple-500',
  'from-blue-400 to-cyan-500',
  'from-emerald-400 to-teal-500',
  'from-orange-400 to-rose-400',
  'from-pink-400 to-fuchsia-500',
  'from-yellow-400 to-orange-400',
];

function Flashcards({ words, onComplete }) {
  const [idx, setIdx]       = useState(0);
  const [flipped, setFlipped] = useState(false);

  const word   = words[idx];
  const isLast = idx === words.length - 1;
  const grad   = CARD_COLORS[idx % CARD_COLORS.length];

  const next = () => { if (isLast) { onComplete(); return; } setIdx(i => i + 1); setFlipped(false); };
  const prev = () => { setIdx(i => Math.max(0, i - 1)); setFlipped(false); };

  const handleSpeak = (e) => {
    e.stopPropagation();
    speak(word.word);
  };

  return (
    <div>
      <p className="text-sm text-gray-400 mb-4 font-medium">
        {idx + 1} / {words.length} — kartani bosib, tarjimani ko'ring 👆
      </p>

      {/* Flip card */}
      <style>{`
        .flip-inner { transition: transform 0.5s; transform-style: preserve-3d; }
        .flipped .flip-inner { transform: rotateY(180deg); }
        .flip-front, .flip-back { backface-visibility: hidden; -webkit-backface-visibility: hidden; }
        .flip-back { transform: rotateY(180deg); }
      `}</style>

      <div
        className={`cursor-pointer select-none h-48 mb-6 relative ${flipped ? 'flipped' : ''}`}
        style={{ perspective: '1000px' }}
        onClick={() => setFlipped(f => !f)}
      >
        <div className="flip-inner w-full h-full relative">
          {/* Front */}
          <div className={`flip-front absolute inset-0 bg-gradient-to-br ${grad} rounded-2xl shadow-lg flex flex-col items-center justify-center p-8`}>
            <div className="flex items-center gap-3">
              <p className="text-4xl font-extrabold text-white mb-2 tracking-wide">{word.word}</p>
              <button 
                onClick={handleSpeak}
                className="p-2 rounded-full bg-white/20 hover:bg-white/40 text-white transition-all scale-110"
                title="O'qish"
              >
                <Volume2 size={24} />
              </button>
            </div>
            {word.example && (
              <p className="text-sm text-white/70 italic text-center mt-2">"{word.example}"</p>
            )}
            <p className="text-white/50 text-xs mt-4">Bosing →</p>
          </div>
          {/* Back */}
          <div className="flip-back absolute inset-0 bg-white border-2 border-gray-100 rounded-2xl shadow-lg flex flex-col items-center justify-center p-8">
            <p className="text-3xl font-extrabold text-gray-900 mb-1">{word.translation}</p>
            <div className="flex items-center gap-2 mt-1">
              <p className={`text-lg font-semibold bg-gradient-to-r ${grad} bg-clip-text text-transparent`}>{word.word}</p>
              <button 
                onClick={handleSpeak}
                className="p-1 rounded-full text-gray-300 hover:text-blue-500 transition-colors"
              >
                <Volume2 size={16} />
              </button>
            </div>
            {word.example && (
              <p className="text-xs text-gray-400 italic text-center mt-3">"{word.example}"</p>
            )}
          </div>
        </div>
      </div>

      {/* Dot progress */}
      <div className="flex items-center gap-3 mb-4">
        <button onClick={prev} disabled={idx === 0}
          className="p-2 rounded-xl border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 transition">
          <ChevronLeft size={18} />
        </button>
        <div className="flex-1 flex gap-1 justify-center flex-wrap">
          {words.map((_, i) => (
            <div key={i} className={`h-2 rounded-full transition-all ${
              i === idx ? 'w-6 bg-gradient-to-r from-violet-500 to-purple-600' :
              i < idx   ? 'w-2 bg-green-400' : 'w-2 bg-gray-200'
            }`} />
          ))}
        </div>
        <button onClick={next}
          className={`flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-bold transition text-white bg-gradient-to-r ${grad} hover:shadow-md`}>
          {isLast ? 'Testga o\'tish' : 'Keyingi'}
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}

/* ── 2 & 3. MCQ QUIZ ───────────────────────────────────────────────── */
function MCQQuiz({ words, mode, onComplete }) {
  const [idx, setIdx]       = useState(0);
  const [selected, setSelected] = useState(null);
  const [results, setResults]   = useState([]);

  const word    = words[idx];
  const isLast  = idx === words.length - 1;
  const title   = mode === 'en_to_uz'
    ? '🇺🇿 Inglizcha so\'zning o\'zbekcha tarjimasini toping'
    : '🇬🇧 O\'zbekcha so\'zning inglizcha tarjimasini toping';

  const options = useMemo(() => {
    const correct = mode === 'en_to_uz' ? word.translation : word.word;
    const pool    = words.filter(w => w.id !== word.id)
                         .map(w => mode === 'en_to_uz' ? w.translation : w.word);
    const others  = pool.sort(() => Math.random() - 0.5).slice(0, 3);
    return [...others, correct].sort(() => Math.random() - 0.5);
  }, [idx, words, mode]);

  const question   = mode === 'en_to_uz' ? word.word      : word.translation;
  const correct    = mode === 'en_to_uz' ? word.translation : word.word;
  const isAnswered = selected !== null;
  const score      = results.filter(Boolean).length;

  const handleSelect = (opt) => {
    if (isAnswered) return;
    setSelected(opt);
    setResults(r => [...r, opt === correct]);
    // MCQ'da inglizcha so'zni avtomatik o'qish (faqat EN->UZ rejimida)
    if (mode === 'en_to_uz') {
      speak(word.word);
    }
  };

  const handleNext = () => {
    if (isLast) { onComplete(); } else { setIdx(i => i + 1); setSelected(null); }
  };

  return (
    <div>
      <p className="text-xs font-bold text-gray-400 mb-1">{idx + 1} / {words.length}</p>
      <p className="text-sm font-semibold text-gray-600 mb-5">{title}</p>

      {/* Question card */}
      <div className="bg-gradient-to-br from-blue-50 to-violet-50 border border-blue-100 rounded-2xl p-6 mb-5 text-center relative group">
        <div className="flex items-center justify-center gap-3">
          <p className="text-3xl font-extrabold text-gray-900">{question}</p>
          {mode === 'en_to_uz' && (
            <button 
              onClick={() => speak(word.word)}
              className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
            >
              <Volume2 size={20} />
            </button>
          )}
        </div>
        {mode === 'en_to_uz' && word.example && (
          <p className="text-xs text-gray-400 italic mt-2">"{word.example}"</p>
        )}
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-2.5 mb-5">
        {options.map((opt, i) => {
          const isCorrect = opt === correct;
          const isChosen  = opt === selected;
          let cls = 'border-gray-200 text-gray-700 hover:border-blue-400 hover:bg-blue-50 hover:scale-[1.02]';
          if (isAnswered) {
            if (isCorrect)             cls = 'border-green-400 bg-green-50 text-green-800 scale-[1.02]';
            else if (isChosen)         cls = 'border-red-400 bg-red-50 text-red-700';
            else                       cls = 'border-gray-100 text-gray-300 opacity-60';
          }
          return (
            <button key={i} onClick={() => handleSelect(opt)}
              className={`px-4 py-3.5 rounded-xl border-2 text-sm font-semibold text-left transition-all duration-200 flex items-center gap-2 ${cls}`}>
              {isAnswered && isCorrect && <CheckCircle size={14} className="text-green-600 shrink-0" />}
              {isAnswered && isChosen && !isCorrect && <XCircle size={14} className="text-red-500 shrink-0" />}
              {opt}
              {isAnswered && isCorrect && mode === 'uz_to_en' && (
                <Volume2 size={12} className="ml-auto text-green-600" />
              )}
            </button>
          );
        })}
      </div>

      {isAnswered && (
        <div className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3">
          <span className={`text-sm font-bold flex items-center gap-1.5 ${selected === correct ? 'text-green-600' : 'text-red-500'}`}>
            {selected === correct ? '✅ To\'g\'ri!' : `❌ To'g'risi: "${correct}"`}
          </span>
          <button onClick={handleNext}
            className="flex items-center gap-1.5 px-5 py-2 bg-gradient-to-r from-blue-500 to-violet-600 text-white rounded-xl text-sm font-bold transition hover:shadow-md">
            {isLast ? `Natija: ${score}/${words.length}` : 'Keyingi'}
            <ArrowRight size={15} />
          </button>
        </div>
      )}
    </div>
  );
}

/* ── 4. TYPING QUIZ ─────────────────────────────────────────────────── */
function TypingQuiz({ words, onComplete }) {
  const [idx, setIdx]       = useState(0);
  const [input, setInput]   = useState('');
  const [checked, setChecked] = useState(false);
  const [results, setResults] = useState([]);

  const word   = words[idx];
  const isLast = idx === words.length - 1;
  const normalize = s => s.trim().toLowerCase();
  const isCorrect  = normalize(input) === normalize(word.word);
  const score      = results.filter(Boolean).length;

  const handleCheck = () => { 
    setChecked(true); 
    setResults(r => [...r, isCorrect]);
    // To'g'ri yozilsa yoki tekshirilganda inglizcha talaffuzni eshittirish
    speak(word.word);
  };
  const handleNext  = () => {
    if (isLast) { onComplete(); return; }
    setIdx(i => i + 1); setInput(''); setChecked(false);
  };

  return (
    <div>
      <p className="text-xs font-bold text-gray-400 mb-1">{idx + 1} / {words.length}</p>
      <p className="text-sm font-semibold text-gray-600 mb-5">✍️ O'zbekcha so'zni ko'rib, inglizcha yozing</p>

      {/* Question */}
      <div className="bg-gradient-to-br from-orange-50 to-rose-50 border border-orange-100 rounded-2xl p-6 mb-5 text-center">
        <p className="text-3xl font-extrabold text-gray-900">{word.translation}</p>
      </div>

      {/* Input */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={e => !checked && setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !checked && input.trim() && handleCheck()}
            disabled={checked}
            placeholder="Inglizcha so'zni yozing..."
            autoFocus
            className={`w-full px-4 py-3.5 border-2 rounded-xl text-base font-semibold focus:outline-none transition-all ${
              checked
                ? isCorrect
                  ? 'border-green-400 bg-green-50 text-green-800'
                  : 'border-red-400 bg-red-50 text-red-700'
                : 'border-gray-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100'
            }`}
          />
          {checked && (
            <button 
              onClick={() => speak(word.word)}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-blue-500"
            >
              <Volume2 size={20} />
            </button>
          )}
        </div>
        {checked && !isCorrect && (
          <p className="mt-2 text-sm text-green-700 font-semibold bg-green-50 px-3 py-1.5 rounded-lg">
            ✅ To'g'ri javob: <span className="font-extrabold">{word.word}</span>
          </p>
        )}
      </div>

      {/* Hint */}
      {!checked && input.length === 0 && (
        <p className="text-xs text-gray-400 mb-3 font-medium">
          💡 Birinchi harf: <span className="font-extrabold text-gray-600">{word.word[0].toUpperCase()}</span>
          {'_ '.repeat(word.word.length - 1).trim()}
        </p>
      )}

      <div className="flex items-center justify-between">
        {!checked ? (
          <button onClick={handleCheck} disabled={!input.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-orange-400 to-rose-500 disabled:opacity-40 text-white rounded-xl text-sm font-bold transition hover:shadow-md">
            Tekshirish ✔
          </button>
        ) : (
          <div className="flex items-center gap-4 w-full justify-between bg-gray-50 rounded-xl px-4 py-3">
            <span className={`text-sm font-bold flex items-center gap-1.5 ${isCorrect ? 'text-green-600' : 'text-red-500'}`}>
              {isCorrect ? <CheckCircle size={16} /> : <XCircle size={16} />}
              {isCorrect ? 'To\'g\'ri!' : 'Noto\'g\'ri'}
            </span>
            <button onClick={handleNext}
              className="flex items-center gap-1.5 px-5 py-2 bg-gradient-to-r from-blue-500 to-violet-600 text-white rounded-xl text-sm font-bold transition hover:shadow-md">
              {isLast ? `Tugash (${score}/${words.length})` : 'Keyingi'}
              <ArrowRight size={15} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Completion screen ──────────────────────────────────────────────── */
function CompletionScreen({ onRestart }) {
  return (
    <div className="text-center py-10">
      <div className="text-6xl mb-4">🎉</div>
      <h3 className="text-2xl font-extrabold text-gray-900 mb-2">Tabriklaymiz!</h3>
      <p className="text-gray-500 mb-6">Barcha so'zlarni 4 bosqichda o'zlashtirdingiz!</p>
      <div className="flex items-center justify-center gap-2 flex-wrap">
        {['🏆','⭐','🔥','💪','✨'].map((e,i) => (
          <span key={i} className="text-3xl animate-bounce" style={{ animationDelay: `${i*0.1}s` }}>{e}</span>
        ))}
      </div>
      <button onClick={onRestart}
        className="mt-6 flex items-center gap-2 mx-auto px-6 py-2.5 border-2 border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
        <RotateCcw size={15} /> Qayta o'rganish
      </button>
    </div>
  );
}
