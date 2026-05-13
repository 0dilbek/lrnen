import { useState, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2, Maximize2, X, ZoomIn, ZoomOut } from 'lucide-react';

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
  const [modalImage, setModalImage] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

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
      {/* ── Topshiriq rasmlari ── */}
      {content?.image_url && (
        <div className="relative group rounded-xl overflow-hidden border border-gray-200 shadow-sm max-h-96 flex justify-center bg-gray-50 cursor-zoom-in" onClick={() => setModalImage(content.image_url)}>
          <img src={content.image_url} alt="Listening task" className="max-w-full max-h-96 object-contain transition group-hover:opacity-90" />
          <div className="absolute top-4 right-4 p-2 bg-white/80 backdrop-blur-md rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
            <Maximize2 size={18} className="text-gray-700" />
          </div>
        </div>
      )}
      {content?.images?.map((img, idx) => (
        <div key={idx} className="relative group rounded-xl overflow-hidden border border-gray-200 shadow-sm max-h-96 flex justify-center bg-gray-50 cursor-zoom-in" onClick={() => setModalImage(img)}>
          <img src={img} alt={`Listening task ${idx + 1}`} className="max-w-full max-h-96 object-contain transition group-hover:opacity-90" />
          <div className="absolute top-4 right-4 p-2 bg-white/80 backdrop-blur-md rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
            <Maximize2 size={18} className="text-gray-700" />
          </div>
        </div>
      ))}

      {/* ── Image Modal (Professional Zoom & Pan) ── */}
      {modalImage && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-md animate-in fade-in duration-300 overflow-hidden select-none"
          onWheel={(e) => {
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            setZoom(prev => Math.min(5, Math.max(0.5, prev + delta)));
          }}
          onClick={() => { setModalImage(null); setZoom(1); setPosition({x:0, y:0}); }}
        >
          {/* Close Button */}
          <button 
            className="absolute top-6 right-6 p-4 bg-white/10 hover:bg-rose-500 text-white rounded-full transition-all z-50 shadow-2xl"
            onClick={(e) => { e.stopPropagation(); setModalImage(null); }}
          >
            <X size={28} />
          </button>

          {/* Controls Overlay */}
          <div 
            className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-6 px-6 py-3 bg-white/10 backdrop-blur-2xl rounded-3xl border border-white/20 z-50 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2">
              <button onClick={() => setZoom(z => Math.max(0.5, z - 0.25))} className="p-2 text-white hover:bg-white/20 rounded-xl transition"><ZoomOut size={22} /></button>
              <div className="w-16 text-center text-white font-black text-sm tracking-tighter">
                {Math.round(zoom * 100)}%
              </div>
              <button onClick={() => setZoom(z => Math.min(5, z + 0.25))} className="p-2 text-white hover:bg-white/20 rounded-xl transition"><ZoomIn size={22} /></button>
            </div>
            <div className="h-6 w-px bg-white/20" />
            <button 
              onClick={() => { setZoom(1); setPosition({x:0, y:0}); }} 
              className="px-4 py-1.5 text-[10px] text-white font-black bg-white/10 rounded-xl hover:bg-white/30 transition uppercase tracking-widest"
            >
              Reset
            </button>
          </div>

          {/* Image Container with Pan Logic */}
          <div 
            className="w-full h-full flex items-center justify-center cursor-grab active:cursor-grabbing"
            onMouseDown={(e) => {
              e.stopPropagation();
              setIsDragging(true);
              setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
            }}
            onMouseMove={(e) => {
              if (!isDragging) return;
              setPosition({
                x: e.clientX - dragStart.x,
                y: e.clientY - dragStart.y
              });
            }}
            onMouseUp={() => setIsDragging(false)}
            onMouseLeave={() => setIsDragging(false)}
          >
            <img 
              src={modalImage} 
              alt="Zoomed view" 
              draggable={false}
              className="max-w-none transition-transform duration-75 ease-out pointer-events-none"
              style={{ 
                transform: `translate(${position.x}px, ${position.y}px) scale(${zoom})`,
              }}
            />
          </div>
        </div>
      )}

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
