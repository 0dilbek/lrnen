import { useState } from 'react';
import { MousePointer, PenLine, GitMerge, Headphones, Mic, ChevronDown, ChevronUp } from 'lucide-react';
import ChooseCorrectExercise from './ChooseCorrectExercise';
import FillBlankExercise from './FillBlankExercise';
import MatchingExercise from './MatchingExercise';
import ListeningExercise from './ListeningExercise';

const TYPE_META = {
  choose_correct: {
    label: "To'g'ri so'zni tanlash",
    icon: MousePointer,
    color: 'text-purple-600 bg-purple-50 border-purple-200',
  },
  fill_blank: {
    label: "Bo'sh joy to'ldirish",
    icon: PenLine,
    color: 'text-blue-600 bg-blue-50 border-blue-200',
  },
  matching: {
    label: 'Moslashtirish',
    icon: GitMerge,
    color: 'text-orange-600 bg-orange-50 border-orange-200',
  },
  listening: {
    label: 'Listening',
    icon: Headphones,
    color: 'text-teal-600 bg-teal-50 border-teal-200',
  },
  speaking: {
    label: 'Speaking',
    icon: Mic,
    color: 'text-rose-600 bg-rose-50 border-rose-200',
  },
};

export default function ExerciseBlock({ exercise, index }) {
  const [open, setOpen] = useState(true);
  const [result, setResult] = useState(null);

  const meta = TYPE_META[exercise.type] || {
    label: exercise.type,
    icon: PenLine,
    color: 'text-gray-600 bg-gray-50 border-gray-200',
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
  }[exercise.type];

  return (
    <div className="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-sm">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-5 py-4 hover:bg-gray-50 transition text-left"
      >
        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${meta.color}`}>
          <Icon size={13} />
          {meta.label}
        </span>
        <span className="text-sm text-gray-700 font-medium flex-1">{exercise.instruction}</span>
        {result && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            result.correct === result.total ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-600'
          }`}>
            {result.correct}/{result.total}
          </span>
        )}
        {open ? <ChevronUp size={16} className="text-gray-400 shrink-0" /> : <ChevronDown size={16} className="text-gray-400 shrink-0" />}
      </button>

      {open && Component && (
        <div className="px-5 pb-5 border-t border-gray-100 pt-4">
          <Component exercise={exercise} onComplete={handleComplete} />
        </div>
      )}
    </div>
  );
}
