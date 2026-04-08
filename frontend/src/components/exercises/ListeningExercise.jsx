import { useState, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2 } from 'lucide-react';

/**
 * Listening exercise
 *
 * exercise.audio_url  — audio manzili (YouTube embed yoki to'g'ridan mp3 URL)
 * exercise.content    — { questions: [{ question, options, correct }] }
 */
export default function ListeningExercise({ exercise, onComplete }) {
  const { audio_url, content } = exercise;
  const questions = content?.questions || content?.items?.map((item) => ({
    question: item.question || item.sentence || '',
    options: item.options || [],
    correct: item.correct_index ?? item.correct ?? 0,
  })) || [];

  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  /* ── audio controls (only for direct file URLs) ── */
  const isDirectAudio = audio_url && !audio_url.includes('youtube') && !audio_url.includes('youtu.be');

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  const restart = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = 0;
    audioRef.current.play();
    setPlaying(true);
  };

  const handleAudioEnded = () => setPlaying(false);

  /* ── answers ── */
  const choose = (qi, idx) => {
    if (submitted) return;
    setAnswers((a) => ({ ...a, [qi]: idx }));
  };

  const handleSubmit = () => {
    if (questions.length === 0) return;
    if (Object.keys(answers).length < questions.length) return;
    setSubmitted(true);
    const correct = questions.filter((q, i) => answers[i] === q.correct).length;
    onComplete?.(correct, questions.length);
  };

  const reset = () => {
    setAnswers({});
    setSubmitted(false);
  };

  /* ── YouTube embed URL ── */
  const getYTEmbed = (url) => {
    if (!url) return null;
    const m = url.match(/(?:youtu\.be\/|v=|embed\/)([A-Za-z0-9_-]{11})/);
    return m ? `https://www.youtube.com/embed/${m[1]}` : null;
  };
  const ytEmbed = !isDirectAudio ? getYTEmbed(audio_url) : null;

  return (
    <div className="space-y-4">
      {/* ── Audio player ── */}
      {audio_url && (
        <div className="rounded-xl overflow-hidden bg-gradient-to-r from-teal-50 to-cyan-50 border border-teal-200 p-4">
          <div className="flex items-center gap-2 mb-3 text-teal-700">
            <Volume2 size={16} />
            <span className="text-sm font-semibold">Audio tinglang</span>
          </div>

          {isDirectAudio ? (
            /* Native audio player */
            <div className="flex items-center gap-3">
              <button
                onClick={togglePlay}
                className="w-10 h-10 rounded-full bg-teal-600 hover:bg-teal-700 text-white flex items-center justify-center transition shrink-0"
              >
                {playing ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
              </button>
              <button
                onClick={restart}
                className="w-8 h-8 rounded-full bg-white border border-teal-200 text-teal-600 hover:bg-teal-50 flex items-center justify-center transition shrink-0"
                title="Qayta boshlash"
              >
                <RotateCcw size={13} />
              </button>
              <div className="flex-1">
                <audio
                  ref={audioRef}
                  src={audio_url}
                  onEnded={handleAudioEnded}
                  className="w-full h-8"
                  controls
                  style={{ display: 'none' }}
                />
                <p className="text-xs text-teal-600 truncate">{audio_url.split('/').pop()}</p>
              </div>
            </div>
          ) : ytEmbed ? (
            /* YouTube embed */
            <div className="rounded-lg overflow-hidden aspect-video">
              <iframe
                src={ytEmbed}
                title="Listening audio"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full"
              />
            </div>
          ) : (
            /* Fallback: clickable link */
            <a
              href={audio_url}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-teal-600 underline hover:text-teal-800"
            >
              Audio ochish
            </a>
          )}
        </div>
      )}

      {/* ── Questions ── */}
      {questions.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Savollar</p>
          {questions.map((q, qi) => (
            <div key={qi} className="border border-gray-200 rounded-xl p-4 bg-white">
              <p className="text-sm font-medium text-gray-800 mb-3">
                <span className="text-gray-400 mr-1">{qi + 1}.</span>
                {q.question}
              </p>
              <div className="space-y-1.5">
                {q.options.map((opt, oi) => {
                  const chosen = answers[qi] === oi;
                  let cls = 'border-gray-200 bg-white text-gray-700 hover:border-teal-300 hover:bg-teal-50';
                  if (submitted) {
                    if (oi === q.correct) cls = 'border-green-400 bg-green-50 text-green-800 font-semibold';
                    else if (chosen) cls = 'border-red-300 bg-red-50 text-red-700 line-through';
                    else cls = 'border-gray-100 bg-gray-50 text-gray-400';
                  } else if (chosen) {
                    cls = 'border-teal-500 bg-teal-50 text-teal-800';
                  }
                  return (
                    <button
                      key={oi}
                      onClick={() => choose(qi, oi)}
                      disabled={submitted}
                      className={`w-full text-left px-3 py-2 rounded-lg border text-sm transition ${cls} disabled:cursor-default`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          {!submitted ? (
            <button
              onClick={handleSubmit}
              disabled={Object.keys(answers).length < questions.length}
              className="w-full py-2.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white font-semibold rounded-xl transition text-sm"
            >
              Tekshirish
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <div className={`flex-1 text-center py-2 rounded-xl text-sm font-semibold ${
                questions.filter((q, i) => answers[i] === q.correct).length === questions.length
                  ? 'bg-green-100 text-green-700'
                  : 'bg-orange-100 text-orange-700'
              }`}>
                {questions.filter((q, i) => answers[i] === q.correct).length} / {questions.length} to'g'ri
              </div>
              <button
                onClick={reset}
                className="px-4 py-2 border border-gray-200 text-gray-600 rounded-xl text-sm hover:bg-gray-50 transition flex items-center gap-1.5"
              >
                <RotateCcw size={13} /> Qayta
              </button>
            </div>
          )}
        </div>
      )}

      {!audio_url && questions.length === 0 && (
        <p className="text-sm text-gray-400 text-center py-4">Kontent hali qo'shilmagan</p>
      )}
    </div>
  );
}
