import { useState, useEffect } from 'react';
import api, { getApiErrorMessage } from '../../api';
import {
  Plus, Pencil, Trash2, Loader2, BookOpen,
  X, Check,
  AlertTriangle, MousePointer, PenLine, GitMerge,
  Headphones, Mic, Volume2, BookMarked, Search, Music2,
  ArrowUp, ArrowDown, UploadCloud, ListOrdered, FilePenLine, Scissors,
} from 'lucide-react';

const EXERCISE_TYPES = [
  { value: 'choose_correct', label: "To'g'ri so'zni tanlash", icon: MousePointer, color: 'text-purple-700 dark:text-purple-300 bg-purple-500/15' },
  { value: 'fill_blank',     label: "Bo'sh joy to'ldirish",  icon: PenLine,       color: 'text-blue-700 dark:text-blue-300 bg-blue-500/15' },
  { value: 'matching',       label: 'Moslashtirish',          icon: GitMerge,      color: 'text-orange-700 dark:text-orange-300 bg-orange-500/15' },
  { value: 'listening',      label: 'Listening',              icon: Headphones,    color: 'text-teal-700 dark:text-teal-300 bg-teal-500/15' },
  { value: 'reading',        label: 'Reading',                icon: BookMarked,    color: 'text-indigo-700 dark:text-indigo-300 bg-indigo-500/15' },
  { value: 'speaking',       label: 'Speaking',               icon: Mic,           color: 'text-rose-700 dark:text-rose-300 bg-rose-500/15' },
  { value: 'word_order',     label: "So'zlarni tartiblash",   icon: ListOrdered,   color: 'text-fuchsia-700 dark:text-fuchsia-300 bg-fuchsia-500/15' },
  { value: 'written_answer', label: 'Yozma javob',             icon: FilePenLine,   color: 'text-cyan-700 dark:text-cyan-300 bg-cyan-500/15' },
];

const TABS = [
  { id: 'vocab', label: "Lug'at" },
  { id: 'exercises', label: 'Mashqlar' },
  { id: 'quizzes', label: 'Testlar' },
];

