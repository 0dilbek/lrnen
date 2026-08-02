import { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { ArrowLeft, Send, Trash2, Loader2, CheckCircle, XCircle, ArrowRight, Home } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import ExerciseBlock from '../components/exercises/ExerciseBlock';
import VocabStudy from '../components/vocab/VocabStudy';
import ExampleBadge from '../components/exercises/ExampleBadge';
import { formatLessonTitle, formatLessonDescription } from '../utils/lessonDisplay';

function getYoutubeId(url) {
  const match = url?.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([^&?/\s]{11})/);
  return match ? match[1] : null;
}

function Confetti() {
  const colors = ['#6366f1','#06b6d4','#10b981','#f59e0b','#ec4899','#f97316'];
  const pseudoRandom = (seed) => ((seed * 9301 + 49297) % 233280) / 233280;
  const pieces = Array.from({ length: 48 }, (_, i) => ({
    id: i,
    color: colors[i % colors.length],
    left: `${pseudoRandom(i + 1) * 100}%`,
    delay: `${pseudoRandom(i + 51) * 1.5}s`,
    duration: `${1.8 + pseudoRandom(i + 101) * 1.2}s`,
    size: `${8 + pseudoRandom(i + 151) * 8}px`,
    rotate: `${pseudoRandom(i + 201) * 360}deg`,
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

function SectionTitle({ emoji, title, sub }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div className="w-10 h-10 rounded-xl bg-surface-200 border border-border flex items-center justify-center text-2xl shrink-0">
        {emoji}
      </div>
      <div>
        <h2 className="student-section-title">{title}</h2>
        {sub && <p className="student-section-sub">{sub}</p>}
      </div>
    </div>
  );
}

function QuizResultBanner({ result, onNext, onDashboard }) {
  const great = result.score >= 80;
  const ok    = result.score >= 60 || result.completed;
  const completed = result.completed ?? ok;
  return (
    <div className={`relative overflow-hidden mb-6 p-5 rounded-2xl border-2 text-center ${
      great ? 'bg-emerald-500/10 border-emerald-500/40' :
      ok    ? 'bg-amber-500/10 border-amber-500/40' :
              'bg-red-500/10 border-red-500/30'
    }`}>
      {great && <Confetti />}
      <div className="text-5xl mb-2">{great ? '🏆' : ok ? '⭐' : '💪'}</div>
      <p className="text-3xl font-extrabold stu-title">{result.score}%</p>
      <p className="text-base font-semibold stu-body mt-1">
        {result.correct}/{result.total} ta to'g'ri
      </p>
      <p className={`text-sm mt-2 font-medium ${great ? 'text-emerald-500' : ok ? 'text-amber-500' : 'text-red-500'}`}>
        {great ? '🎉 Ajoyib! Dars muvaffaqiyatli yakunlandi!' :
         ok    ? '👍 Yaxshi natija! Dars yakunlandi.' :
                 '😅 Qayta urinib ko\'ring — siz uddalaysiz!'}
      </p>
      {completed && (
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-5">
          {result.next_lesson_id ? (
            <button
              onClick={onNext}
              className="admin-btn-primary px-6 py-3"
            >
              Keyingi dars
              <ArrowRight size={16} />
            </button>
          ) : (
            <p className="text-sm text-emerald-500 font-semibold">Barcha darslar yakunlandi! 🎓</p>
          )}
          <button
            onClick={onDashboard}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-border stu-muted hover:stu-body text-sm font-semibold transition"
          >
            <Home size={16} />
            Bosh sahifa
          </button>
        </div>
      )}
    </div>
  );
}

export default function LessonPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refreshProgress } = useGame() || {};

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
  const [answerAnim, setAnswerAnim] = useState({});
  const quizRef = useRef(null);

  // Dars o'zgarganda holatni tozalash
  useEffect(() => {
    setQuizResult(null);
    setSubmitted(false);
    setAnswers({});
    setAnswerAnim({});
    setLoading(true);
  }, [id]);

  useEffect(() => {
    Promise.all([
      api.get(`/courses/lessons/${id}/`),
      api.get(`/courses/vocabulary/?lesson=${id}`),
      api.get(`/quiz/?lesson=${id}`),
      api.get(`/quiz/exercises/?lesson=${id}`),
      api.get(`/comments/?lesson=${id}`),
    ]).then(([l, v, q, ex, c]) => {
      if (l.data.is_locked) {
        navigate('/dashboard', { replace: true });
        return;
      }
      setLesson(l.data);
      setVocab(v.data);
      const quizList = q.data || [];
      setQuizzes(quizList);
      setExercises(ex.data);
      setComments(c.data);

      // Namuna savolni oldindan to'ldirish
      const initial = {};
      quizList.forEach((quiz) => {
        if (quiz.is_example && quiz.correct_option_index != null) {
          initial[quiz.id] = quiz.correct_option_index;
        }
      });
      setAnswers(initial);

      api.post('/courses/progress/', { lesson: Number(id), status: 'in-progress' }).catch(() => {});
    }).catch(() => {
      navigate('/dashboard', { replace: true });
    }).finally(() => setLoading(false));
  }, [id, navigate]);

  const scorableQuizzes = useMemo(
    () => quizzes.filter((q) => !q.is_example),
    [quizzes]
  );

  const allScorableAnswered = scorableQuizzes.every((q) => answers[q.id] !== undefined);

  const handleAnswer = (quizId, idx) => {
    if (submitted) return;
    const quiz = quizzes.find((q) => q.id === quizId);
    if (quiz?.is_example) return;
    setAnswers((prev) => ({ ...prev, [quizId]: idx }));
  };

  const handleSubmitQuiz = async () => {
    if (!allScorableAnswered) {
      quizRef.current?.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    setSubmitting(true);
    const payload = {
      lesson_id: Number(id),
      answers: quizzes.map((q) => ({
        quiz_id: q.id,
        selected_index: q.is_example
          ? (q.correct_option_index ?? answers[q.id])
          : answers[q.id],
      })),
    };
    try {
      const { data } = await api.post('/quiz/submit/', payload);
      const anim = {};
      data.results?.forEach((r) => {
        anim[r.quiz_id] = r.is_correct ? 'correct' : 'wrong';
      });
      setAnswerAnim(anim);
      setQuizResult(data);
      setSubmitted(true);
      if (data.completed) {
        refreshProgress?.();
      }
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
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }
  if (!lesson) return <div className="text-center py-20 text-slate-500">Dars topilmadi</div>;

  const ytId = getYoutubeId(lesson.video_url);
  const displayTitle = formatLessonTitle(lesson.title);
  const displayDesc = formatLessonDescription(lesson.description);
  const readingExercises = exercises.filter((exercise) => exercise.type === 'reading');
  const practiceExercises = exercises.filter((exercise) => exercise.type !== 'reading');

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">

      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-2 text-slate-500 hover:text-indigo-400 transition mb-6 font-medium"
      >
        <ArrowLeft size={18} /> Orqaga
      </button>

      <div className="mb-6">
        <h1 className="text-3xl font-extrabold stu-title leading-tight">{displayTitle}</h1>
      </div>

      <section className="mb-8">
        <SectionTitle emoji="🎬" title="Video dars" />
        <div className="rounded-2xl overflow-hidden shadow-xl aspect-video bg-black border border-border">
          {ytId ? (
            <iframe
              className="w-full h-full"
              src={`https://www.youtube.com/embed/${ytId}`}
              title={displayTitle}
              allowFullScreen
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            />
          ) : (
            <video className="w-full h-full" src={lesson.video_url} controls />
          )}
        </div>
      </section>

      {displayDesc && (
        <section className="mb-8">
          <SectionTitle emoji="📖" title="Dars haqida" />
          <div className="student-panel">
            <p className="text-slate-300 leading-relaxed text-base">{displayDesc}</p>
          </div>
        </section>
      )}

      {vocab.length > 0 && (
        <section className="mb-8">
          <SectionTitle emoji="💬" title="Yangi so'zlar" sub={`${vocab.length} ta so'z — 4 bosqichda o'rganing`} />
          <div className="student-panel">
            <VocabStudy words={vocab} />
          </div>
        </section>
      )}

      {readingExercises.length > 0 && (
        <section className="mb-8">
          <SectionTitle emoji="📚" title="Reading" sub={`${readingExercises.length} ta matn — avval sahifani o'qing, keyin topshiriqni bajaring`} />
          <div className="space-y-4">
            {readingExercises.map((exercise, index) => (
              <ExerciseBlock key={exercise.id} exercise={exercise} index={index} />
            ))}
          </div>
        </section>
      )}

      {practiceExercises.length > 0 && (
        <section className="mb-8">
          <SectionTitle emoji="✏️" title="Mashqlar" sub={`${practiceExercises.length} ta mashq`} />
          <div className="space-y-3">
            {practiceExercises.map((ex, i) => (
              <ExerciseBlock key={ex.id} exercise={ex} index={i} />
            ))}
          </div>
        </section>
      )}

      {quizzes.length > 0 && (
        <section className="mb-8" ref={quizRef}>
          <SectionTitle emoji="📝" title="Test" sub={`${quizzes.length} ta savol`} />

          {quizResult && (
            <QuizResultBanner
              result={quizResult}
              onNext={() => navigate(`/lessons/${quizResult.next_lesson_id}`)}
              onDashboard={() => navigate('/dashboard')}
            />
          )}

          {quizzes.some((q) => q.is_example) && !submitted && (
            <p className="text-xs stu-muted mb-4 italic">
              1-savol namuna — shunday yechiladi. Siz 2-savoldan boshlang.
            </p>
          )}

          <div className="space-y-4">
            {quizzes.map((quiz, qi) => {
              const result = quizResult?.results?.find((r) => r.quiz_id === quiz.id);
              const anim = answerAnim[quiz.id];
              const isExample = quiz.is_example;
              return (
                <div
                  key={quiz.id}
                  className={`student-card p-5 border-2 transition-all duration-300 ${
                    isExample ? 'border-amber-500/30 bg-amber-500/5' :
                    anim === 'correct' ? 'border-emerald-500/50' :
                    anim === 'wrong'   ? 'border-red-500/40' :
                                        'border-border'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-4">
                    <span className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold text-white ${
                      isExample || anim === 'correct' ? 'bg-emerald-500' :
                      anim === 'wrong'   ? 'bg-red-500' :
                                          'bg-surface-300'
                    }`}>
                      {qi + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        {isExample && <ExampleBadge />}
                      </div>
                      <p className="font-semibold stu-title text-base leading-snug">{quiz.question}</p>
                    </div>
                  </div>

                  <div className="space-y-2 pl-10">
                    {quiz.options.map((opt, idx) => {
                      const isSelected = answers[quiz.id] === idx;
                      const exampleCorrect = isExample && idx === quiz.correct_option_index;
                      const isCorrect  = (result && idx === result.correct_option_index) || exampleCorrect;
                      const isWrong    = result && isSelected && !result.is_correct && !isExample;

                      let cls = 'student-quiz-option';
                      if (!submitted && isSelected && !isExample) cls += ' selected';
                      if ((submitted || isExample) && isCorrect) cls += ' correct';
                      if (submitted && isWrong) cls += ' wrong';

                      return (
                        <button
                          key={idx}
                          onClick={() => handleAnswer(quiz.id, idx)}
                          disabled={submitted || isExample}
                          className={cls}
                        >
                          {(submitted || isExample) && isCorrect && <CheckCircle size={16} className="text-emerald-500 shrink-0" />}
                          {submitted && isWrong   && <XCircle    size={16} className="text-red-400 shrink-0" />}
                          <span>{String.fromCharCode(65 + idx)}. {opt}</span>
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
              disabled={submitting || !allScorableAnswered}
              className="mt-6 w-full sm:w-auto admin-btn-primary px-8 py-3.5 disabled:opacity-50"
            >
              {submitting
                ? <><Loader2 className="animate-spin" size={18} /> Tekshirilmoqda...</>
                : <>📨 Testni yakunlash ({scorableQuizzes.filter((q) => answers[q.id] !== undefined).length}/{scorableQuizzes.length})</>
              }
            </button>
          )}
        </section>
      )}

      <section>
        <SectionTitle emoji="💭" title="Izohlar" sub={`${comments.length} ta izoh`} />

        <form onSubmit={handleComment} className="flex gap-3 mb-6">
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Savol yoki izoh yozing..."
            className="student-input"
          />
          <button
            type="submit"
            disabled={!comment.trim()}
            className="admin-btn-primary disabled:opacity-40"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Yuborish</span>
          </button>
        </form>

        {comments.length === 0 ? (
          <div className="text-center py-10 student-panel border-dashed">
            <div className="text-4xl mb-2">💬</div>
            <p className="text-slate-500 text-sm">Hali izoh yo'q — birinchi bo'ling!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {comments.map((c) => (
              <div key={c.id} className="student-card p-4 flex gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-400 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {(c.user_name || c.user_username || '?')[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-200">
                      {c.user_name || `@${c.user_username}`}
                    </p>
                    <div className="flex items-center gap-2 shrink-0">
                      <p className="text-xs text-slate-500">{new Date(c.created_at).toLocaleString('uz-UZ')}</p>
                      {(user?.role === 'admin' || user?.id === c.user) && (
                        <button onClick={() => deleteComment(c.id)} className="text-slate-600 hover:text-red-400 transition">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                  <p className="text-slate-400 mt-1 text-sm leading-relaxed">{c.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
