import { Check, Flag, LockKeyhole, Play, Sparkles, Star } from 'lucide-react';
import { formatLessonTitle } from '../../utils/lessonDisplay';

const LESSONS_PER_REGION = 8;

const THEMES = [
  {
    key: 'meadow',
    eyebrow: 'Sayohat boshlanishi',
    title: 'Yashil vodiy',
    description: 'Poydevorni mustahkamlang va ilk marralarni zabt eting.',
    icon: '🌱',
    decorations: ['☁️', '🌳', '🌼'],
  },
  {
    key: 'coast',
    eyebrow: 'Yangi ufqlar',
    title: 'Bilim sohillari',
    description: 'Har bir dars bilan yangi til ko‘nikmalarini kashf eting.',
    icon: '⛵',
    decorations: ['☀️', '🌴', '🐚'],
  },
  {
    key: 'forest',
    eyebrow: 'Kashfiyotlar davom etadi',
    title: 'Sirli o‘rmon',
    description: 'Murakkabroq mavzulardan dadil va izchil o‘ting.',
    icon: '🌲',
    decorations: ['🦉', '🍄', '🌿'],
  },
  {
    key: 'desert',
    eyebrow: 'Mahorat sinovi',
    title: 'Oltin sahro',
    description: 'Mashqlarni bajaring va bilim xazinasiga yaqinlashing.',
    icon: '🏜️',
    decorations: ['☀️', '🌵', '🏺'],
  },
  {
    key: 'mountain',
    eyebrow: 'Cho‘qqilar sari',
    title: 'Baland tog‘lar',
    description: 'Yuqori natijalarga olib boradigan qiyin yo‘lni zabt eting.',
    icon: '🏔️',
    decorations: ['☁️', '🦅', '🏕️'],
  },
  {
    key: 'sky',
    eyebrow: 'Ustalik bosqichi',
    title: 'Yulduzlar olami',
    description: 'Til mahoratingizni yangi darajaga olib chiqing.',
    icon: '🚀',
    decorations: ['✨', '🪐', '🌙'],
  },
];

const DESKTOP_X = [50, 29, 24, 39, 64, 75, 61, 36];
const MOBILE_X = [34, 67, 33, 66, 35, 68, 34, 66];
const TOP_GAP = 118;
const STEP_GAP = 150;

function splitIntoRegions(lessons) {
  const regions = [];
  for (let index = 0; index < lessons.length; index += LESSONS_PER_REGION) {
    regions.push(lessons.slice(index, index + LESSONS_PER_REGION));
  }
  return regions;
}

function getPoint(index, xPattern) {
  return {
    x: xPattern[index % xPattern.length],
    y: TOP_GAP + index * STEP_GAP,
  };
}

function buildPath(count, xPattern) {
  if (!count) return '';
  const points = Array.from({ length: count }, (_, index) => getPoint(index, xPattern));
  return points.reduce((path, point, index) => {
    const x = point.x * 10;
    if (index === 0) return `M ${x} ${point.y}`;
    const previous = points[index - 1];
    const previousX = previous.x * 10;
    const middleY = (previous.y + point.y) / 2;
    return `${path} C ${previousX} ${middleY}, ${x} ${middleY}, ${x} ${point.y}`;
  }, '');
}

function getLessonState(lesson, lessonProgress, currentLessonId) {
  if (lessonProgress?.status === 'completed') return 'completed';
  if (lesson.is_locked) return 'locked';
  if (lesson.id === currentLessonId) return 'current';
  return 'available';
}

function stateLabel(state) {
  if (state === 'completed') return 'Yakunlandi';
  if (state === 'locked') return 'Qulflangan';
  if (state === 'current') return 'Hozirgi dars';
  return 'Ochiq dars';
}