/* ─────────────────────────────────────────────
   Main page
───────────────────────────────────────────── */
export default function AdminLessons() {
  const [categories, setCategories] = useState([]);
  const [levels, setLevels] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [vocab, setVocab] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState('');
  const [selectedCat, setSelectedCat] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [activeTab, setActiveTab] = useState('vocab');
  const [lessonSearch, setLessonSearch] = useState('');
  const [modal, setModal] = useState(null);
  const [confirm, setConfirm] = useState(null);

  const load = async () => {
    try {
      const [c, lvl, l, q, ex, v] = await Promise.all([
        api.get('/courses/categories/'),
        api.get('/courses/levels/'),
        api.get('/courses/lessons/'),
        api.get('/quiz/'),
        api.get('/quiz/exercises/'),
        api.get('/courses/vocabulary/'),
      ]);
      setCategories(c.data);
      setLevels(lvl.data);
      setLessons(l.data);
      setQuizzes(q.data);
      setExercises(ex.data);
      setVocab(v.data);
      setPageError('');
      return c.data;
    } catch (loadError) {
      setPageError(getApiErrorMessage(loadError, 'Admin ma’lumotlarini yuklab bo‘lmadi.'));
      throw loadError;
    }
  };

  useEffect(() => {
    load()
      .then((cats) => { if (cats.length) setSelectedCat(cats[0]); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const askConfirm = (message, onConfirm) => setConfirm({ message, onConfirm });

  const delLesson = (id) =>
    askConfirm("Bu darsni o'chirasizmi? Unga bog'liq testlar ham o'chadi.", async () => {
      await api.delete(`/courses/lessons/${id}/`);
      setLessons((p) => p.filter((l) => l.id !== id));
      if (selectedLesson === id) setSelectedLesson(null);
    });

  const delCategory = (cat) =>
    askConfirm(`"${cat.name}" kategoriyasini o'chirasizmi?`, async () => {
      await api.delete(`/courses/categories/${cat.id}/`);
      setCategories((p) => p.filter((c) => c.id !== cat.id));
      if (selectedCat?.id === cat.id) setSelectedCat(null);
    });

  const delQuiz = (id) =>
    askConfirm("Bu savolni o'chirasizmi?", async () => {
      await api.delete(`/quiz/${id}/`);
      setQuizzes((p) => p.filter((q) => q.id !== id));
    });

  const delExercise = (id) =>
    askConfirm("Bu mashqni o'chirasizmi?", async () => {
      await api.delete(`/quiz/exercises/${id}/`);
      setExercises((p) => p.filter((e) => e.id !== id));
    });

  const delVocab = (id) =>
    askConfirm("Bu lug'at so'zini o'chirasizmi?", async () => {
      await api.delete(`/courses/vocabulary/${id}/`);
      setVocab((p) => p.filter((v) => v.id !== id));
    });

  const closeModal = () => setModal(null);

  const onCategorySaved = async (saved, isNew) => {
    closeModal();
    const cats = await load();
    if (isNew && saved) setSelectedCat(cats.find((c) => c.id === saved.id) ?? cats[0]);
  };

  const filteredLessons = selectedCat
    ? lessons
        .filter((l) => l.category === selectedCat.id)
        .filter((l) =>
          !lessonSearch || l.title.toLowerCase().includes(lessonSearch.toLowerCase())
        )
    : [];

  const currentLesson = lessons.find((l) => l.id === selectedLesson);
  const lQuizzes = currentLesson ? quizzes.filter((q) => q.lesson === currentLesson.id) : [];
  const lExercises = currentLesson ? exercises.filter((e) => e.lesson === currentLesson.id) : [];
  const lVocab = currentLesson ? vocab.filter((v) => v.lesson === currentLesson.id) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="animate-spin text-indigo-400" size={36} />
      </div>
    );
  }

  return (
    <>
    {pageError && (
      <div className="m-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm font-medium text-red-500">
        {pageError}
      </div>
    )}
    <div className="flex min-h-[calc(100vh-65px)] flex-col lg:h-[calc(100vh-81px)] lg:min-h-0 lg:flex-row">

      {/* ── Panel 1: Categories ── */}
      <div className="flex max-h-56 w-full shrink-0 flex-col border-b border-inherit admin-panel-alt lg:max-h-none lg:w-52 lg:border-b-0 lg:border-r">
        <div className="px-3 py-3 border-b border-border flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-widest admin-text-muted">Kategoriya</span>
          <button onClick={() => setModal({ type: 'category' })} className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition" title="Yangi">
            <Plus size={12} />
          </button>
        </div>
        <div className="flex flex-1 gap-1 overflow-auto p-1 lg:block lg:py-1">
          {categories.map((cat) => {
            const count = lessons.filter((l) => l.category === cat.id).length;
            const active = selectedCat?.id === cat.id;
            return (
              <div
                key={cat.id}
                onClick={() => { setSelectedCat(cat); setSelectedLesson(null); }}
                className={`group my-0.5 min-w-40 cursor-pointer rounded-xl border px-3 py-2.5 transition-all admin-cat-item lg:mx-1.5 lg:min-w-0 ${
                  active ? 'active' : 'admin-text-body hover:bg-black/5 dark:hover:bg-surface-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium truncate flex-1">{cat.name}</p>
                  <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
                    <button onClick={(e) => { e.stopPropagation(); setModal({ type: 'category', data: cat }); }} className="admin-btn-ghost !p-1"><Pencil size={11} /></button>
                    <button onClick={(e) => { e.stopPropagation(); delCategory(cat); }} className="admin-btn-danger !p-1"><Trash2 size={11} /></button>
                  </div>
                </div>
                <p className="mt-0.5 text-[11px] admin-text-muted">{count} dars</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Panel 2: Lessons list ── */}
      <div className="flex max-h-72 w-full shrink-0 flex-col border-b border-inherit admin-panel-alt lg:max-h-none lg:w-72 lg:border-b-0 lg:border-r">
        {!selectedCat ? (
          <div className="flex flex-1 items-center justify-center p-4 text-center text-sm admin-text-muted">Kategoriya tanlang</div>
        ) : (
          <>
            <div className="p-3 border-b border-border space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-xs admin-text-muted">{filteredLessons.length} ta dars</p>
                <button onClick={() => setModal({ type: 'lesson', data: { category: selectedCat.id } })} className="admin-btn-primary !py-1.5 !px-2.5 !text-xs">
                  <Plus size={12} /> Dars
                </button>
              </div>
              <input
                type="text"
                value={lessonSearch}
                onChange={(e) => setLessonSearch(e.target.value)}
                placeholder="Dars qidirish..."
                className="admin-input !py-2 !text-xs"
              />
            </div>
            <div className="flex-1 overflow-y-auto py-1">
              {filteredLessons.map((lesson) => {
                const vCount = vocab.filter((v) => v.lesson === lesson.id).length;
                const eCount = exercises.filter((e) => e.lesson === lesson.id).length;
                const qCount = quizzes.filter((q) => q.lesson === lesson.id).length;
                const active = selectedLesson === lesson.id;
                return (
                  <div
                    key={lesson.id}
                    onClick={() => setSelectedLesson(lesson.id)}
                    className={`mx-2 my-0.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all border admin-lesson-item ${
                      active ? 'active' : ''
                    }`}
                  >
                    <p className="text-sm font-medium truncate">{lesson.title}</p>
                    <p className="mt-1 flex gap-1.5 text-[10px] admin-text-muted">
                      <span>{vCount} lug'at</span><span>·</span><span>{eCount} mashq</span><span>·</span><span>{qCount} test</span>
                    </p>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* ── Panel 3: Lesson editor ── */}
      <div className="flex min-h-[32rem] min-w-0 flex-1 flex-col admin-panel lg:min-h-0">
        {!currentLesson ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center admin-text-muted">
              <BookOpen size={48} className="mx-auto mb-3 opacity-20" />
              <p className="text-sm">Darsni tanlang yoki yangi qo'shing</p>
            </div>
          </div>
        ) : (
          <>
            <div className="px-5 py-4 border-b border-inherit flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <h2 className="font-semibold admin-text-title truncate">{currentLesson.title}</h2>
                <p className="text-xs admin-text-muted mt-0.5 truncate">{currentLesson.description || 'Tavsif yo\'q'}</p>
              </div>
              <div className="flex gap-1 shrink-0">
                <button onClick={() => setModal({ type: 'lesson', data: currentLesson })} className="admin-btn-ghost"><Pencil size={14} /></button>
                <button onClick={() => delLesson(currentLesson.id)} className="admin-btn-danger"><Trash2 size={14} /></button>
              </div>
            </div>

            <div className="px-5 border-b border-inherit flex gap-1">
              {TABS.map((tab) => {
                const count = tab.id === 'vocab' ? lVocab.length : tab.id === 'exercises' ? lExercises.length : lQuizzes.length;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`admin-tab px-4 py-3 text-sm font-medium border-b-2 transition -mb-px ${
                      activeTab === tab.id ? 'active' : 'border-transparent'
                    }`}
                  >
                    {tab.label}
                    <span className="ml-1.5 text-xs opacity-60">({count})</span>
                  </button>
                );
              })}
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {activeTab === 'vocab' && (
                <TabContent
                  count={lVocab.length}
                  empty="Lug'at so'zlari yo'q"
                  onAdd={() => setModal({ type: 'vocab', data: { lesson: currentLesson.id } })}
                  addLabel="So'z qo'shish"
                >
                  <div className="space-y-1.5">
                    {lVocab.map((v) => (
                      <div key={v.id} className="flex items-center gap-3 px-4 py-2.5 bg-surface-100 border border-border rounded-xl group">
                        <span className="w-32 shrink-0 text-sm font-semibold text-indigo-700 dark:text-indigo-300">{v.word}</span>
                        <span className="admin-text-muted">—</span>
                        <span className="text-sm admin-text-body flex-1">{v.translation}</span>
                        {v.example && <span className="hidden max-w-xs truncate text-xs italic admin-text-muted lg:block">"{v.example}"</span>}
                        <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
                          <button onClick={() => setModal({ type: 'vocab', data: v })} className="admin-btn-ghost !p-1"><Pencil size={12} /></button>
                          <button onClick={() => delVocab(v.id)} className="admin-btn-danger !p-1"><Trash2 size={12} /></button>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabContent>
              )}

              {activeTab === 'exercises' && (
                <TabContent
                  count={lExercises.length}
                  empty="Mashqlar yo'q"
                  onAdd={() => setModal({ type: 'exercise', data: { lesson: currentLesson.id } })}
                  addLabel="Mashq qo'shish"
                >
                  <div className="space-y-2">
                    {lExercises.map((ex) => {
                      const meta = EXERCISE_TYPES.find((t) => t.value === ex.type);
                      const Icon = meta?.icon || PenLine;
                      return (
                        <div key={ex.id} className="flex items-start gap-3 px-4 py-3 bg-surface-100 border border-border rounded-xl group">
                          <div className="flex-1 min-w-0">
                            <span className={`mb-1.5 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${meta?.color || 'admin-text-muted bg-surface-200'}`}>
                              <Icon size={10} />{meta?.label || ex.type}
                            </span>
                            <p className="text-sm admin-text-body">{ex.instruction}</p>
                            <div className="flex flex-wrap gap-2 mt-2 text-[10px] admin-text-muted">
                              <span>Tartib: {ex.order}</span>
                              {ex.type === 'reading' && <span className="text-indigo-500 font-bold">{ex.content?.pages?.length || 0} sahifa</span>}
                              {ex.type === 'listening' && <span className={ex.audio_url ? 'text-emerald-500 font-bold' : 'text-amber-500 font-bold'}>{ex.audio_url ? 'Audio tayyor' : 'Audio tanlanmagan'}</span>}
                            </div>
                          </div>
                          <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
                            <button onClick={() => setModal({ type: 'exercise', data: ex })} className="admin-btn-ghost !p-1"><Pencil size={12} /></button>
                            <button onClick={() => delExercise(ex.id)} className="admin-btn-danger !p-1"><Trash2 size={12} /></button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </TabContent>
              )}

              {activeTab === 'quizzes' && (
                <TabContent
                  count={lQuizzes.length}
                  empty="Test savollari yo'q"
                  onAdd={() => setModal({ type: 'quiz', data: { lesson: currentLesson.id } })}
                  addLabel="Savol qo'shish"
                >
                  <div className="space-y-2">
                    {lQuizzes.map((q, qi) => (
                      <div key={q.id} className="px-4 py-3 bg-surface-100 border border-border rounded-xl group">
                        <div className="flex items-start gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium admin-text-body">
                              <span className="mr-1 admin-text-muted">{qi + 1}.</span>{q.question}
                            </p>
                            {qi === 0 && <span className="inline-flex mt-1.5 text-[10px] font-black uppercase tracking-wide text-amber-500 bg-amber-500/10 border border-amber-500/25 rounded-full px-2 py-0.5">Namuna · ballga kirmaydi</span>}
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              {q.options.map((opt, i) => (
                                <span key={i} className={`text-xs px-2.5 py-1 rounded-lg inline-flex items-center gap-1 ${
                                  i === q.correct_option_index
                                    ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 font-semibold'
                                    : 'bg-surface-200 admin-text-muted border border-border'
                                }`}>
                                  {i === q.correct_option_index && <Check size={9} />}{opt}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
                            <button onClick={() => setModal({ type: 'quiz', data: q })} className="admin-btn-ghost !p-1"><Pencil size={12} /></button>
                            <button onClick={() => delQuiz(q.id)} className="admin-btn-danger !p-1"><Trash2 size={12} /></button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabContent>
              )}
            </div>
          </>
        )}
      </div>
    </div>

      {/* ── Modals ── */}
      {modal?.type === 'lesson' && (
        <LessonModal
          data={modal.data}
          categories={categories}
          levels={levels}
          onClose={closeModal}
          onSave={async () => { closeModal(); await load(); }}
        />
      )}
      {modal?.type === 'category' && (
        <CategoryModal
          data={modal.data}
          onClose={closeModal}
          onSave={(saved) => onCategorySaved(saved, !modal.data?.id)}
        />
      )}
      {modal?.type === 'quiz' && (
        <QuizModal
          data={modal.data}
          lessons={lessons}
          onClose={closeModal}
          onSave={async () => { closeModal(); await load(); }}
        />
      )}
      {modal?.type === 'exercise' && (
        <ExerciseModal
          data={modal.data}
          lessons={lessons}
          onClose={closeModal}
          onSave={async () => { closeModal(); await load(); }}
        />
      )}
      {modal?.type === 'vocab' && (
        <VocabModal
          data={modal.data}
          lessons={lessons}
          onClose={closeModal}
          onSave={async () => { closeModal(); await load(); }}
        />
      )}
      {confirm && (
        <ConfirmModal
          message={confirm.message}
          onConfirm={confirm.onConfirm}
          onDone={() => setConfirm(null)}
          onCancel={() => setConfirm(null)}
        />
      )}
    </>
  );
}

function TabContent({ children, empty, onAdd, addLabel, count }) {
  return (
    <>
      <div className="flex justify-end mb-4">
        <button onClick={onAdd} className="admin-btn-primary !text-xs">
          <Plus size={13} /> {addLabel}
        </button>
      </div>
      {count > 0 ? children : (
        <div className="py-16 text-center admin-text-muted">
          <p className="text-sm">{empty}</p>
          <button onClick={onAdd} className="mt-3 text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-300 dark:hover:text-indigo-200">{addLabel}</button>
        </div>
      )}
    </>
  );
}

/* ─────────────────────────────────────────────
   Confirm dialog
───────────────────────────────────────────── */
function ConfirmModal({ message, onConfirm, onDone, onCancel }) {
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');

  const handleConfirm = async () => {
    setDeleting(true);
    setError('');
    try {
      await onConfirm();
      onDone();
    } catch (deleteError) {
      setError(getApiErrorMessage(deleteError, 'O‘chirishda xatolik yuz berdi.'));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="admin-modal rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-start gap-3 mb-5">
          <div className="p-2 rounded-full bg-red-500/15 shrink-0">
            <AlertTriangle size={20} className="text-red-400" />
          </div>
          <p className="admin-text-body text-sm leading-relaxed pt-1">{message}</p>
        </div>
        {error && <p className="mb-4 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-500">{error}</p>}
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} disabled={deleting} className="admin-btn-ghost">Bekor qilish</button>
          <button onClick={handleConfirm} disabled={deleting} className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-60 text-white text-sm font-medium transition">
            {deleting ? 'O‘chirilmoqda…' : "Ha, o'chirish"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Modal wrapper
───────────────────────────────────────────── */
function ModalWrapper({ title, subtitle, onClose, children, wide = false }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className={`admin-modal rounded-2xl shadow-2xl w-full ${wide ? 'max-w-5xl' : 'max-w-lg'} max-h-[90vh] flex flex-col`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-inherit shrink-0">
          <div>
            <h2 className="font-semibold admin-text-title">{title}</h2>
            {subtitle && <p className="text-xs admin-text-muted mt-0.5">{subtitle}</p>}
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg admin-text-muted hover:admin-text-body hover:bg-black/5 dark:hover:bg-surface-200 transition">
            <X size={18} />
          </button>
        </div>
        <div className="p-6 overflow-y-auto admin-text-body modal-form">{children}</div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Lesson modal
───────────────────────────────────────────── */
function LessonModal({ data, categories, levels, onClose, onSave }) {
  const isEdit = !!data?.id;
  const [form, setForm] = useState({
    title_kaa: data?.title_kaa ?? data?.title ?? '',
    title_uz: data?.title_uz ?? data?.title ?? '',
    description_kaa: data?.description_kaa ?? data?.description ?? '',
    description_uz: data?.description_uz ?? data?.description ?? '',
    video_url_kaa: data?.video_url_kaa ?? data?.video_url ?? '',
    video_url_uz: data?.video_url_uz ?? '',
    category: data?.category ?? '',
    order: data?.order ?? 0,
  });
  const [selectedLevelIds, setSelectedLevelIds] = useState(
    data?.levels?.map((l) => l.id) ?? []
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const toggleLevel = (id) =>
    setSelectedLevelIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );

  const handleSave = async () => {
    if (!form.title_kaa.trim() || !form.title_uz.trim()) {
      return setError('Dars nomini qoraqalpoqcha va o‘zbekcha kiriting');
    }
    setError('');
    setSaving(true);
    try {
      const payload = {
        ...form,
        // Legacy fields remain populated for old clients and exports.
        title: form.title_kaa,
        description: form.description_kaa,
        video_url: form.video_url_kaa || null,
        video_url_kaa: form.video_url_kaa || null,
        video_url_uz: form.video_url_uz || null,
        level_ids: selectedLevelIds,
      };
      if (isEdit) {
        await api.put(`/courses/lessons/${data.id}/`, payload);
      } else {
        await api.post('/courses/lessons/', payload);
      }
      onSave();
    } catch (saveError) {
      setError(getApiErrorMessage(saveError, 'Darsni saqlashda xatolik yuz berdi.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalWrapper title={isEdit ? 'Darsni tahrirlash' : 'Yangi dars qo\'shish'} onClose={onClose}>
      <div className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Dars nomi — Qoraqalpoqcha *" value={form.title_kaa} onChange={(v) => set('title_kaa', v)} placeholder="Qaraqalpaqsha ataması" />
          <Field label="Dars nomi — O‘zbekcha *" value={form.title_uz} onChange={(v) => set('title_uz', v)} placeholder="O‘zbekcha nomi" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <LessonVideoField
            label="Qoraqalpoq guruh videosi"
            value={form.video_url_kaa}
            onChange={(value) => set('video_url_kaa', value)}
          />
          <LessonVideoField
            label="O‘zbek guruh videosi"
            value={form.video_url_uz}
            onChange={(value) => set('video_url_uz', value)}
            optional
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Kategoriya</label>
          <select
            value={form.category}
            onChange={(e) => set('category', e.target.value)}
            className="admin-input text-sm"
          >
            <option value="">— Tanlanmagan —</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Daraja (bir nechta tanlash mumkin)</label>
          <div className="flex flex-wrap gap-2">
            {levels.map((lvl) => {
              const active = selectedLevelIds.includes(lvl.id);
              return (
                <button
                  key={lvl.id}
                  type="button"
                  onClick={() => toggleLevel(lvl.id)}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
                    active
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'admin-panel-alt admin-text-muted border-border hover:border-indigo-500/40'
                  }`}
                >
                  {active && <Check size={10} className="inline mr-1" />}
                  {lvl.name}
                </button>
              );
            })}
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <TextAreaField label="Tavsif — Qoraqalpoqcha" value={form.description_kaa} onChange={(v) => set('description_kaa', v)} placeholder="Sabaq haqqında qısqasha maǵlıwmat..." />
          <TextAreaField label="Tavsif — O‘zbekcha" value={form.description_uz} onChange={(v) => set('description_uz', v)} placeholder="Dars haqida qisqacha ma’lumot..." />
        </div>
        <Field label="Tartib raqami" value={String(form.order)} onChange={(v) => set('order', Number(v))} type="number" />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full admin-btn-primary py-2.5 justify-center"
        >
          {saving && <Loader2 className="animate-spin" size={15} />}
          {isEdit ? 'Saqlash' : 'Qo\'shish'}
        </button>
      </div>
    </ModalWrapper>
  );
}

function LessonVideoField({ label, value, onChange, optional = false }) {
  return (
    <div className="space-y-2 rounded-xl border border-border p-3">
      <label className="block text-sm font-medium">{label}</label>
      {value && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-3 py-2">
          <span className="truncate text-xs font-semibold text-emerald-500">
            {value.split('/').pop() || 'Video biriktirilgan'}
          </span>
          <button type="button" onClick={() => onChange('')} className="admin-btn-danger !p-1.5" title="Videoni olib tashlash">
            <X size={13} />
          </button>
        </div>
      )}
      <MediaUploadField
        kind="video"
        accept="video/mp4,video/webm,video/quicktime"
        label={value ? 'Video faylni almashtirish' : 'Video faylni yuklash'}
        onUploaded={(asset) => onChange(asset.url)}
      />
      <p className="text-xs admin-text-muted">{optional ? 'Hozircha bo‘sh qoldirish mumkin.' : 'Mavjud videolar shu guruhga tegishli.'}</p>
    </div>
  );
}

function TextAreaField({ label, value, onChange, placeholder }) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} rows={3} placeholder={placeholder} className="admin-input resize-none text-sm" />
    </div>
  );
}

