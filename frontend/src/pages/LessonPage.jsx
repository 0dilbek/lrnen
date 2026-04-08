import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { ArrowLeft, Send, Trash2, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ExerciseBlock from '../components/exercises/ExerciseBlock';
import VocabStudy from '../components/vocab/VocabStudy';

function getYoutubeId(url) {
  const match = url?.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([^&?/\s]{11})/);
  return match ? match[1] : null;
}

/* ── Confetti ──────────────────────────────────────────────────────── */
function Confetti() {
  const colors = ['#6366f1','#06b6d4','#10b981','#f59e0b','#ec4899','#f97316'];
  const pieces = Array.from({ length: 48 }, (_, i) => ({
    id: i,
    color: colors[i % colors.length],
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 1.5}s`,
    duration: `${1.8 + Math.random() * 1.2}s`,
    size: `${8 + Math.random() * 8}px`,
    rotate: `${Math.random() * 360}deg`,
  }));
  return (
    <>
      <style>{`
        @keyframes confettiFall {
          0%   { transform: translateY(-20px) rotate(0deg); opacity: 1; }
          100% { transform: translateY(320px) rotate(720deg); opacity: 0; }
        }
      `}</style>
      <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl">
        {pieces.map((p) => (
          <div key={p.id} style={{
            position:'absolute', left: p.left, top:'-10px',
            width: p.size, height: p.size,
            backgroundColor: p.color, borderRadius:'2px',
            animation: `confettiFall ${p.duration} ${p.delay} ease-in forwards`,
            transform: `rotate(${p.rotate})`,
          }} />
        ))}
      </div>
    </>
  );
}

/* ── Section sarlavhasi ─────────────────────────────────────────────── */
function SectionTitle({ emoji, title, sub }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-2xl shrink-0">
        {emoji}
      </div>
      <div>
        <h2 className="text-lg font-extrabold text-gray-900">{title}</h2>
        {sub && <p className="text-sm text-gray-400">{sub}</p>}
      </div>
    </div>
  );
}

/* ── Quiz natija baneri ─────────────────────────────────────────────── */
function QuizResultBanner({ result }) {
  const great = result.score >= 80;
  const ok    = result.score >= 60;
  return (
    <div className={`relative overflow-hidden mb-6 p-5 rounded-2xl border-2 text-center ${
      great ? 'bg-green-50 border-green-300' :
      ok    ? 'bg-yellow-50 border-yellow-300' :
              'bg-red-50 border-red-200'
    }`}>
      {great && <Confetti />}
      <div className="text-5xl mb-2">{great ? '🏆' : ok ? '⭐' : '💪'}</div>
      <p className="text-3xl font-extrabold text-gray-900">{result.score}%</p>
      <p className="text-base font-semibold text-gray-700 mt-1">
        {result.correct}/{result.total} ta to'g'ri
      </p>
      <p className={`text-sm mt-2 font-medium ${great ? 'text-green-700' : ok ? 'text-yellow-700' : 'text-red-600'}`}>
        {great ? '🎉 Ajoyib! Dars muvaffaqiyatli yakunlandi!' :
         ok    ? '👍 Yaxshi natija! Dars yakunlandi.' :
                 '😅 Qayta urinib ko\'ring — siz uddalaysiz!'}
      </p>
    </div>
  );
}

export default function LessonPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [lesson, setLesson]       = useState(null);
  const [vocab, setVocab]         = useState([]);
  const [quizzes, setQuizzes]     = useState([]);
  const [exercises, setExercises] = useState([]);
  const [comments, setComments]   = useState([]);
  const [answers, setAnswers]     = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [comment, setComment]     = useState('');
  const [loading, setLoading]     = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [answerAnim, setAnswerAnim] = useState({});  // quizId → 'correct'|'wrong'
  const quizRef = useRef(null);

  useEffect(() => {
    Promise.all([
      api.get(`/courses/lessons/${id}/`),
      api.get(`/courses/vocabulary/?lesson=${id}`),
      api.get(`/quiz/?lesson=${id}`),
      api.get(`/quiz/exercises/?lesson=${id}`),
      api.get(`/comments/?lesson=${id}`),
    ]).then(([l, v, q, ex, c]) => {
      setLesson(l.data);
      setVocab(v.data);
      setQuizzes(q.data);
      setExercises(ex.data);
      setComments(c.data);
      api.post('/courses/progress/', { lesson: Number(id), status: 'in-progress' }).catch(() => {});
    }).finally(() => setLoading(false));
  }, [id]);

  const handleAnswer = (quizId, idx) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [quizId]: idx }));
  };

  const handleSubmitQuiz = async () => {
    if (Object.keys(answers).length !== quizzes.length) {
      quizRef.current?.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    setSubmitting(true);
    const payload = {
      lesson_id: Number(id),
      answers: quizzes.map((q) => ({ quiz_id: q.id, selected_index: answers[q.id] })),
    };
    try {
      const { data } = await api.post('/quiz/submit/', payload);
      // Animate each answer
      const anim = {};
      data.results?.forEach((r) => {
        anim[r.quiz_id] = r.is_correct ? 'correct' : 'wrong';
      });
      setAnswerAnim(anim);
      setQuizResult(data);
      setSubmitted(true);
    } finally {
      setSubmitting(false);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    const { data } = await api.post('/comments/', { lesson: Number(id), message: comment });
    setComments((prev) => [data, ...prev]);
    setComment('');
  };

  const deleteComment = async (cid) => {
    await api.delete(`/comments/${cid}/`);
    setComments((prev) => prev.filter((c) => c.id !== cid));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }
  if (!lesson) return <div className="text-center py-20 text-gray-400">Dars topilmadi</div>;

  const ytId = getYoutubeId(lesson.video_url);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">

      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition mb-6 font-medium"
      >
        <ArrowLeft size={18} /> Orqaga
      </button>

      {/* Title */}
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 leading-tight mb-3">{lesson.title}</h1>
        {lesson.category_name && (
          <span className="inline-block text-sm font-semibold bg-violet-100 text-violet-700 px-3 py-1 rounded-full">
            📂 {lesson.category_name}
          </span>
        )}
      </div>

      {/* ── Video ───────────────────────────────── */}
      <section className="mb-8">
        <SectionTitle emoji="🎬" title="Video dars" />
        <div className="rounded-2xl overflow-hidden shadow-xl aspect-video bg-black">
          {ytId ? (
            <iframe
              className="w-full h-full"
              src={`https://www.youtube.com/embed/${ytId}`}
              title={lesson.title}
              allowFullScreen
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            />
          ) : (
            <video className="w-full h-full" src={lesson.video_url} controls />
          )}
        </div>
      </section>

      {/* ── Description ─────────────────────────── */}
      {lesson.description && (
        <section className="mb-8">
          <SectionTitle emoji="📖" title="Dars haqida" />
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6">
            <p className="text-gray-700 leading-relaxed text-base">{lesson.description}</p>
          </div>
        </section>
      )}

      {/* ── Vocabulary ──────────────────────────── */}
      {vocab.length > 0 && (
        <section className="mb-8">
          <SectionTitle emoji="💬" title="Yangi so'zlar" sub={`${vocab.length} ta so'z — 4 bosqichda o'rganing`} />
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <VocabStudy words={vocab} />
          </div>
        </section>
      )}

      {/* ── Exercises ───────────────────────────── */}
      {exercises.length > 0 && (
        <section className="mb-8">
          <SectionTitle emoji="✏️" title="Mashqlar" sub={`${exercises.length} ta mashq`} />
          <div className="space-y-3">
            {exercises.map((ex, i) => (
              <ExerciseBlock key={ex.id} exercise={ex} index={i} />
            ))}
          </div>
        </section>
      )}

      {/* ── Quiz ────────────────────────────────── */}
      {quizzes.length > 0 && (
        <section className="mb-8" ref={quizRef}>
          <SectionTitle emoji="📝" title="Test" sub={`${quizzes.length} ta savol`} />

          {quizResult && <QuizResultBanner result={quizResult} />}

          <div className="space-y-4">
            {quizzes.map((quiz, qi) => {
              const result = quizResult?.results?.find((r) => r.quiz_id === quiz.id);
              const anim = answerAnim[quiz.id];
              return (
                <div
                  key={quiz.id}
                  className={`bg-white rounded-2xl border-2 shadow-sm p-5 transition-all duration-300 ${
                    anim === 'correct' ? 'border-green-400 bg-green-50/40' :
                    anim === 'wrong'   ? 'border-red-300 bg-red-50/30' :
                                        'border-gray-100'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-4">
                    <span className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold text-white ${
                      anim === 'correct' ? 'bg-green-500' :
                      anim === 'wrong'   ? 'bg-red-400' :
                                          'bg-gray-300'
                    }`}>
                      {qi + 1}
                    </span>
                    <p className="font-semibold text-gray-900 text-base leading-snug">{quiz.question}</p>
                  </div>

                  <div className="space-y-2 pl-10">
                    {quiz.options.map((opt, idx) => {
                      const isSelected = answers[quiz.id] === idx;
                      const isCorrect  = result && idx === result.correct_option_index;
                      const isWrong    = result && isSelected && !result.is_correct;

                      let cls = 'border-gray-200 text-gray-700 hover:border-blue-400 hover:bg-blue-50';
                      if (!submitted && isSelected) cls = 'border-blue-500 bg-blue-50 text-blue-800';
                      if (submitted && isCorrect)   cls = 'border-green-500 bg-green-50 text-green-800';
                      if (submitted && isWrong)     cls = 'border-red-400 bg-red-50 text-red-800';

                      return (
                        <button
                          key={idx}
                          onClick={() => handleAnswer(quiz.id, idx)}
                          disabled={submitted}
                          className={`w-full text-left px-4 py-3 rounded-xl border-2 transition-all duration-200 flex items-center gap-3 font-medium ${cls}`}
                        >
                          {submitted && isCorrect && <CheckCircle size={16} className="text-green-600 shrink-0" />}
                          {submitted && isWrong   && <XCircle    size={16} className="text-red-500 shrink-0" />}
                          <span className="text-sm">{String.fromCharCode(65 + idx)}. {opt}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {!submitted && (
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting || Object.keys(answers).length !== quizzes.length}
              className="mt-6 w-full sm:w-auto bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 disabled:opacity-50 text-white font-bold px-8 py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200"
            >
              {submitting
                ? <><Loader2 className="animate-spin" size={18} /> Tekshirilmoqda...</>
                : <>📨 Testni yakunlash ({Object.keys(answers).length}/{quizzes.length})</>
              }
            </button>
          )}
        </section>
      )}

      {/* ── Comments ────────────────────────────── */}
      <section>
        <SectionTitle emoji="💭" title="Izohlar" sub={`${comments.length} ta izoh`} />

        <form onSubmit={handleComment} className="flex gap-3 mb-6">
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Savol yoki izoh yozing..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white text-sm"
          />
          <button
            type="submit"
            disabled={!comment.trim()}
            className="bg-gradient-to-r from-blue-500 to-violet-600 disabled:opacity-40 text-white px-5 py-3 rounded-xl transition flex items-center gap-2 font-semibold"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Yuborish</span>
          </button>
        </form>

        {comments.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
            <div className="text-4xl mb-2">💬</div>
            <p className="text-gray-400 text-sm">Hali izoh yo'q — birinchi bo'ling!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {comments.map((c) => (
              <div key={c.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 flex gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-400 to-blue-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {(c.user_name || c.user_username || '?')[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-gray-800">
                      {c.user_name || `@${c.user_username}`}
                    </p>
                    <div className="flex items-center gap-2 shrink-0">
                      <p className="text-xs text-gray-400">{new Date(c.created_at).toLocaleString('uz-UZ')}</p>
                      {(user?.role === 'admin' || user?.id === c.user) && (
                        <button onClick={() => deleteComment(c.id)} className="text-gray-300 hover:text-red-500 transition">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                  <p className="text-gray-600 mt-1 text-sm leading-relaxed">{c.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
