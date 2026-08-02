import { useState } from 'react';
import { MousePointer, PenLine, GitMerge, Headphones, Mic, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import ChooseCorrectExercise from './ChooseCorrectExercise';
import FillBlankExercise from './FillBlankExercise';
import MatchingExercise from './MatchingExercise';
import ListeningExercise from './ListeningExercise';
import ReadingExercise from './ReadingExercise';

const TYPE_META = {
  choose_correct: {
    label: "To'g'ri so'zni tanlash",
    icon: MousePointer,
    color: 'text-purple-300 bg-purple-500/15 border-purple-500/30',
  },
  fill_blank: {
    label: "Bo'sh joy to'ldirish",
    icon: PenLine,
    color: 'text-blue-300 bg-blue-500/15 border-blue-500/30',
  },
  matching: {
    label: 'Moslashtirish',
    icon: GitMerge,
    color: 'text-orange-300 bg-orange-500/15 border-orange-500/30',
  },
  listening: {
    label: 'Listening',
    icon: Headphones,
    color: 'text-teal-300 bg-teal-500/15 border-teal-500/30',
  },
  reading: {
    label: 'Reading',
    icon: BookOpen,
    color: 'text-indigo-300 bg-indigo-500/15 border-indigo-500/30',
  },
  speaking: {
    label: 'Speaking',
    icon: Mic,
    color: 'text-rose-300 bg-rose-500/15 border-rose-500/30',
  },
};

export default function ExerciseBlock({ exercise }) {
  const [open, setOpen] = useState(true);
  const [result, setResult] = useState(null);

  const meta = TYPE_META[exercise.type] || {
    label: exercise.type,
    icon: PenLine,
    color: 'text-slate-400 bg-surface-200 border-border',
  };
  const Icon = meta.icon;

  const handleComplete = (correct, total) => {
    setResult({ correct, total });
  };

  const Component = {
    choose_correct: ChooseCorrectExercise,
    fill_blank: FillBlankExercise,
    matching: MatchingExercise,
    listening: ListeningExercise,
    reading: ReadingExercise,
  }[exercise.type];

  return (
    <div className="student-card overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-5 py-4 hover:bg-surface-200/40 transition text-left"
      >
        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${meta.color}`}>
          <Icon size={13} />
          {meta.label}
        </span>
        <span className="text-sm text-slate-300 font-medium flex-1">{exercise.instruction}</span>
        {result && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            result.correct === result.total ? 'bg-emerald-500/15 text-emerald-400' : 'bg-orange-500/15 text-orange-400'
          }`}>
            {result.correct}/{result.total}
          </span>
        )}
        {open ? <ChevronUp size={16} className="text-slate-500 shrink-0" /> : <ChevronDown size={16} className="text-slate-500 shrink-0" />}
      </button>

      {open && Component && (
        <div className="px-5 pb-5 border-t border-border pt-4">
          <Component exercise={exercise} onComplete={handleComplete} />
        </div>
      )}
    </div>
  );
}