/* ─────────────────────────────────────────────
   Category modal
───────────────────────────────────────────── */
function CategoryModal({ data, onClose, onSave }) {
  const isEdit = !!data?.id;
  const [form, setForm] = useState({ name: data?.name ?? '', description: data?.description ?? '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!form.name.trim()) return setError('Kategoriya nomi majburiy');
    setError('');
    setSaving(true);
    try {
      let res;
      if (isEdit) {
        res = await api.put(`/courses/categories/${data.id}/`, form);
      } else {
        res = await api.post('/courses/categories/', form);
      }
      onSave(res.data);
    } catch (saveError) {
      setError(getApiErrorMessage(saveError, 'Kategoriyani saqlashda xatolik yuz berdi.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalWrapper title={isEdit ? 'Kategoriyani tahrirlash' : 'Yangi kategoriya'} onClose={onClose}>
      <div className="space-y-4">
        <Field label="Kategoriya nomi *" value={form.name} onChange={(v) => setForm((f) => ({ ...f, name: v }))} placeholder="Masalan: Grammar" />
        <div>
          <label className="block text-sm font-medium mb-1">Tavsif</label>
          <textarea
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            rows={2}
            placeholder="Ixtiyoriy..."
            className="admin-input resize-none text-sm"
          />
        </div>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full admin-btn-primary py-2.5 justify-center"
        >
          {saving && <Loader2 className="animate-spin" size={15} />}
          {isEdit ? 'Saqlash' : 'Qo\'shish'}
        </button>
      </div>
    </ModalWrapper>
  );
}

/* ─────────────────────────────────────────────
   Quiz modal  (create + edit, dynamic options)
───────────────────────────────────────────── */
function QuizModal({ data, lessons, onClose, onSave }) {
  const isEdit = !!data?.id;
  const [form, setForm] = useState({
    lesson: data?.lesson ?? '',
    question: data?.question ?? '',
    options: data?.options?.length ? [...data.options] : ['', '', '', ''],
    correct_option_index: data?.correct_option_index ?? 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const updateOption = (i, val) => {
    const opts = [...form.options];
    opts[i] = val;
    setForm((f) => ({ ...f, options: opts }));
  };

  const addOption = () => {
    if (form.options.length >= 6) return;
    setForm((f) => ({ ...f, options: [...f.options, ''] }));
  };

  const removeOption = (i) => {
    if (form.options.length <= 2) return;
    const opts = form.options.filter((_, idx) => idx !== i);
    const correct = form.correct_option_index >= opts.length
      ? opts.length - 1
      : form.correct_option_index === i
        ? 0
        : form.correct_option_index > i
          ? form.correct_option_index - 1
          : form.correct_option_index;
    setForm((f) => ({ ...f, options: opts, correct_option_index: correct }));
  };

  const handleSave = async () => {
    if (!form.lesson) return setError('Darsni tanlang');
    if (!form.question.trim()) return setError('Savol matni majburiy');
    if (form.options.some((o) => !o.trim())) return setError('Barcha variantlarni to\'ldiring');
    setError('');
    setSaving(true);
    try {
      if (isEdit) {
        await api.put(`/quiz/${data.id}/`, form);
      } else {
        await api.post('/quiz/', form);
      }
      onSave();
    } catch (saveError) {
      setError(getApiErrorMessage(saveError, 'Testni saqlashda xatolik yuz berdi.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalWrapper
      title={isEdit ? 'Savolni tahrirlash' : 'Yangi savol qo\'shish'}
      subtitle="To'g'ri javobni radio tugma bilan belgilang"
      onClose={onClose}
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Dars *</label>
          <select
            value={form.lesson}
            onChange={(e) => setForm((f) => ({ ...f, lesson: Number(e.target.value) }))}
            className="admin-input text-sm"
          >
            <option value="">— Darsni tanlang —</option>
            {lessons.map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Savol *</label>
          <textarea
            value={form.question}
            onChange={(e) => setForm((f) => ({ ...f, question: e.target.value }))}
            rows={2}
            placeholder="Savol matnini kiriting..."
            className="admin-input resize-none text-sm"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium admin-text-body">Javob variantlari *</label>
            {form.options.length < 6 && (
              <button
                onClick={addOption}
                className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <Plus size={11} /> Variant qo'shish
              </button>
            )}
          </div>
          <div className="space-y-2">
            {form.options.map((opt, i) => {
              const isCorrect = form.correct_option_index === i;
              return (
                <div key={i} className="flex items-center gap-2">
                  <button
                    onClick={() => setForm((f) => ({ ...f, correct_option_index: i }))}
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition ${
                      isCorrect ? 'border-green-500 bg-green-500' : 'border-border hover:border-green-400'
                    }`}
                    title="To'g'ri javob sifatida belgilash"
                  >
                    {isCorrect && <div className="w-2 h-2 rounded-full bg-white" />}
                  </button>
                  <input
                    type="text"
                    value={opt}
                    onChange={(e) => updateOption(i, e.target.value)}
                    placeholder={`${i + 1}-variant`}
                    className={`flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 transition ${
                      isCorrect
                        ? 'border-green-500 bg-green-500/10 text-green-700 focus:ring-green-500/25 dark:text-green-300'
                        : 'border-border bg-surface-100 admin-text-body focus:ring-indigo-500/40'
                    }`}
                  />
                  {form.options.length > 2 && (
                    <button
                      onClick={() => removeOption(i)}
                      className="p-1 rounded admin-text-muted hover:text-red-400 transition shrink-0"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full admin-btn-primary py-2.5 justify-center"
        >
          {saving && <Loader2 className="animate-spin" size={15} />}
          {isEdit ? 'Saqlash' : 'Qo\'shish'}
        </button>
      </div>
    </ModalWrapper>
  );
}

/* ─────────────────────────────────────────────
   Reusable text field
───────────────────────────────────────────── */
/* ─────────────────────────────────────────────
   Exercise modal  (3 types)
───────────────────────────────────────────── */
function ExerciseModal({ data, lessons, onClose, onSave }) {
  const isEdit = !!data?.id;
  const [type, setType] = useState(data?.type ?? 'choose_correct');
  const [instructionKaa, setInstructionKaa] = useState(data?.instruction_kaa ?? data?.instruction ?? '');
  const [instructionUz, setInstructionUz] = useState(data?.instruction_uz ?? data?.instruction ?? '');
  const [lessonId, setLessonId] = useState(data?.lesson ?? '');
  const [content, setContent] = useState(() => buildDefaultContent(data));
  const [audioUrl, setAudioUrl] = useState(data?.audio_url ?? '');
  const [hasAudio, setHasAudio] = useState(data?.has_audio ?? false);
  const [order, setOrder] = useState(data?.order ?? 0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  function buildDefaultContent(d) {
    if (d?.content) return d.content;
    return {
      choose_correct: { sentences: [{ before: '', options: ['', ''], after: '', correct: 0 }, { before: '', options: ['', ''], after: '', correct: 0 }] },
      fill_blank:     { sentences: [{ text: '', answer: '' }, { text: '', answer: '' }], word_panel: [] },
      matching:       { left: ['', ''], right: ['', ''], pairs: [0, 1] },
      listening:      { questions: [{ question: '', options: ['', '', '', ''], correct: 0 }, { question: '', options: ['', '', '', ''], correct: 0 }], pages: [] },
      reading:        { passage_title: '', pages: [], questions: [{ question: '', options: ['', '', '', ''], correct: 0 }, { question: '', options: ['', '', '', ''], correct: 0 }] },
      speaking:       { prompt: '' },
      word_order:     { items: [{ tokens: ['', ''], answer: '' }, { tokens: ['', ''], answer: '' }] },
      written_answer: { questions: [{ prompt: '', answer: '', alternatives: [] }, { prompt: '', answer: '', alternatives: [] }] },
    }[d?.type ?? 'choose_correct'] ?? {};
  }

  const switchType = (t) => {
    setType(t);
    setContent({
      choose_correct: { sentences: [{ before: '', options: ['', ''], after: '', correct: 0 }, { before: '', options: ['', ''], after: '', correct: 0 }] },
      fill_blank:     { sentences: [{ text: '', answer: '' }, { text: '', answer: '' }], word_panel: [] },
      matching:       { left: ['', ''], right: ['', ''], pairs: [0, 1] },
      listening:      { questions: [{ question: '', options: ['', '', '', ''], correct: 0 }, { question: '', options: ['', '', '', ''], correct: 0 }], pages: [] },
      reading:        { passage_title: '', pages: [], questions: [{ question: '', options: ['', '', '', ''], correct: 0 }, { question: '', options: ['', '', '', ''], correct: 0 }] },
      speaking:       { prompt: '' },
      word_order:     { items: [{ tokens: ['', ''], answer: '' }, { tokens: ['', ''], answer: '' }] },
      written_answer: { questions: [{ prompt: '', answer: '', alternatives: [] }, { prompt: '', answer: '', alternatives: [] }] },
    }[t] ?? {});
    if (t === 'listening' || t === 'speaking') {
      setHasAudio(true);
    } else {
      setHasAudio(false);
      setAudioUrl('');
    }
  };

  const handleSave = async () => {
    if (!lessonId) return setError('Darsni tanlang');
    if (!instructionKaa.trim() || !instructionUz.trim()) {
      return setError('Ko‘rsatmani qoraqalpoqcha va o‘zbekcha kiriting');
    }
    setError(''); setSaving(true);
    try {
      const payload = {
        lesson: Number(lessonId), type,
        instruction: instructionKaa,
        instruction_kaa: instructionKaa,
        instruction_uz: instructionUz,
        content,
        has_audio: hasAudio,
        audio_url: audioUrl.trim() || null,
        order: Number(order) || 0,
      };
      if (isEdit) {
        await api.put(`/quiz/exercises/${data.id}/`, payload);
      } else {
        await api.post('/quiz/exercises/', payload);
      }
      onSave();
    } catch (saveError) {
      setError(getApiErrorMessage(saveError, 'Mashqni saqlashda xatolik yuz berdi.'));
    }
    finally { setSaving(false); }
  };

  return (
    <ModalWrapper
      title={isEdit ? 'Mashqni tahrirlash' : 'Yangi mashq qo\'shish'}
      subtitle="Birinchi savol namuna sifatida ko'rsatiladi va natijaga qo'shilmaydi"
      onClose={onClose}
      wide
    >
      <div className="space-y-4">
        {/* Lesson select */}
        <div>
          <label className="block text-sm font-medium mb-1">Dars *</label>
          <select
            value={lessonId}
            onChange={(e) => setLessonId(e.target.value)}
            className="admin-input text-sm"
          >
            <option value="">— Tanlang —</option>
            {lessons.map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
          </select>
        </div>

        {/* Type selector */}
        <div>
          <label className="block text-sm font-medium mb-2">Mashq turi</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
            {EXERCISE_TYPES.map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.value}
                  onClick={() => !isEdit && switchType(t.value)}
                  disabled={isEdit}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-xs font-medium transition ${
                    type === t.value ? 'border-indigo-500 bg-indigo-500/15 text-indigo-400' : 'border-border admin-text-muted hover:border-indigo-500/30'
                  } disabled:opacity-60 disabled:cursor-default`}
                >
                  <Icon size={18} />
                  <span className="text-center leading-tight">{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Audio URL — listening / speaking uchun */}
        {(type === 'listening' || type === 'speaking') && (
          <div className="space-y-2">
            <label className="block text-sm font-medium">
              <Volume2 size={14} className="inline mr-1 text-teal-600" />
              Audio URL
            </label>
            <input
              type="text"
              value={audioUrl}
              onChange={(e) => { setAudioUrl(e.target.value); setHasAudio(!!e.target.value.trim()); }}
              placeholder="https://... yoki YouTube URL"
              className="w-full rounded-xl border border-teal-500/30 bg-teal-500/10 px-4 py-2.5 text-sm admin-text-body focus:outline-none focus:ring-2 focus:ring-teal-500/30"
            />
            <p className="text-xs admin-text-muted">MP3 URL yoki YouTube havola kiritish mumkin</p>
            <MediaUploadField
              kind="audio"
              accept="audio/*"
              label="Audio faylni VPS uchun yuklash"
              onUploaded={(asset) => { setAudioUrl(asset.url); setHasAudio(true); }}
            />
            {type === 'listening' && (
              <AudioLibraryPicker
                unit={lessons.find((lesson) => lesson.id === Number(lessonId))?.order}
                selected={audioUrl}
                onSelect={(url) => { setAudioUrl(url); setHasAudio(true); }}
              />
            )}
          </div>
        )}

        {type === 'listening' && (
          <BookPagePicker pages={content.pages || []} onChange={(pages) => setContent({ ...content, pages })} compact />
        )}

        {/* Instruction */}
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Ko‘rsatma — Qoraqalpoqcha *" value={instructionKaa} onChange={setInstructionKaa} placeholder="Durıs sózdi tańlań" />
          <Field label="Ko‘rsatma — O‘zbekcha *" value={instructionUz} onChange={setInstructionUz} placeholder="To‘g‘ri so‘zni tanlang" />
        </div>

        {/* Content editor by type */}
        {type === 'choose_correct' && (
          <ChooseCorrectEditor content={content} setContent={setContent} />
        )}
        {type === 'fill_blank' && (
          <FillBlankEditor content={content} setContent={setContent} />
        )}
        {type === 'matching' && (
          <MatchingEditor content={content} setContent={setContent} />
        )}
        {type === 'listening' && (
          <ListeningEditor content={content} setContent={setContent} sourceAudioUrl={audioUrl} />
        )}
        {type === 'reading' && (
          <ReadingEditor content={content} setContent={setContent} />
        )}
        {type === 'speaking' && (
          <SpeakingEditor content={content} setContent={setContent} />
        )}
        {type === 'word_order' && (
          <WordOrderEditor content={content} setContent={setContent} />
        )}
        {type === 'written_answer' && (
          <WrittenAnswerEditor content={content} setContent={setContent} />
        )}

        <div className="grid sm:grid-cols-2 gap-3 items-end">
          <Field label="Tartib raqami" value={String(order)} onChange={(value) => setOrder(Number(value))} type="number" />
          <p className="text-xs admin-text-muted pb-3">Kichik raqamli mashq yuqoriroq chiqadi.</p>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full admin-btn-primary py-2.5 justify-center"
        >
          {saving && <Loader2 className="animate-spin" size={15} />}
          {isEdit ? 'Saqlash' : 'Qo\'shish'}
        </button>
      </div>
    </ModalWrapper>
  );
}

/* choose_correct content editor */
function ChooseCorrectEditor({ content, setContent }) {
  const sentences = content.sentences || [];
  const update = (i, key, val) => {
    const s = sentences.map((s, si) => si === i ? { ...s, [key]: val } : s);
    setContent({ sentences: s });
  };
  const updateOption = (i, oi, val) => {
    const s = sentences.map((s, si) => {
      if (si !== i) return s;
      const opts = [...s.options]; opts[oi] = val;
      return { ...s, options: opts };
    });
    setContent({ sentences: s });
  };
  const addSentence = () => setContent({ sentences: [...sentences, { before: '', options: ['', ''], after: '', correct: 0 }] });
  const removeSentence = (i) => setContent({ sentences: sentences.filter((_, si) => si !== i) });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">Gaplar</label>
      {sentences.map((s, i) => (
        <div key={i} className="admin-panel-alt rounded-xl p-3 space-y-2 border">
          <div className="flex gap-2">
            <input value={s.before} onChange={(e) => update(i, 'before', e.target.value)} placeholder="Oldin..." className="admin-input-sm flex-1" />
            <input value={s.after} onChange={(e) => update(i, 'after', e.target.value)} placeholder="Keyin..." className="admin-input-sm flex-1" />
          </div>
          <p className="text-xs admin-text-muted">Variantlar (to'g'risini radio bilan belgilang):</p>
          <div className="flex gap-2 flex-wrap">
            {s.options.map((opt, oi) => (
              <div key={oi} className="flex items-center gap-1">
                <button
                  onClick={() => update(i, 'correct', oi)}
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 ${s.correct === oi ? 'border-green-500 bg-green-500' : 'border-border'}`}
                >
                  {s.correct === oi && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                </button>
                <input value={opt} onChange={(e) => updateOption(i, oi, e.target.value)} placeholder={`${oi + 1}-variant`} className="admin-input-sm w-24" />
              </div>
            ))}
          </div>
          {sentences.length > 1 && (
            <button onClick={() => removeSentence(i)} className="text-xs text-red-400 hover:text-red-600">− Gapni o'chirish</button>
          )}
        </div>
      ))}
      <button onClick={addSentence} className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1">
        <Plus size={12} /> Gap qo'shish
      </button>
    </div>
  );
}

/* fill_blank content editor */
function FillBlankEditor({ content, setContent }) {
  const sentences = content.sentences || [];
  const wordPanel = content.word_panel || [];
  const [wordInput, setWordInput] = useState('');

  const updateSentence = (i, key, val) => {
    const s = sentences.map((s, si) => si === i ? { ...s, [key]: val } : s);
    setContent({ ...content, sentences: s });
  };
  const addSentence = () => setContent({ ...content, sentences: [...sentences, { text: '', answer: '' }] });
  const removeSentence = (i) => setContent({ ...content, sentences: sentences.filter((_, si) => si !== i) });
  const addWord = () => {
    const w = wordInput.trim();
    if (!w) return;
    setContent({ ...content, word_panel: [...wordPanel, w] });
    setWordInput('');
  };
  const removeWord = (i) => setContent({ ...content, word_panel: wordPanel.filter((_, wi) => wi !== i) });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">Gaplar (___ = bo'sh joy)</label>
      {sentences.map((s, i) => (
        <div key={i} className="admin-panel-alt rounded-xl p-3 space-y-2 border">
          <input value={s.text} onChange={(e) => updateSentence(i, 'text', e.target.value)} placeholder="We ___ Australian." className="admin-input-sm w-full" />
          <input value={s.answer} onChange={(e) => updateSentence(i, 'answer', e.target.value)} placeholder="To'g'ri javob..." className="w-full rounded-lg border border-green-500/35 bg-green-500/10 px-3 py-2 text-sm admin-text-body focus:outline-none focus:ring-1 focus:ring-green-500/30" />
          {sentences.length > 1 && <button onClick={() => removeSentence(i)} className="text-xs text-red-400 hover:text-red-600">− O'chirish</button>}
        </div>
      ))}
      <button onClick={addSentence} className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"><Plus size={12} /> Gap qo'shish</button>

      <div>
        <label className="block text-sm font-medium admin-text-body mb-1">So'z paneli (ixtiyoriy)</label>
        <div className="flex flex-wrap gap-1 mb-2">
          {wordPanel.map((w, i) => (
            <span key={i} className="flex items-center gap-1 rounded-lg bg-blue-500/10 px-2 py-1 text-xs text-blue-700 dark:text-blue-300">
              {w}
              <button onClick={() => removeWord(i)} className="text-blue-400 hover:text-red-500"><X size={10} /></button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input value={wordInput} onChange={(e) => setWordInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addWord()} placeholder="So'z kiriting, Enter bosing..." className="admin-input-sm flex-1" />
          <button onClick={addWord} className="rounded-lg bg-blue-500/10 px-3 py-2 text-sm text-blue-700 transition hover:bg-blue-500/20 dark:text-blue-300">+</button>
        </div>
      </div>
    </div>
  );
}

/* matching content editor */
function MatchingEditor({ content, setContent }) {
  const left = content.left || [];
  const right = content.right || [];
  const pairs = content.pairs || [];

  const updateLeft = (i, val) => {
    const l = [...left]; l[i] = val;
    setContent({ left: l, right, pairs });
  };
  const updateRight = (i, val) => {
    const r = [...right]; r[i] = val;
    setContent({ left, right: r, pairs });
  };
  const addPair = () => {
    setContent({ left: [...left, ''], right: [...right, ''], pairs: [...pairs, right.length] });
  };
  const removePair = (i) => {
    setContent({
      left: left.filter((_, li) => li !== i),
      right: right.filter((_, ri) => ri !== i),
      pairs: pairs.filter((_, pi) => pi !== i).map((p) => (p > i ? p - 1 : p)),
    });
  };

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-2 gap-2 text-xs font-medium admin-text-muted px-1">
        <span>Chap (savol)</span>
        <span>O'ng (javob)</span>
      </div>
      {left.map((_, i) => (
        <div key={i} className="flex gap-2 items-center">
          <input value={left[i] || ''} onChange={(e) => updateLeft(i, e.target.value)} placeholder={`Chap ${i + 1}`} className="admin-input-sm flex-1" />
          <span className="admin-text-muted shrink-0">→</span>
          <input value={right[i] || ''} onChange={(e) => updateRight(i, e.target.value)} placeholder={`O'ng ${i + 1}`} className="admin-input-sm flex-1" />
          {left.length > 1 && <button onClick={() => removePair(i)} className="p-1 admin-text-muted hover:text-red-400"><X size={13} /></button>}
        </div>
      ))}
      <p className="text-xs admin-text-muted">* O'ng tomoni avtomatik aralashtiriladi</p>
      <button onClick={addPair} className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"><Plus size={12} /> Juft qo'shish</button>
    </div>
  );
}

/* listening content editor */
function ListeningEditor({ content, setContent, label = 'Tinglash savollari', sourceAudioUrl = '', enableRowAudio = true }) {
  const questions = content.questions || [];
  const audioUrls = Array.isArray(content.audio_urls) ? content.audio_urls : [];

  const updateQ = (i, key, val) => {
    const qs = questions.map((q, qi) => qi === i ? { ...q, [key]: val } : q);
    setContent({ ...content, questions: qs });
  };
  const updateOpt = (i, oi, val) => {
    const qs = questions.map((q, qi) => {
      if (qi !== i) return q;
      const opts = [...q.options]; opts[oi] = val;
      return { ...q, options: opts };
    });
    setContent({ ...content, questions: qs });
  };
  const updateAudio = (index, url) => {
    const next = Array.from({ length: questions.length }, (_, audioIndex) => audioUrls[audioIndex] || '');
    next[index] = url;
    setContent({ ...content, audio_urls: next });
  };
  const addQuestion = () => setContent({
    ...content,
    questions: [...questions, { question: '', options: ['', '', '', ''], correct: 0 }],
    audio_urls: [...audioUrls, ''],
  });
  const removeQuestion = (i) => setContent({
    ...content,
    questions: questions.filter((_, qi) => qi !== i),
    audio_urls: audioUrls.filter((_, audioIndex) => audioIndex !== i),
  });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">{label}</label>
      {questions.map((q, i) => (
        <div key={i} className={`border rounded-xl p-3 space-y-2 ${i === 0 ? 'border-amber-400/50 bg-amber-500/5' : 'border-teal-400/30 bg-teal-500/5'}`}>
          {i === 0 && <p className="text-[10px] font-black uppercase tracking-wider text-amber-500">Namuna · ballga kirmaydi</p>}
          <input
            value={q.question}
            onChange={(e) => updateQ(i, 'question', e.target.value)}
            placeholder={`${i + 1}-savol matni`}
            className="admin-input-sm w-full"
          />
          {enableRowAudio && (
            <QuestionAudioEditor
              value={audioUrls[i] || ''}
              sourceAudioUrl={sourceAudioUrl}
              name={`listening-${i + 1}`}
              onChange={(url) => updateAudio(i, url)}
            />
          )}
          <p className="text-xs admin-text-muted">Variantlar (to'g'risini radio bilan belgilang):</p>
          <div className="space-y-1.5">
            {q.options.map((opt, oi) => (
              <div key={oi} className="flex items-center gap-2">
                <button
                  onClick={() => updateQ(i, 'correct', oi)}
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 ${q.correct === oi ? 'border-green-500 bg-green-500' : 'border-border'}`}
                >
                  {q.correct === oi && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                </button>
                <input
                  value={opt}
                  onChange={(e) => updateOpt(i, oi, e.target.value)}
                  placeholder={`${oi + 1}-variant`}
                  className="admin-input-sm flex-1"
                />
              </div>
            ))}
          </div>
          {questions.length > 1 && (
            <button onClick={() => removeQuestion(i)} className="text-xs text-red-400 hover:text-red-600">
              − Savolni o'chirish
            </button>
          )}
        </div>
      ))}
      <button onClick={addQuestion} className="text-xs text-teal-600 hover:text-teal-700 flex items-center gap-1">
        <Plus size={12} /> Savol qo'shish
      </button>
    </div>
  );
}

function QuestionAudioEditor({ value, sourceAudioUrl, name, onChange }) {
  const [open, setOpen] = useState(false);
  const [start, setStart] = useState('0');
  const [end, setEnd] = useState('5');
  const [cutting, setCutting] = useState(false);
  const [error, setError] = useState('');

  const cut = async () => {
    if (!sourceAudioUrl) {
      setError('Avval yuqoridan asosiy audioni tanlang.');
      return;
    }
    setCutting(true);
    setError('');
    try {
      const { data } = await api.post('/courses/media-audio-clip/', {
        source_url: sourceAudioUrl,
        start_seconds: Number(start),
        end_seconds: Number(end),
        name,
      });
      onChange(data.url);
    } catch (clipError) {
      setError(getApiErrorMessage(clipError, 'Audio parchani yaratib bo‘lmadi.'));
    } finally {
      setCutting(false);
    }
  };

  return (
    <div className="rounded-xl border border-teal-500/25 bg-surface-100 p-2.5">
      <button type="button" onClick={() => setOpen((current) => !current)} className="flex w-full items-center justify-between gap-3 text-left">
        <span className="inline-flex items-center gap-2 text-xs font-bold text-teal-600 dark:text-teal-300">
          <Volume2 size={13} /> {value ? 'Audio parcha biriktirilgan' : 'Bu savolga audio biriktirish'}
        </span>
        <span className="text-[11px] admin-text-muted">{open ? 'Yopish' : 'Sozlash'}</span>
      </button>
      {value && <audio src={value} controls preload="metadata" className="mt-2 h-8 w-full" />}
      {open && (
        <div className="mt-3 space-y-3 border-t border-border pt-3">
          <input value={value} onChange={(event) => onChange(event.target.value)} placeholder="Audio URL" className="admin-input-sm w-full" />
          <MediaUploadField kind="audio" accept="audio/*" label="Alohida audio fayl yuklash" onUploaded={(asset) => onChange(asset.url)} />
          <div className="rounded-xl border border-dashed border-teal-500/30 bg-teal-500/5 p-3">
            <p className="mb-2 flex items-center gap-2 text-xs font-bold text-teal-600 dark:text-teal-300"><Scissors size={14} /> Asosiy audiodan kesib olish</p>
            <div className="grid grid-cols-2 gap-2">
              <Field label="Boshlanish (sekund)" value={start} onChange={setStart} type="number" />
              <Field label="Tugash (sekund)" value={end} onChange={setEnd} type="number" />
            </div>
            <button type="button" onClick={cut} disabled={cutting || !sourceAudioUrl} className="admin-btn-primary mt-3 !px-3 !py-2 !text-xs disabled:opacity-50">
              {cutting ? <Loader2 size={14} className="animate-spin" /> : <Scissors size={14} />}
              Parchani yaratish va biriktirish
            </button>
            {!sourceAudioUrl && <p className="mt-2 text-[11px] text-amber-500">Asosiy Audio URL tanlanmagan.</p>}
          </div>
          {error && <p className="text-xs text-red-500">{error}</p>}
        </div>
      )}
    </div>
  );
}

function ReadingEditor({ content, setContent }) {
  const usesWrittenAnswers = Array.isArray(content.sentences) && !content.questions?.length;
  return (
    <div className="space-y-5 rounded-2xl border border-indigo-500/25 bg-indigo-500/5 p-4">
      <div>
        <label className="block text-sm font-medium mb-1">Matn sarlavhasi</label>
        <input
          value={content.passage_title || ''}
          onChange={(event) => setContent({ ...content, passage_title: event.target.value })}
          placeholder="Masalan: A day in London"
          className="admin-input-sm w-full"
        />
      </div>
      <BookPagePicker pages={content.pages || []} onChange={(pages) => setContent({ ...content, pages })} />
      {usesWrittenAnswers
        ? <FillBlankEditor content={content} setContent={setContent} />
        : <ListeningEditor content={content} setContent={setContent} label="Reading savollari" enableRowAudio={false} />}
    </div>
  );
}

function BookPagePicker({ pages, onChange, compact = false }) {
  const [open, setOpen] = useState(false);
  const [assets, setAssets] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (assets.length) return;
    setLoading(true);
    Promise.all([
      api.get('/quiz/assets/?kind=book'),
      api.get('/courses/media-assets/?kind=image'),
    ])
      .then(([bookResponse, uploadedResponse]) => {
        setAssets([...(uploadedResponse.data || []), ...(bookResponse.data.results || [])]);
      })
      .finally(() => setLoading(false));
  }, [assets.length]);

  const selectedUrls = new Set(pages.map((page) => typeof page === 'string' ? page : page.url));
  const filtered = assets.filter((asset) => !query || String(asset.page_number).includes(query.trim()));
  const add = (asset) => {
    if (selectedUrls.has(asset.url)) return;
    onChange([...pages, {
      url: asset.url,
      page_number: asset.page_number || null,
      caption: asset.page_number ? `Practice Book — ${asset.page_number}-sahifa` : asset.name,
    }]);
  };
  const remove = (index) => onChange(pages.filter((_, pageIndex) => pageIndex !== index));
  const move = (index, direction) => {
    const nextIndex = index + direction;
    if (nextIndex < 0 || nextIndex >= pages.length) return;
    const next = [...pages];
    [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
    onChange(next);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium admin-text-body">Kitob sahifalari *</p>
          <p className="text-xs admin-text-muted">Bir nechta sahifani tanlab, tartibini o'zgartirish mumkin.</p>
        </div>
        <button type="button" onClick={() => setOpen((value) => !value)} className="admin-btn-ghost !text-xs border border-border">
          <BookMarked size={14} /> {open ? 'Kutubxonani yopish' : 'Sahifa tanlash'}
        </button>
      </div>

      <MediaUploadField
        kind="image"
        accept="image/jpeg,image/png,image/webp,image/gif"
        label="Yangi sahifa rasmini yuklash"
        onUploaded={(asset) => {
          setAssets((current) => [asset, ...current]);
          add(asset);
        }}
      />

      {pages.length > 0 ? (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {pages.map((page, index) => {
            const value = typeof page === 'string' ? { url: page } : page;
            const previewUrl = assets.find((asset) => asset.url === value.url)?.preview_url || value.url;
            return (
              <div key={`${value.url}-${index}`} className="relative shrink-0 w-28 rounded-xl border border-border bg-surface-100 overflow-hidden group">
                <img src={previewUrl} alt="" className={`${compact ? 'h-24' : 'h-36'} w-full object-cover object-top`} />
                <div className="px-2 py-1.5 text-[10px] font-bold admin-text-body truncate">{value.page_number ? `${value.page_number}-sahifa` : `Sahifa ${index + 1}`}</div>
                <div className="absolute top-1 right-1 flex gap-1 opacity-0 group-hover:opacity-100 transition">
                  <button type="button" onClick={() => move(index, -1)} className="p-1 bg-black/70 text-white rounded"><ArrowUp size={11} /></button>
                  <button type="button" onClick={() => move(index, 1)} className="p-1 bg-black/70 text-white rounded"><ArrowDown size={11} /></button>
                  <button type="button" onClick={() => remove(index)} className="p-1 bg-red-600 text-white rounded"><X size={11} /></button>
                </div>
              </div>
            );
          })}
        </div>
      ) : <p className="text-xs text-amber-500">Hali sahifa tanlanmagan.</p>}

      {open && (
        <div className="rounded-xl border border-border bg-surface-200/60 p-3">
          <div className="relative mb-3">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 admin-text-muted" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Sahifa raqami..." className="admin-input-sm w-full !pl-9" />
          </div>
          {loading ? <Loader2 className="animate-spin text-indigo-500 mx-auto my-8" /> : (
            <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-8 gap-2 max-h-72 overflow-y-auto pr-1">
              {filtered.map((asset) => (
                <button key={asset.url} type="button" onClick={() => add(asset)} disabled={selectedUrls.has(asset.url)} className={`rounded-lg border overflow-hidden text-left transition ${selectedUrls.has(asset.url) ? 'border-emerald-500 opacity-45' : 'border-border hover:border-indigo-500'}`}>
                  <img src={asset.preview_url || asset.url} alt="" loading="lazy" className="h-24 w-full object-cover object-top" />
                  <span className="block px-1.5 py-1 text-[10px] font-bold admin-text-body">{asset.page_number ? `${asset.page_number}-sahifa` : asset.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AudioLibraryPicker({ unit, selected, onSelect }) {
  const [open, setOpen] = useState(false);
  const [assets, setAssets] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    const unitQuery = unit ? `&unit=${encodeURIComponent(unit)}` : '';
    api.get(`/quiz/assets/?kind=audio${unitQuery}`)
      .then(({ data }) => setAssets(data.results || []))
      .finally(() => setLoading(false));
  }, [open, unit]);

  const filtered = assets.filter((asset) => !query || asset.name.toLowerCase().includes(query.toLowerCase()));
  return (
    <div className="rounded-xl border border-teal-500/25 bg-teal-500/5 p-3">
      <button type="button" onClick={() => { if (!open) setLoading(true); setOpen((value) => !value); }} className="flex items-center justify-between gap-3 w-full text-left">
        <span className="inline-flex items-center gap-2 text-xs font-bold text-teal-500"><Music2 size={14} /> Audio kutubxonasi {unit ? `· Unit ${unit}` : ''}</span>
        <span className="text-xs admin-text-muted">{open ? 'Yopish' : 'Tanlash'}</span>
      </button>
      {open && (
        <div className="mt-3 space-y-2">
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Trekni qidiring..." className="admin-input-sm w-full" />
          <div className="max-h-48 overflow-y-auto space-y-1">
            {loading && <Loader2 className="animate-spin text-teal-500 mx-auto my-5" />}
            {!loading && filtered.map((asset) => (
              <button key={asset.url} type="button" onClick={() => onSelect(asset.url)} className={`w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg border text-xs transition ${selected === asset.url ? 'border-emerald-500 bg-emerald-500/10 text-emerald-500' : 'border-border admin-text-body hover:border-teal-500'}`}>
                <span className="truncate">{asset.name}</span><span className="admin-text-muted shrink-0">{asset.track}</span>
              </button>
            ))}
            {!loading && !filtered.length && <p className="text-xs admin-text-muted text-center py-4">Audio topilmadi.</p>}
          </div>
        </div>
      )}
    </div>
  );
}

/* speaking content editor */
function SpeakingEditor({ content, setContent }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Speaking topshirig'i</label>
      <textarea
        value={content.prompt || ''}
        onChange={(e) => setContent({ prompt: e.target.value })}
        rows={3}
        placeholder="Masalan: Describe your daily routine using Present Simple..."
        className="w-full resize-none rounded-xl border border-rose-500/30 bg-rose-500/5 px-3 py-2.5 text-sm admin-text-body focus:outline-none focus:ring-2 focus:ring-rose-500/25"
      />
      <p className="text-xs admin-text-muted">O'quvchi bu topshiriqni o'qib, audio yozib yuborishi kerak</p>
    </div>
  );
}

/* word_order content editor */
function WordOrderEditor({ content, setContent }) {
  const items = content.items || [];
  const update = (index, key, value) => setContent({
    ...content,
    items: items.map((item, itemIndex) => itemIndex === index ? { ...item, [key]: value } : item),
  });
  const add = () => setContent({ ...content, items: [...items, { tokens: ['', ''], answer: '' }] });
  const remove = (index) => setContent({ ...content, items: items.filter((_, itemIndex) => itemIndex !== index) });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">So‘z tartiblash gaplari</label>
      <p className="text-xs admin-text-muted">So‘zlarni | belgisi bilan ajrating. Birinchi qator namuna bo‘ladi.</p>
      {items.map((item, index) => (
        <div key={index} className="admin-panel-alt space-y-2 rounded-xl border p-3">
          <input value={(item.tokens || []).join(' | ')} onChange={(event) => update(index, 'tokens', event.target.value.split('|').map((token) => token.trim()))} placeholder="Jack | is | not | a | gardener." className="admin-input-sm w-full" />
          <input value={item.answer || ''} onChange={(event) => update(index, 'answer', event.target.value)} placeholder="Jack is not a gardener." className="w-full rounded-lg border border-green-500/35 bg-green-500/10 px-3 py-2 text-sm admin-text-body" />
          {items.length > 2 && <button type="button" onClick={() => remove(index)} className="text-xs text-red-500">− O‘chirish</button>}
        </div>
      ))}
      <button type="button" onClick={add} className="flex items-center gap-1 text-xs text-blue-600"><Plus size={12} /> Gap qo‘shish</button>
    </div>
  );
}

/* written_answer content editor */
function WrittenAnswerEditor({ content, setContent }) {
  const questions = content.questions || [];
  const update = (index, key, value) => setContent({
    ...content,
    questions: questions.map((question, questionIndex) => questionIndex === index ? { ...question, [key]: value } : question),
  });
  const add = () => setContent({ ...content, questions: [...questions, { prompt: '', answer: '', alternatives: [] }] });
  const remove = (index) => setContent({ ...content, questions: questions.filter((_, questionIndex) => questionIndex !== index) });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">To‘liq yozma javoblar</label>
      <p className="text-xs admin-text-muted">Muqobil to‘g‘ri javoblarni | bilan ajrating. Birinchi savol namuna bo‘ladi.</p>
      {questions.map((question, index) => (
        <div key={index} className="admin-panel-alt space-y-2 rounded-xl border p-3">
          <textarea value={question.prompt || ''} onChange={(event) => update(index, 'prompt', event.target.value)} rows={2} placeholder="Savol yoki tuzatiladigan gap..." className="admin-input-sm w-full resize-y" />
          <input value={question.answer || ''} onChange={(event) => update(index, 'answer', event.target.value)} placeholder="To‘g‘ri to‘liq javob" className="w-full rounded-lg border border-green-500/35 bg-green-500/10 px-3 py-2 text-sm admin-text-body" />
          <input value={(question.alternatives || []).join(' | ')} onChange={(event) => update(index, 'alternatives', event.target.value.split('|').map((answer) => answer.trim()).filter(Boolean))} placeholder="Muqobil javoblar (ixtiyoriy)" className="admin-input-sm w-full" />
          {questions.length > 2 && <button type="button" onClick={() => remove(index)} className="text-xs text-red-500">− O‘chirish</button>}
        </div>
      ))}
      <button type="button" onClick={add} className="flex items-center gap-1 text-xs text-blue-600"><Plus size={12} /> Savol qo‘shish</button>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Vocabulary modal
───────────────────────────────────────────── */
function VocabModal({ data, lessons, onClose, onSave }) {
  const isEdit = !!data?.id;
  const [form, setForm] = useState({
    lesson: data?.lesson ?? '',
    word: data?.word ?? '',
    translation_kaa: data?.translation_kaa ?? data?.translation ?? '',
    translation_uz: data?.translation_uz ?? '',
    example: data?.example ?? '',
    order: data?.order ?? 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSave = async () => {
    if (!form.lesson) return setError('Darsni tanlang');
    if (!form.word.trim()) return setError("Inglizcha so'z majburiy");
    if (!form.translation_kaa.trim()) return setError('Qoraqalpoqcha tarjima majburiy');
    if (!form.translation_uz.trim()) return setError('O‘zbekcha tarjima majburiy');
    setError(''); setSaving(true);
    try {
      const payload = { ...form, translation: form.translation_kaa };
      if (isEdit) {
        await api.put(`/courses/vocabulary/${data.id}/`, payload);
      } else {
        await api.post('/courses/vocabulary/', payload);
      }
      onSave();
    } catch (saveError) {
      setError(getApiErrorMessage(saveError, 'Lug‘atni saqlashda xatolik yuz berdi.'));
    }
    finally { setSaving(false); }
  };

  return (
    <ModalWrapper title={isEdit ? "So'zni tahrirlash" : "Yangi lug'at so'zi"} onClose={onClose}>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Dars *</label>
          <select
            value={form.lesson}
            onChange={(e) => set('lesson', e.target.value)}
            className="admin-input text-sm"
          >
            <option value="">— Tanlang —</option>
            {lessons.map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
          </select>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Inglizcha *" value={form.word} onChange={(v) => set('word', v)} placeholder="e.g. beautiful" />
          <Field label="Qoraqalpoqcha *" value={form.translation_kaa} onChange={(v) => set('translation_kaa', v)} placeholder="e.g. sulıw" />
          <Field label="O‘zbekcha *" value={form.translation_uz} onChange={(v) => set('translation_uz', v)} placeholder="e.g. chiroyli" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Misol gap (ixtiyoriy)</label>
          <input
            type="text"
            value={form.example}
            onChange={(e) => set('example', e.target.value)}
            placeholder="e.g. She is a beautiful girl."
            className="admin-input text-sm"
          />
        </div>
        <Field label="Tartib" value={String(form.order)} onChange={(v) => set('order', Number(v))} type="number" />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full admin-btn-primary py-2.5 justify-center"
        >
          {saving && <Loader2 className="animate-spin" size={15} />}
          {isEdit ? 'Saqlash' : "Qo'shish"}
        </button>
      </div>
    </ModalWrapper>
  );
}

/* ─────────────────────────────────────────────
   Reusable text field
───────────────────────────────────────────── */
function MediaUploadField({ kind, accept, label, onUploaded }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const upload = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    const body = new FormData();
    body.append('kind', kind);
    body.append('file', file);
    setError('');
    setProgress(0);
    setUploading(true);
    try {
      const { data } = await api.post('/courses/media-assets/', body, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: ({ loaded, total }) => {
          if (total) setProgress(Math.round((loaded / total) * 100));
        },
      });
      onUploaded(data);
      setProgress(100);
    } catch (uploadError) {
      setError(getApiErrorMessage(uploadError, 'Faylni yuklashda xatolik yuz berdi.'));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="rounded-xl border border-dashed border-indigo-500/35 bg-indigo-500/5 p-3">
      <label className={`flex cursor-pointer items-center justify-between gap-3 ${uploading ? 'pointer-events-none opacity-70' : ''}`}>
        <span className="inline-flex items-center gap-2 text-xs font-bold text-indigo-500">
          {uploading ? <Loader2 size={15} className="animate-spin" /> : <UploadCloud size={15} />}
          {uploading ? `Yuklanmoqda… ${progress}%` : label}
        </span>
        <span className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-bold text-white">Fayl tanlash</span>
        <input type="file" accept={accept} onChange={upload} disabled={uploading} className="sr-only" />
      </label>
      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </div>
  );
}

function Field({ label, value, onChange, placeholder = '', type = 'text' }) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="admin-input text-sm"
      />
    </div>
  );
}