export default function LearningRoadmap({ lessons, progress = {}, onOpenLesson }) {
  if (!lessons.length) {
    return (
      <div className="student-card px-5 py-16 text-center">
        <div className="mb-4 text-6xl" aria-hidden="true">🗺️</div>
        <h2 className="stu-title text-xl font-extrabold">Hozircha darslar yo‘q</h2>
        <p className="stu-muted mt-2">Sizga dars biriktirilganda yo‘l xaritasi shu yerda paydo bo‘ladi.</p>
      </div>
    );
  }

  const regions = splitIntoRegions(lessons);
  const currentLesson = lessons.find(
    (lesson) => progress[lesson.id]?.status !== 'completed' && !lesson.is_locked,
  );

  return (
    <div className="learning-roadmap" aria-label="Darslar yo‘l xaritasi">
      <div className="roadmap-legend" aria-label="Belgilar izohi">
        <span><Check size={14} /> Yakunlangan</span>
        <span><Play size={13} /> Hozirgi dars</span>
        <span><LockKeyhole size={13} /> Hali ochilmagan</span>
      </div>

      {regions.map((regionLessons, regionIndex) => {
        const theme = THEMES[regionIndex % THEMES.length];
        const completedInRegion = regionLessons.filter(
          (lesson) => progress[lesson.id]?.status === 'completed',
        ).length;
        const stageHeight = TOP_GAP * 2 + Math.max(0, regionLessons.length - 1) * STEP_GAP;
        const startNumber = regionIndex * LESSONS_PER_REGION + 1;
        const endNumber = startNumber + regionLessons.length - 1;

        return (
          <section
            key={`${theme.key}-${regionIndex}`}
            className={`roadmap-region roadmap-theme-${theme.key}`}
            aria-labelledby={`roadmap-region-${regionIndex}`}
          >
            <div className="roadmap-region-glow" aria-hidden="true" />
            <span className="roadmap-decoration roadmap-decoration-one" aria-hidden="true">
              {theme.decorations[0]}
            </span>
            <span className="roadmap-decoration roadmap-decoration-two" aria-hidden="true">
              {theme.decorations[1]}
            </span>
            <span className="roadmap-decoration roadmap-decoration-three" aria-hidden="true">
              {theme.decorations[2]}
            </span>

            <header className="roadmap-region-header">
              <div className="roadmap-region-icon" aria-hidden="true">{theme.icon}</div>
              <div className="min-w-0 flex-1">
                <p className="roadmap-region-eyebrow">{regionIndex + 1}-hudud · {theme.eyebrow}</p>
                <h2 id={`roadmap-region-${regionIndex}`}>{theme.title}</h2>
                <p>{theme.description}</p>
              </div>
              <div className="roadmap-region-score">
                <strong>{completedInRegion}/{regionLessons.length}</strong>
                <span>{startNumber}–{endNumber}-darslar</span>
              </div>
            </header>

            <div className="roadmap-stage" style={{ height: stageHeight }}>
              <svg
                className="roadmap-route roadmap-route-desktop"
                viewBox={`0 0 1000 ${stageHeight}`}
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <path className="roadmap-route-shadow" d={buildPath(regionLessons.length, DESKTOP_X)} />
                <path className="roadmap-route-line" d={buildPath(regionLessons.length, DESKTOP_X)} />
              </svg>
              <svg
                className="roadmap-route roadmap-route-mobile"
                viewBox={`0 0 1000 ${stageHeight}`}
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <path className="roadmap-route-shadow" d={buildPath(regionLessons.length, MOBILE_X)} />
                <path className="roadmap-route-line" d={buildPath(regionLessons.length, MOBILE_X)} />
              </svg>

              {regionLessons.map((lesson, lessonIndex) => {
                const globalIndex = regionIndex * LESSONS_PER_REGION + lessonIndex;
                const desktopPoint = getPoint(lessonIndex, DESKTOP_X);
                const mobilePoint = getPoint(lessonIndex, MOBILE_X);
                const lessonProgress = progress[lesson.id];
                const state = getLessonState(lesson, lessonProgress, currentLesson?.id);
                const isLocked = state === 'locked';
                const score = lessonProgress?.score || 0;

                return (
                  <div
                    id={`roadmap-lesson-${lesson.id}`}
                    key={lesson.id}
                    className={`roadmap-stop roadmap-stop-${state}`}
                    style={{
                      '--roadmap-x': `${desktopPoint.x}%`,
                      '--roadmap-mobile-x': `${mobilePoint.x}%`,
                      '--roadmap-y': `${desktopPoint.y}px`,
                      '--roadmap-delay': `${Math.min(globalIndex, 12) * 55}ms`,
                    }}
                    title={isLocked ? 'Bu dars oldingi dars yakunlangach ochiladi' : undefined}
                  >
                    {state === 'current' && (
                      <span className="roadmap-current-flag">
                        <Flag size={13} /> Siz shu yerdasiz
                      </span>
                    )}

                    <button
                      type="button"
                      className="roadmap-node"
                      disabled={isLocked}
                      onClick={() => !isLocked && onOpenLesson?.(lesson)}
                      aria-label={`${globalIndex + 1}-dars: ${formatLessonTitle(lesson.title)}. ${stateLabel(state)}`}
                    >
                      <span className="roadmap-node-shine" aria-hidden="true" />
                      {state === 'completed' && <Check size={28} strokeWidth={3} />}
                      {state === 'locked' && <LockKeyhole size={25} strokeWidth={2.4} />}
                      {state === 'current' && <Play size={25} fill="currentColor" />}
                      {state === 'available' && <Star size={25} />}
                    </button>

                    <div className="roadmap-lesson-card">
                      <div className="roadmap-lesson-meta">
                        <span>{globalIndex + 1}-dars</span>
                        {state === 'completed' && score > 0 && <strong>{score}%</strong>}
                        {state === 'current' && <Sparkles size={13} />}
                      </div>
                      <h3>{formatLessonTitle(lesson.title)}</h3>
                      <p>{stateLabel(state)}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}

      <div className="roadmap-finish">
        <span aria-hidden="true">🏆</span>
        <div>
          <strong>Yo‘l xaritasining marrasi</strong>
          <p>Barcha darslarni tugatib, til cho‘qqisini zabt eting!</p>
        </div>
      </div>
    </div>
  );
}
