import BookPageViewer from './BookPageViewer';
import ChooseCorrectExercise from './ChooseCorrectExercise';
import FillBlankExercise from './FillBlankExercise';

export default function ReadingExercise({ exercise, onComplete }) {
  const content = exercise.content || {};
  const hasQuestions = Array.isArray(content.questions) && content.questions.length > 0;
  const hasSentences = Array.isArray(content.sentences) && content.sentences.length > 0;

  return (
    <div className="space-y-6">
      <BookPageViewer pages={content.pages || []} title={content.passage_title || "Matnni o'qing"} />
      <div className="border-t border-border pt-5">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[.16em] font-black text-indigo-500">Topshiriqlar</p>
          <p className="text-sm stu-muted mt-1">Yuqoridagi sahifalarni o'qib, savollarga javob bering.</p>
        </div>
        {hasQuestions && <ChooseCorrectExercise exercise={{ ...exercise, content: { questions: content.questions } }} onComplete={onComplete} />}
        {!hasQuestions && hasSentences && <FillBlankExercise exercise={{ ...exercise, content: { sentences: content.sentences, word_panel: content.word_panel } }} onComplete={onComplete} />}
        {!hasQuestions && !hasSentences && <p className="text-sm stu-muted text-center py-8">Savollar hali kiritilmagan.</p>}
      </div>
    </div>
  );
}
