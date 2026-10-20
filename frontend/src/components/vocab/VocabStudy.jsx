import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw, CheckCircle, XCircle, ArrowRight, Volume2 } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

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

function randomShuffle(values) {
  const shuffled = [...values];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
  }
  return shuffled;
}

export default function VocabStudy({ words }) {
  const [stage, setStage] = useState(0);
  const { language, t } = useLanguage();
  const languageCode = language === 'kaa' ? 'KAA' : 'UZ';

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
                ? 'bg-emerald-500/15 text-emerald-400'
                : 'bg-surface-200 stu-muted'
            }`}
          >
            {stage > i ? <CheckCircle size={12} /> : <span>{s.emoji}</span>}
            {i === 1 ? `2. EN → ${languageCode}` : i === 2 ? `3. ${languageCode} → EN` : t(s.label)}
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
      <p className="mb-4 text-sm font-medium stu-muted">
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
          <div className="flip-back absolute inset-0 bg-surface-100 border-2 border-border rounded-2xl shadow-lg flex flex-col items-center justify-center p-8">
            <p className="text-3xl font-extrabold stu-title mb-1">{word.translation}</p>
            <div className="flex items-center gap-2 mt-1">
              <p className={`text-lg font-semibold bg-gradient-to-r ${grad} bg-clip-text text-transparent`}>{word.word}</p>
              <button 
                onClick={handleSpeak}
                className="rounded-full p-1 stu-muted transition-colors hover:text-indigo-500"
              >
                <Volume2 size={16} />
              </button>
            </div>
            {word.example && (
              <p className="mt-3 text-center text-xs italic stu-muted">"{word.example}"</p>
            )}
          </div>
        </div>
      </div>

      {/* Dot progress */}
      <div className="flex items-center gap-3 mb-4">
        <button onClick={prev} disabled={idx === 0}
          className="rounded-xl border border-border p-2 stu-muted transition hover:bg-surface-200 disabled:opacity-30">
          <ChevronLeft size={18} />
        </button>
        <div className="flex-1 flex gap-1 justify-center flex-wrap">
          {words.map((_, i) => (
            <div key={i} className={`h-2 rounded-full transition-all ${
              i === idx ? 'w-6 bg-gradient-to-r from-violet-500 to-purple-600' :
              i < idx   ? 'w-2 bg-emerald-400' : 'w-2 bg-surface-300'
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
    const pool = [...new Set(
      words
        .filter((candidate) => candidate.id !== word.id)
        .map((candidate) => mode === 'en_to_uz' ? candidate.translation : candidate.word)
        .filter((value) => value && value !== correct),
    )];
    const others = randomShuffle(pool).slice(0, 3);
    return randomShuffle([...others, correct]);
  }, [words, mode, word]);

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
      <p className="mb-1 text-xs font-bold stu-muted">{idx + 1} / {words.length}</p>
      <p className="mb-5 text-sm font-semibold stu-body">{title}</p>

      {/* Question card */}
      <div className="group relative mb-5 rounded-2xl border border-blue-500/20 bg-gradient-to-br from-blue-500/10 to-violet-500/10 p-6 text-center">
        <div className="flex items-center justify-center gap-3">
          <p className="text-3xl font-extrabold stu-title">{question}</p>
          {mode === 'en_to_uz' && (
            <button 
              onClick={() => speak(word.word)}
              className="rounded-full bg-blue-500/15 p-2 text-blue-600 transition-colors hover:bg-blue-500/25 dark:text-blue-300"
            >
              <Volume2 size={20} />
            </button>
          )}
        </div>
        {mode === 'en_to_uz' && word.example && (
          <p className="mt-2 text-xs italic stu-muted">"{word.example}"</p>
        )}
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-2.5 mb-5">
        {options.map((opt, i) => {
          const isCorrect = opt === correct;
          const isChosen  = opt === selected;
          let cls = 'border-border bg-surface-100 stu-body hover:border-indigo-500/40 hover:bg-indigo-500/10 hover:scale-[1.02]';
          if (isAnswered) {
            if (isCorrect)             cls = 'border-green-500 bg-green-500/10 text-green-700 dark:text-green-300 scale-[1.02]';
            else if (isChosen)         cls = 'border-red-500 bg-red-500/10 text-red-700 dark:text-red-300';
            else                       cls = 'border-border bg-surface-200 stu-muted opacity-60';
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
        <div className="flex items-center justify-between bg-surface-200/50 rounded-xl px-4 py-3">
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
      <p className="mb-1 text-xs font-bold stu-muted">{idx + 1} / {words.length}</p>
      <p className="mb-5 text-sm font-semibold stu-body">✍️ O'zbekcha so'zni ko'rib, inglizcha yozing</p>

      {/* Question */}
      <div className="mb-5 rounded-2xl border border-orange-500/20 bg-gradient-to-br from-orange-500/10 to-rose-500/10 p-6 text-center">
        <p className="text-3xl font-extrabold stu-title">{word.translation}</p>
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
                  ? 'border-green-500 bg-green-500/10 text-green-700 dark:text-green-300'
                  : 'border-red-500 bg-red-500/10 text-red-700 dark:text-red-300'
                : 'border-border bg-surface-100 stu-body focus:border-violet-400 focus:ring-2 focus:ring-violet-500/20'
            }`}
          />
          {checked && (
            <button 
              onClick={() => speak(word.word)}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 stu-muted hover:text-blue-500"
            >
              <Volume2 size={20} />
            </button>
          )}
        </div>
        {checked && !isCorrect && (
          <p className="mt-2 rounded-lg bg-green-500/10 px-3 py-1.5 text-sm font-semibold text-green-700 dark:text-green-300">
            ✅ To'g'ri javob: <span className="font-extrabold">{word.word}</span>
          </p>
        )}
      </div>

      {/* Hint */}
      {!checked && input.length === 0 && (
        <p className="mb-3 text-xs font-medium stu-muted">
          💡 Birinchi harf: <span className="font-extrabold stu-body">{word.word[0].toUpperCase()}</span>
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
          <div className="flex items-center gap-4 w-full justify-between bg-surface-200/50 rounded-xl px-4 py-3">
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
      <h3 className="text-2xl font-extrabold stu-title mb-2">Tabriklaymiz!</h3>
      <p className="mb-6 stu-muted">Barcha so'zlarni 4 bosqichda o'zlashtirdingiz!</p>
      <div className="flex items-center justify-center gap-2 flex-wrap">
        {['🏆','⭐','🔥','💪','✨'].map((e,i) => (
          <span key={i} className="text-3xl animate-bounce" style={{ animationDelay: `${i*0.1}s` }}>{e}</span>
        ))}
      </div>
      <button onClick={onRestart}
        className="mx-auto mt-6 flex items-center gap-2 rounded-xl border-2 border-border px-6 py-2.5 text-sm font-semibold stu-body transition hover:bg-surface-200/50">
        <RotateCcw size={15} /> Qayta o'rganish
      </button>
    </div>
  );
}
