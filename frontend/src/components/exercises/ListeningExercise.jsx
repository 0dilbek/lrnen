import { useState, useRef, useMemo } from 'react';
import { Play, Pause, RotateCcw, Volume2, Maximize2, X, ZoomIn, ZoomOut } from 'lucide-react';
import ExampleBadge from './ExampleBadge';
import FillBlankExercise from './FillBlankExercise';
import MatchingExercise from './MatchingExercise';
import BookPageViewer from './BookPageViewer';
import { ProtectedMedia } from '../../context/MediaProtectionContext';

/**
 * Listening exercise
 *
 * exercise.audio_url  — audio manzili (YouTube embed yoki to'g'ridan mp3 URL)
 * exercise.content    — { questions } | { sentences } | { left, right, pairs }
 */
export default function ListeningExercise({ exercise, onComplete }) {
  const { audio_url, content } = exercise;
  const questions = useMemo(() => content?.questions || content?.items?.map((item) => ({
    question: item.question || item.sentence || '',
    options: item.options || [],
    correct: item.correct_index ?? item.correct ?? 0,
  })) || [], [content]);
  const rowAudioUrls = Array.isArray(content?.audio_urls) ? content.audio_urls : [];
  const hasRowAudio = rowAudioUrls.some(Boolean);
  const hasSentenceContent = Array.isArray(content?.sentences) && content.sentences.length > 0 && questions.length === 0;
  const hasMatchingContent = Array.isArray(content?.left) && Array.isArray(content?.right) && questions.length === 0;

  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const exampleCount = Number.isInteger(content?.example_count)
    ? content.example_count
    : (questions.length >= 2 ? 1 : 0);
  const hasExample = exampleCount > 0;
  const exampleAnswers = useMemo(
    () => (hasExample ? { 0: questions[0].correct } : {}),
    [hasExample, questions]
  );
  const [answers, setAnswers] = useState(() => ({ ...exampleAnswers }));
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
    if (submitted || qi < exampleCount) return;
    setAnswers((a) => ({ ...a, [qi]: idx }));
  };

  const scorable = questions.slice(exampleCount);

  const handleSubmit = () => {
    if (scorable.length === 0) return;
    const allDone = scorable.every((_, i) => answers[i + exampleCount] !== undefined);
    if (!allDone) return;
    setSubmitted(true);
    const correct = scorable.filter((q, i) => answers[i + exampleCount] === q.correct).length;
    onComplete?.(correct, scorable.length, {
      answers: Object.fromEntries(scorable.map((_, i) => [String(i), answers[i + exampleCount]])),
    });
  };

  const reset = () => {
    setAnswers({ ...exampleAnswers });
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
      {Array.isArray(content?.pages) && content.pages.length > 0 && (
        <BookPageViewer pages={content.pages} title="Listening sahifalari" />
      )}
      {/* ── Topshiriq rasmlari ── */}
      {content?.image_url && (
        <ProtectedMedia className="group flex max-h-96 cursor-zoom-in justify-center rounded-xl border border-border bg-surface-200/50 shadow-sm" onClick={() => setModalImage(content.image_url)}>
          <img src={content.image_url} alt="Listening task" draggable="false" className="max-w-full max-h-96 object-contain transition group-hover:opacity-90" />
          <div className="absolute top-4 right-4 p-2 bg-white/80 backdrop-blur-md rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
            <Maximize2 size={18} className="text-gray-700" />
          </div>
        </ProtectedMedia>
      )}
      {content?.images?.map((img, idx) => (
        <ProtectedMedia key={idx} className="group flex max-h-96 cursor-zoom-in justify-center rounded-xl border border-border bg-surface-200/50 shadow-sm" onClick={() => setModalImage(img)}>
          <img src={img} alt={`Listening task ${idx + 1}`} draggable="false" className="max-w-full max-h-96 object-contain transition group-hover:opacity-90" />
          <div className="absolute top-4 right-4 p-2 bg-white/80 backdrop-blur-md rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
            <Maximize2 size={18} className="text-gray-700" />
          </div>
        </ProtectedMedia>
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
          <ProtectedMedia
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
          </ProtectedMedia>
        </div>
      )}

      {/* ── Audio player ── */}
      {audio_url && !hasRowAudio && (
        <div className="overflow-hidden rounded-xl border border-teal-500/25 bg-gradient-to-r from-teal-500/10 to-cyan-500/10 p-4">
          <div className="mb-3 flex items-center gap-2 text-teal-700 dark:text-teal-300">
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
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-teal-500/25 bg-surface-100 text-teal-600 transition hover:bg-teal-500/10 dark:text-teal-300"
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
                  controlsList="nodownload noremoteplayback"
                  preload="metadata"
                  disableRemotePlayback
                  style={{ display: 'none' }}
                />
                <p className="truncate text-xs text-teal-700 dark:text-teal-300">{audio_url.split('/').pop()}</p>
              </div>
            </div>
          ) : ytEmbed ? (
            /* YouTube embed */
            <div className="rounded-lg overflow-hidden aspect-video">
              <iframe
                src={ytEmbed}
                title="Listening audio"
                allow="autoplay; encrypted-media"
                referrerPolicy="strict-origin-when-cross-origin"
                className="w-full h-full"
              />
            </div>
          ) : (
            <p className="text-sm text-amber-600">Audio brauzerda ijro qilinmadi.</p>
          )}
        </div>
      )}

      {hasRowAudio && questions.length === 0 && (
        <div className="rounded-xl border border-teal-500/25 bg-teal-500/5 p-4">
          <div className="mb-3 flex items-center gap-2 text-teal-700 dark:text-teal-300">
            <Volume2 size={16} />
            <span className="text-sm font-semibold">Audio parchalar</span>
          </div>
          <div className="space-y-2">
            {rowAudioUrls.map((url, index) => url && (
              <div key={`${url}-${index}`} className="flex items-center gap-3 rounded-lg border border-border bg-surface-100 px-3 py-2">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-teal-500/15 text-[10px] font-black text-teal-700 dark:text-teal-300">{index + 1}</span>
                <audio src={url} controls controlsList="nodownload noremoteplayback" preload="metadata" disableRemotePlayback className="h-9 w-full" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* sentences → fill blank (namuna 1-savolda) */}
      {hasSentenceContent && (
        <FillBlankExercise
          exercise={{ ...exercise, content: { sentences: content.sentences, word_panel: content.word_panel } }}
          onComplete={onComplete}
        />
      )}

      {/* matching content */}
      {hasMatchingContent && (
        <MatchingExercise exercise={exercise} onComplete={onComplete} />
      )}

      {/* ── Questions ── */}
      {questions.length > 0 && (
        <div className="space-y-3">
          {hasExample && (
            <p className="text-xs stu-muted italic">
              1-savol namuna — shunday yechiladi. Siz 2-savoldan boshlang.
            </p>
          )}
          <p className="text-xs font-semibold stu-muted uppercase tracking-wide">Savollar</p>
          {questions.map((q, qi) => {
            const isExample = qi < exampleCount;
            return (
              <div
                key={qi}
                className={`border rounded-xl p-4 ${
                  isExample ? 'border-amber-500/30 bg-amber-500/5' : 'border-border bg-surface-100'
                }`}
              >
                <p className="text-sm font-medium stu-title mb-3 flex items-center gap-2 flex-wrap">
                  <span className="stu-muted mr-1">{qi + 1}.</span>
                  {isExample && <ExampleBadge />}
                  {q.question}
                </p>
                {rowAudioUrls[qi] && (
                  <audio
                    src={rowAudioUrls[qi]}
                    controls
                    controlsList="nodownload noremoteplayback"
                    preload="metadata"
                    disableRemotePlayback
                    className="mb-3 h-9 w-full"
                    onContextMenu={(event) => event.preventDefault()}
                  />
                )}
                <div className="space-y-1.5">
                  {q.options.map((opt, oi) => {
                    const chosen = answers[qi] === oi;
                    let cls = 'border-border bg-surface-50 stu-body hover:border-teal-400 hover:bg-teal-500/10';
                    if (submitted || isExample) {
                      if (oi === q.correct) cls = 'border-green-500 bg-green-500/10 text-green-700 dark:text-green-300 font-semibold';
                      else if (chosen && !isExample) cls = 'border-red-500 bg-red-500/10 text-red-700 dark:text-red-300 line-through';
                      else cls = 'border-border bg-surface-200 stu-muted';
                    } else if (chosen) {
                      cls = 'border-teal-500 bg-teal-500/10 text-teal-700 dark:text-teal-300';
                    }
                    return (
                      <button
                        key={oi}
                        onClick={() => choose(qi, oi)}
                        disabled={submitted || isExample}
                        className={`w-full text-left px-3 py-2 rounded-lg border text-sm transition ${cls} disabled:cursor-default`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {!submitted ? (
            <button
              onClick={handleSubmit}
              disabled={scorable.some((_, i) => answers[i + exampleCount] === undefined)}
              className="w-full py-2.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white font-semibold rounded-xl transition text-sm"
            >
              Tekshirish
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <div className={`flex-1 text-center py-2 rounded-xl text-sm font-semibold ${
                scorable.filter((q, i) => answers[i + exampleCount] === q.correct).length === scorable.length
                  ? 'bg-green-500/10 text-green-700 dark:text-green-300'
                  : 'bg-orange-500/10 text-orange-700 dark:text-orange-300'
              }`}>
                {scorable.filter((q, i) => answers[i + exampleCount] === q.correct).length} / {scorable.length} to'g'ri
              </div>
              <button
                onClick={reset}
                className="px-4 py-2 border border-border stu-muted rounded-xl text-sm hover:bg-surface-200 transition flex items-center gap-1.5"
              >
                <RotateCcw size={13} /> Qayta
              </button>
            </div>
          )}
        </div>
      )}

      {!audio_url && questions.length === 0 && !hasSentenceContent && !hasMatchingContent && (
        <p className="text-sm stu-muted text-center py-4">Kontent hali qo'shilmagan</p>
      )}
    </div>
  );
}
