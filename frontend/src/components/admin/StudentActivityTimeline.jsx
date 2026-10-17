import {
  CheckCircle2,
  Clock3,
  FileQuestion,
  Headphones,
  Keyboard,
  Link2,
  Loader2,
  MessageCircle,
  XCircle,
} from 'lucide-react';

const TYPE_ICONS = {
  choose_correct: FileQuestion,
  fill_blank: Keyboard,
  matching: Link2,
  listening: Headphones,
  reading: FileQuestion,
  speaking: MessageCircle,
};

function formatDate(value) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('uz-UZ', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function scorableRows(rows) {
  return rows.length >= 2 ? rows.slice(1) : rows;
}

function feedbackRows(values, sourceRows) {
  if (!Array.isArray(values)) return [];
  return sourceRows.length >= 2 && values.length === sourceRows.length ? values.slice(1) : values;
}

function stringifyValue(value) {
  if (value === null || value === undefined || value === '') return 'Javob berilmagan';
  if (typeof value === 'string' || typeof value === 'number') return String(value);
  return JSON.stringify(value, null, 2);
}

function buildAnswerRows(attempt) {
  const content = attempt.content_snapshot || {};
  const answer = attempt.user_answer || {};
  const feedback = attempt.feedback || {};
  const type = attempt.exercise_type;

  if (type === 'choose_correct') {
    const source = content.sentences || content.items || [];
    const rows = scorableRows(source);
    const answers = Array.isArray(answer.answers) ? answer.answers : [];
    const correctValues = feedbackRows(feedback.correct_indices, source);
    return rows.map((row, index) => {
      const options = row.options || [];
      const selectedIndex = answers[index];
      const correctIndex = correctValues[index] ?? row.correct ?? row.correct_index;
      return {
        question: row.sentence || `${row.before || ''} ___ ${row.after || ''}`.trim(),
        selected: options[selectedIndex] ?? selectedIndex,
        correct: options[correctIndex] ?? correctIndex,
        isCorrect: selectedIndex === correctIndex,
      };
    });
  }

  if (type === 'fill_blank' || (type === 'reading' && (content.sentences || content.items))) {
    const source = content.sentences || content.items || [];
    const rows = scorableRows(source);
    const answers = Array.isArray(answer.answers) ? answer.answers : [];
    const correctValues = feedbackRows(feedback.correct_answers, source);
    return rows.map((row, index) => {
      const selected = answers[index];
      const correct = correctValues[index] ?? row.answer;
      return {
        question: row.text || row.sentence || `Savol ${index + 1}`,
        selected,
        correct,
        isCorrect: String(selected || '').trim().toLowerCase() === String(correct || '').trim().toLowerCase(),
      };
    });
  }

  if (type === 'listening' || type === 'reading') {
    const source = content.questions || content.items || [];
    const rows = scorableRows(source);
    const answers = answer.answers && typeof answer.answers === 'object' ? answer.answers : {};
    const correctValues = feedbackRows(feedback.correct_indices, source);
    return rows.map((row, index) => {
      const options = row.options || [];
      const selectedIndex = answers[String(index)];
      const correctIndex = correctValues[index] ?? row.correct ?? row.correct_index;
      return {
        question: row.question || row.sentence || `Savol ${index + 1}`,
        selected: options[selectedIndex] ?? selectedIndex,
        correct: options[correctIndex] ?? correctIndex,
        isCorrect: selectedIndex === correctIndex,
      };
    });
  }

  if (type === 'matching' && Array.isArray(content.left) && Array.isArray(content.right)) {
    const start = content.left.length >= 2 ? 1 : 0;
    const matches = answer.matches || {};
    const pairs = content.pairs || content.left.map((_, index) => index);
    return content.left.slice(start).map((left, offset) => {
      const index = offset + start;
      const selectedIndex = matches[String(index)];
      const correctIndex = pairs[index];
      return {
        question: left,
        selected: content.right[selectedIndex] ?? selectedIndex,
        correct: content.right[correctIndex] ?? correctIndex,
        isCorrect: Number(selectedIndex) === Number(correctIndex),
      };
    });
  }

  return [];
}

function AnswerRows({ rows, fallback }) {
  if (!rows.length) {
    return (
      <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-surface-200 p-3 text-xs admin-text-body">
        {stringifyValue(fallback)}
      </pre>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      {rows.map((row, index) => (
        <div key={`${row.question}-${index}`} className={`rounded-xl border p-3 ${row.isCorrect ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
          <div className="flex items-start gap-2">
            {row.isCorrect
              ? <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-500" />
              : <XCircle size={16} className="mt-0.5 shrink-0 text-red-500" />}
            <div className="min-w-0 text-xs">
              <p className="font-bold admin-text-title">{row.question || `Savol ${index + 1}`}</p>
              <p className="mt-1 admin-text-muted">O‘quvchi javobi: <span className="font-semibold admin-text-body">{stringifyValue(row.selected)}</span></p>
              {!row.isCorrect && <p className="mt-0.5 text-emerald-600 dark:text-emerald-300">To‘g‘ri javob: <strong>{stringifyValue(row.correct)}</strong></p>}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function StudentActivityTimeline({ quizAttempts = [], exerciseAttempts = [], loading = false }) {
  if (loading) {
    return <div className="grid min-h-48 place-items-center"><Loader2 className="animate-spin text-indigo-500" size={30} /></div>;
  }

  if (!quizAttempts.length && !exerciseAttempts.length) {
    return (
      <div className="rounded-2xl border border-dashed border-border px-5 py-12 text-center">
        <Clock3 className="mx-auto admin-text-muted opacity-50" size={34} />
        <p className="mt-3 font-bold admin-text-title">Urinishlar topilmadi</p>
        <p className="mt-1 text-sm admin-text-muted">Bu dars bo‘yicha topshiriq yoki test tarixi hali yo‘q.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {exerciseAttempts.length > 0 && (
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-extrabold admin-text-title">Dars mashqlari</h3>
            <span className="rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-bold text-indigo-600 dark:text-indigo-300">{exerciseAttempts.length} urinish</span>
          </div>
          <div className="space-y-3">
            {exerciseAttempts.map((attempt) => {
              const Icon = TYPE_ICONS[attempt.exercise_type] || FileQuestion;
              const answerRows = buildAnswerRows(attempt);
              return (
                <details key={`exercise-${attempt.id}`} className="group rounded-2xl border border-border bg-surface-100 p-4 open:shadow-card">
                  <summary className="flex cursor-pointer list-none items-center gap-3">
                    <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ${attempt.score >= 60 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                      <Icon size={19} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-bold admin-text-title">{attempt.instruction_snapshot || attempt.exercise_type_display}</span>
                      <span className="mt-0.5 block text-xs admin-text-muted">{attempt.exercise_type_display} · {formatDate(attempt.submitted_at)}</span>
                    </span>
                    <strong className={`${attempt.score >= 60 ? 'text-emerald-500' : 'text-red-500'}`}>{attempt.score}%</strong>
                  </summary>
                  <AnswerRows rows={answerRows} fallback={attempt.user_answer} />
                </details>
              );
            })}
          </div>
        </section>
      )}

      {quizAttempts.length > 0 && (
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-extrabold admin-text-title">Yakuniy testlar</h3>
            <span className="rounded-full bg-violet-500/10 px-2.5 py-1 text-xs font-bold text-violet-600 dark:text-violet-300">{quizAttempts.length} urinish</span>
          </div>
          <div className="space-y-3">
            {quizAttempts.map((attempt) => (
              <details key={`quiz-${attempt.id}`} open={attempt.id === quizAttempts[0]?.id} className="group rounded-2xl border border-border bg-surface-100 p-4 open:shadow-card">
                <summary className="flex cursor-pointer list-none items-center gap-3">
                  <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ${attempt.score >= 60 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                    <FileQuestion size={19} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-bold admin-text-title">Yakuniy test</span>
                    <span className="mt-0.5 block text-xs admin-text-muted">{formatDate(attempt.submitted_at)} · {attempt.correct_count}/{attempt.total_count} to‘g‘ri</span>
                  </span>
                  <strong className={`${attempt.score >= 60 ? 'text-emerald-500' : 'text-red-500'}`}>{attempt.score}%</strong>
                </summary>
                <div className="mt-3 space-y-2">
                  {attempt.answers.map((answer, index) => (
                    <div key={answer.id} className={`rounded-xl border p-3 ${answer.is_correct ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
                      <div className="flex items-start gap-2">
                        {answer.is_correct
                          ? <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-500" />
                          : <XCircle size={16} className="mt-0.5 shrink-0 text-red-500" />}
                        <div className="min-w-0 text-xs">
                          <p className="font-bold admin-text-title">{index + 1}. {answer.question_snapshot}</p>
                          <p className="mt-1 admin-text-muted">O‘quvchi javobi: <span className="font-semibold admin-text-body">{answer.selected_text || 'Javob berilmagan'}</span></p>
                          {!answer.is_correct && <p className="mt-0.5 text-emerald-600 dark:text-emerald-300">To‘g‘ri javob: <strong>{answer.correct_text}</strong></p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
