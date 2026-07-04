import { useState, useEffect } from 'react';
import api from '../../api';
import {
  Plus, Pencil, Trash2, Loader2, BookOpen,
  X, Check,
  AlertTriangle, MousePointer, PenLine, GitMerge,
  Headphones, Mic, Volume2,
} from 'lucide-react';

const EXERCISE_TYPES = [
  { value: 'choose_correct', label: "To'g'ri so'zni tanlash", icon: MousePointer, color: 'text-purple-300 bg-purple-500/15' },
  { value: 'fill_blank',     label: "Bo'sh joy to'ldirish",  icon: PenLine,       color: 'text-blue-300 bg-blue-500/15' },
  { value: 'matching',       label: 'Moslashtirish',          icon: GitMerge,      color: 'text-orange-300 bg-orange-500/15' },
  { value: 'listening',      label: 'Listening',              icon: Headphones,    color: 'text-teal-300 bg-teal-500/15' },
  { value: 'speaking',       label: 'Speaking',               icon: Mic,           color: 'text-rose-300 bg-rose-500/15' },
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
  const [selectedCat, setSelectedCat] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [activeTab, setActiveTab] = useState('vocab');
  const [lessonSearch, setLessonSearch] = useState('');
  const [modal, setModal] = useState(null);
  const [confirm, setConfirm] = useState(null);

  const load = async () => {
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
    return c.data;
  };

  useEffect(() => {
    load()
      .then((cats) => { if (cats.length) setSelectedCat(cats[0]); })
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
    <div className="flex h-[calc(100vh-88px)]">

      {/* ── Panel 1: Categories ── */}
      <div className="w-52 shrink-0 border-r border-inherit flex flex-col admin-panel-alt">
        <div className="px-3 py-3 border-b border-border flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Kategoriya</span>
          <button onClick={() => setModal({ type: 'category' })} className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition" title="Yangi">
            <Plus size={12} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-1">
          {categories.map((cat) => {
            const count = lessons.filter((l) => l.category === cat.id).length;
            const active = selectedCat?.id === cat.id;
            return (
              <div
                key={cat.id}
                onClick={() => { setSelectedCat(cat); setSelectedLesson(null); }}
                className={`group mx-1.5 my-0.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all border admin-cat-item ${
                  active ? 'active' : 'admin-text-body hover:bg-black/5 dark:hover:bg-surface-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  <p className={`text-sm font-medium truncate flex-1 ${active ? 'text-indigo-300' : 'text-slate-300'}`}>{cat.name}</p>
                  <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
                    <button onClick={(e) => { e.stopPropagation(); setModal({ type: 'category', data: cat }); }} className="admin-btn-ghost !p-1"><Pencil size={11} /></button>
                    <button onClick={(e) => { e.stopPropagation(); delCategory(cat); }} className="admin-btn-danger !p-1"><Trash2 size={11} /></button>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">{count} dars</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Panel 2: Lessons list ── */}
      <div className="w-72 shrink-0 border-r border-inherit flex flex-col admin-panel-alt">
        {!selectedCat ? (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-sm p-4 text-center">Kategoriya tanlang</div>
        ) : (
          <>
            <div className="p-3 border-b border-border space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-400">{filteredLessons.length} ta dars</p>
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
                    <p className={`text-sm font-medium truncate ${active ? 'text-white' : 'text-slate-300'}`}>{lesson.title}</p>
                    <p className="text-[10px] text-slate-500 mt-1 flex gap-1.5">
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
      <div className="flex-1 flex flex-col min-w-0 admin-panel">
        {!currentLesson ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-slate-500">
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
                        <span className="text-sm font-semibold text-indigo-300 w-32 shrink-0">{v.word}</span>
                        <span className="text-slate-600">—</span>
                        <span className="text-sm text-slate-300 flex-1">{v.translation}</span>
                        {v.example && <span className="text-xs text-slate-500 italic truncate max-w-xs hidden lg:block">"{v.example}"</span>}
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
                            <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium mb-1.5 ${meta?.color || 'text-slate-400 bg-surface-200'}`}>
                              <Icon size={10} />{meta?.label || ex.type}
                            </span>
                            <p className="text-sm text-slate-300">{ex.instruction}</p>
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
                            <p className="text-sm text-slate-200 font-medium">
                              <span className="text-slate-500 mr-1">{qi + 1}.</span>{q.question}
                            </p>
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              {q.options.map((opt, i) => (
                                <span key={i} className={`text-xs px-2.5 py-1 rounded-lg inline-flex items-center gap-1 ${
                                  i === q.correct_option_index
                                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold'
                                    : 'bg-surface-200 text-slate-400 border border-border'
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
          onConfirm={() => { confirm.onConfirm(); setConfirm(null); }}
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
        <div className="text-center py-16 text-slate-500">
          <p className="text-sm">{empty}</p>
          <button onClick={onAdd} className="mt-3 text-sm text-indigo-400 hover:text-indigo-300">{addLabel}</button>
        </div>
      )}
    </>
  );
}

/* ─────────────────────────────────────────────
   Confirm dialog
───────────────────────────────────────────── */
function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="admin-modal rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-start gap-3 mb-5">
          <div className="p-2 rounded-full bg-red-500/15 shrink-0">
            <AlertTriangle size={20} className="text-red-400" />
          </div>
          <p className="text-slate-300 text-sm leading-relaxed pt-1">{message}</p>
        </div>
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} className="admin-btn-ghost">Bekor qilish</button>
          <button onClick={onConfirm} className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-sm font-medium transition">
            Ha, o'chirish
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Modal wrapper
───────────────────────────────────────────── */
function ModalWrapper({ title, subtitle, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="admin-modal rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col">
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
    title: data?.title ?? '',
    description: data?.description ?? '',
    video_url: data?.video_url ?? '',
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
    if (!form.title.trim()) return setError('Dars nomi majburiy');
    if (!form.video_url.trim()) return setError('Video URL majburiy');
    setError('');
    setSaving(true);
    try {
      const payload = { ...form, level_ids: selectedLevelIds };
      if (isEdit) {
        await api.put(`/courses/lessons/${data.id}/`, payload);
      } else {
        await api.post('/courses/lessons/', payload);
      }
      onSave();
    } catch {
      setError('Saqlashda xatolik yuz berdi');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalWrapper title={isEdit ? 'Darsni tahrirlash' : 'Yangi dars qo\'shish'} onClose={onClose}>
      <div className="space-y-4">
        <Field label="Dars nomi *" value={form.title} onChange={(v) => set('title', v)} placeholder="Masalan: Present Simple" />
        <Field label="YouTube URL *" value={form.video_url} onChange={(v) => set('video_url', v)} placeholder="https://youtu.be/..." />
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
        <div>
          <label className="block text-sm font-medium mb-1">Tavsif</label>
          <textarea
            value={form.description}
            onChange={(e) => set('description', e.target.value)}
            rows={3}
            placeholder="Dars haqida qisqacha ma'lumot..."
            className="admin-input resize-none text-sm"
          />
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
    } catch {
      setError('Saqlashda xatolik yuz berdi');
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
    } catch {
      setError('Saqlashda xatolik yuz berdi');
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
                        ? 'border-green-400 bg-green-50 focus:ring-green-300'
                        : 'border-border focus:ring-indigo-500/40'
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
  const [instruction, setInstruction] = useState(data?.instruction ?? '');
  const [lessonId, setLessonId] = useState(data?.lesson ?? '');
  const [content, setContent] = useState(() => buildDefaultContent(data));
  const [audioUrl, setAudioUrl] = useState(data?.audio_url ?? '');
  const [hasAudio, setHasAudio] = useState(data?.has_audio ?? false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  function buildDefaultContent(d) {
    if (d?.content) return d.content;
    return {
      choose_correct: { sentences: [{ before: '', options: ['', ''], after: '', correct: 0 }] },
      fill_blank:     { sentences: [{ text: '', answer: '' }], word_panel: [] },
      matching:       { left: [''], right: [''], pairs: [0] },
      listening:      { questions: [{ question: '', options: ['', '', '', ''], correct: 0 }] },
      speaking:       { prompt: '' },
    }[d?.type ?? 'choose_correct'] ?? {};
  }

  const switchType = (t) => {
    setType(t);
    setContent({
      choose_correct: { sentences: [{ before: '', options: ['', ''], after: '', correct: 0 }] },
      fill_blank:     { sentences: [{ text: '', answer: '' }], word_panel: [] },
      matching:       { left: [''], right: [''], pairs: [0] },
      listening:      { questions: [{ question: '', options: ['', '', '', ''], correct: 0 }] },
      speaking:       { prompt: '' },
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
    if (!instruction.trim()) return setError('Ko\'rsatma matni majburiy');
    setError(''); setSaving(true);
    try {
      const payload = {
        lesson: Number(lessonId), type, instruction, content,
        has_audio: hasAudio,
        audio_url: audioUrl.trim() || null,
      };
      if (isEdit) {
        await api.put(`/quiz/exercises/${data.id}/`, payload);
      } else {
        await api.post('/quiz/exercises/', payload);
      }
      onSave();
    } catch { setError('Saqlashda xatolik'); }
    finally { setSaving(false); }
  };

  return (
    <ModalWrapper
      title={isEdit ? 'Mashqni tahrirlash' : 'Yangi mashq qo\'shish'}
      onClose={onClose}
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
          <div className="grid grid-cols-3 gap-2">
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
              className="w-full px-4 py-2.5 border border-teal-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm bg-teal-50"
            />
            <p className="text-xs admin-text-muted">MP3 URL yoki YouTube havola kiritish mumkin</p>
          </div>
        )}

        {/* Instruction */}
        <div>
          <label className="block text-sm font-medium mb-1">Ko'rsatma *</label>
          <input
            type="text"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Masalan: To'g'ri so'zni tanlang"
            className="admin-input text-sm"
          />
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
          <ListeningEditor content={content} setContent={setContent} />
        )}
        {type === 'speaking' && (
          <SpeakingEditor content={content} setContent={setContent} />
        )}

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
          <input value={s.answer} onChange={(e) => updateSentence(i, 'answer', e.target.value)} placeholder="To'g'ri javob..." className="w-full px-3 py-2 border border-green-300 bg-green-50 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-green-400" />
          {sentences.length > 1 && <button onClick={() => removeSentence(i)} className="text-xs text-red-400 hover:text-red-600">− O'chirish</button>}
        </div>
      ))}
      <button onClick={addSentence} className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"><Plus size={12} /> Gap qo'shish</button>

      <div>
        <label className="block text-sm font-medium admin-text-body mb-1">So'z paneli (ixtiyoriy)</label>
        <div className="flex flex-wrap gap-1 mb-2">
          {wordPanel.map((w, i) => (
            <span key={i} className="flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-lg">
              {w}
              <button onClick={() => removeWord(i)} className="text-blue-400 hover:text-red-500"><X size={10} /></button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input value={wordInput} onChange={(e) => setWordInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addWord()} placeholder="So'z kiriting, Enter bosing..." className="admin-input-sm flex-1" />
          <button onClick={addWord} className="px-3 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100 transition">+</button>
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
  const updatePair = (i, val) => {
    const p = [...pairs]; p[i] = Number(val);
    setContent({ left, right, pairs: p });
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
function ListeningEditor({ content, setContent }) {
  const questions = content.questions || [];

  const updateQ = (i, key, val) => {
    const qs = questions.map((q, qi) => qi === i ? { ...q, [key]: val } : q);
    setContent({ questions: qs });
  };
  const updateOpt = (i, oi, val) => {
    const qs = questions.map((q, qi) => {
      if (qi !== i) return q;
      const opts = [...q.options]; opts[oi] = val;
      return { ...q, options: opts };
    });
    setContent({ questions: qs });
  };
  const addQuestion = () =>
    setContent({ questions: [...questions, { question: '', options: ['', '', '', ''], correct: 0 }] });
  const removeQuestion = (i) =>
    setContent({ questions: questions.filter((_, qi) => qi !== i) });

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">Tinglash savollari</label>
      {questions.map((q, i) => (
        <div key={i} className="border border-teal-200 rounded-xl p-3 space-y-2 bg-teal-50/40">
          <input
            value={q.question}
            onChange={(e) => updateQ(i, 'question', e.target.value)}
            placeholder={`${i + 1}-savol matni`}
            className="admin-input-sm w-full"
          />
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
        className="w-full px-3 py-2.5 border border-rose-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-rose-300 resize-none text-sm bg-rose-50/30"
      />
      <p className="text-xs admin-text-muted">O'quvchi bu topshiriqni o'qib, audio yozib yuborishi kerak</p>
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
    translation: data?.translation ?? '',
    example: data?.example ?? '',
    order: data?.order ?? 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSave = async () => {
    if (!form.lesson) return setError('Darsni tanlang');
    if (!form.word.trim()) return setError("Inglizcha so'z majburiy");
    if (!form.translation.trim()) return setError("O'zbekcha tarjima majburiy");
    setError(''); setSaving(true);
    try {
      if (isEdit) {
        await api.put(`/courses/vocabulary/${data.id}/`, form);
      } else {
        await api.post('/courses/vocabulary/', form);
      }
      onSave();
    } catch { setError('Saqlashda xatolik'); }
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
        <div className="grid grid-cols-2 gap-3">
          <Field label="Inglizcha *" value={form.word} onChange={(v) => set('word', v)} placeholder="e.g. beautiful" />
          <Field label="O'zbekcha *" value={form.translation} onChange={(v) => set('translation', v)} placeholder="e.g. chiroyli" />
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
