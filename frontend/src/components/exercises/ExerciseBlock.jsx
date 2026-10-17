import { useState } from 'react';
import { MousePointer, PenLine, GitMerge, Headphones, Mic, BookOpen, ChevronDown, ChevronUp, ListOrdered, FilePenLine, Loader2 } from 'lucide-react';
import api, { getApiErrorMessage } from '../../api';
import ChooseCorrectExercise from './ChooseCorrectExercise';
import FillBlankExercise from './FillBlankExercise';
import MatchingExercise from './MatchingExercise';
import ListeningExercise from './ListeningExercise';
import ReadingExercise from './ReadingExercise';
import WordOrderExercise from './WordOrderExercise';
import WrittenAnswerExercise from './WrittenAnswerExercise';
import { useLanguage } from '../../context/LanguageContext';

const TYPE_META = {
  choose_correct: {
    label: "To'g'ri so'zni tanlash",
    icon: MousePointer,
    color: 'text-purple-700 dark:text-purple-300 bg-purple-500/15 border-purple-500/30',
  },
  fill_blank: {
    label: "Bo'sh joy to'ldirish",
    icon: PenLine,
    color: 'text-blue-700 dark:text-blue-300 bg-blue-500/15 border-blue-500/30',
  },
  matching: {
    label: 'Moslashtirish',
    icon: GitMerge,
    color: 'text-orange-700 dark:text-orange-300 bg-orange-500/15 border-orange-500/30',
  },
  listening: {
    label: 'Listening',
    icon: Headphones,
    color: 'text-teal-700 dark:text-teal-300 bg-teal-500/15 border-teal-500/30',
  },
  reading: {
    label: 'Reading',
    icon: BookOpen,
    color: 'text-indigo-700 dark:text-indigo-300 bg-indigo-500/15 border-indigo-500/30',
  },
  speaking: {
    label: 'Speaking',
    icon: Mic,
    color: 'text-rose-700 dark:text-rose-300 bg-rose-500/15 border-rose-500/30',
  },
  word_order: {
    label: "So'zlarni tartiblash",
    icon: ListOrdered,
    color: 'text-fuchsia-700 dark:text-fuchsia-300 bg-fuchsia-500/15 border-fuchsia-500/30',
  },
  written_answer: {
    label: 'Yozma javob',
    icon: FilePenLine,
    color: 'text-cyan-700 dark:text-cyan-300 bg-cyan-500/15 border-cyan-500/30',
  },
};

export default function ExerciseBlock({ exercise }) {
  const { t } = useLanguage();
  const [open, setOpen] = useState(true);
  const [result, setResult] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  const meta = TYPE_META[exercise.type] || {
    label: exercise.type,
    icon: PenLine,
    color: 'stu-muted bg-surface-200 border-border',
  };
  const Icon = meta.icon;

  const handleComplete = async (correct, total, answer) => {
    setResult({ correct, total });
    if (!answer) return;
    setSaving(true);
    setSaveError('');
    try {
      const response = await api.post('/quiz/exercises/submit/', {
        exercise_id: exercise.id,
        answer,
      });
      setResult({ correct, total, score: response.data.score, saved: true });
    } catch (error) {
      setSaveError(getApiErrorMessage(error, t('Natijani serverga saqlab bo‘lmadi.')));
    } finally {
      setSaving(false);
    }
  };

  const Component = {
    choose_correct: ChooseCorrectExercise,
    fill_blank: FillBlankExercise,
    matching: MatchingExercise,
    listening: ListeningExercise,
    reading: ReadingExercise,
    word_order: WordOrderExercise,
    written_answer: WrittenAnswerExercise,
  }[exercise.type];

  return (
    <div className="student-card overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-5 py-4 hover:bg-surface-200/40 transition text-left"
      >
        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${meta.color}`}>
          <Icon size={13} />
          {t(meta.label)}
        </span>
        <span className="flex-1 text-sm font-medium stu-body">{exercise.instruction}</span>
        {result && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            result.correct === result.total ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300' : 'bg-orange-500/15 text-orange-700 dark:text-orange-300'
          }`}>
            {result.correct}/{result.total}
          </span>
        )}
        {saving && <Loader2 size={15} className="animate-spin text-indigo-500" />}
        {open ? <ChevronUp size={16} className="shrink-0 stu-muted" /> : <ChevronDown size={16} className="shrink-0 stu-muted" />}
      </button>

      {open && Component && (
        <div className="px-5 pb-5 border-t border-border pt-4">
          <Component exercise={exercise} onComplete={handleComplete} />
        </div>
      )}
      {open && saveError && <p className="px-5 pb-4 text-xs font-semibold text-rose-500">{saveError}</p>}
    </div>
  );
}
