import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, Loader2, Plus, Users, Pencil, Trash2, Search, X, Save, LockKeyhole } from 'lucide-react';
import api, { getApiErrorMessage } from '../../api';
import { useLanguage } from '../../context/LanguageContext';

export default function AdminGroups() {
  const { t } = useLanguage();
  const [groups, setGroups] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);
  const [membersOpen, setMembersOpen] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    Promise.all([api.get('/auth/student-groups/'), api.get('/auth/students/')])
      .then(([groupResponse, studentResponse]) => {
        if (!active) return;
        setGroups(groupResponse.data);
        setStudents(studentResponse.data);
        setSelectedId((current) => groupResponse.data.some((group) => group.id === current)
          ? current : groupResponse.data[0]?.id || null);
        setError('');
      })
      .catch((requestError) => { if (active) setError(getApiErrorMessage(requestError)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [refreshKey]);

  const selectedGroup = groups.find((group) => group.id === selectedId);
  const members = students.filter((student) => student.group?.id === selectedId);

  const remove = async (group) => {
    if (!window.confirm(t('“{name}” guruhi o‘chirilsinmi? O‘quvchilar va ularning natijalari saqlanadi.', { name: group.name }))) return;
    setDeletingId(group.id);
    setError('');
    try {
      await api.delete(`/auth/student-groups/${group.id}/`);
      setRefreshKey((current) => current + 1);
    } catch (requestError) { setError(getApiErrorMessage(requestError)); }
    finally { setDeletingId(null); }
  };

  return (
    <div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black admin-text-title">{t('Guruhlar')}</h1>
          <p className="mt-1 max-w-2xl text-sm admin-text-muted">{t('O‘quvchilarni guruhlang va har bir guruh uchun darslarni alohida oching.')}</p>
        </div>
        <button type="button" onClick={() => setEditing({})} className="admin-btn-primary"><Plus size={18} /> {t('Guruh qo‘shish')}</button>
      </div>
      {error && <p role="alert" className="mb-5 rounded-xl bg-red-500/10 p-4 text-sm text-red-600 dark:text-red-300">{error}</p>}
      {loading ? <Loader2 className="mx-auto my-20 animate-spin text-indigo-500" size={32} /> : groups.length === 0 ? (
        <div className="admin-card px-6 py-16 text-center">
          <Users size={42} className="mx-auto mb-4 text-indigo-400" />
          <h2 className="text-lg font-bold admin-text-title">{t('Hali guruhlar yo‘q')}</h2>
          <p className="mx-auto mt-2 max-w-md text-sm admin-text-muted">{t('Birinchi guruhni yarating, o‘quvchilarni biriktiring va ochilgan darsni tanlang.')}</p>
        </div>
      ) : (
        <div className="grid items-start gap-5 lg:grid-cols-[260px_1fr]">
          <div className="flex gap-2 overflow-x-auto pb-2 lg:block lg:space-y-2">
            {groups.map((group) => (
              <button key={group.id} type="button" onClick={() => setSelectedId(group.id)} className={`flex min-w-48 shrink-0 items-center gap-3 rounded-2xl border p-4 text-left transition lg:w-full ${selectedId === group.id ? 'border-indigo-500 bg-indigo-500/10' : 'border-border bg-surface-100 hover:border-indigo-500/40'}`}>
                <span className="rounded-xl bg-indigo-500/15 p-2 text-indigo-500"><Users size={18} /></span>
                <span className="min-w-0"><span className="block truncate font-bold admin-text-title">{group.name}</span><span className="text-xs admin-text-muted">{group.student_count} {t('o‘quvchi')}</span></span>
              </button>
            ))}
          </div>
          {selectedGroup && (
            <div className="min-w-0 space-y-5">
              <section className="admin-card p-5 sm:p-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div><h2 className="text-xl font-black admin-text-title">{selectedGroup.name}</h2><p className="mt-1 text-sm admin-text-muted">{members.length} {t('o‘quvchi')}</p></div>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => setEditing(selectedGroup)} className="admin-btn-ghost !p-2" aria-label={t('Guruh nomini tahrirlash')}><Pencil size={17} /></button>
                    <button type="button" onClick={() => remove(selectedGroup)} disabled={deletingId === selectedGroup.id} className="admin-btn-danger !p-2" aria-label={t('Guruhni o‘chirish')}>{deletingId === selectedGroup.id ? <Loader2 size={17} className="animate-spin" /> : <Trash2 size={17} />}</button>
                    <button type="button" onClick={() => setMembersOpen(true)} className="admin-btn-primary !text-xs"><Users size={15} /> {t('O‘quvchilarni tanlash')}</button>
                  </div>
                </div>
                <div className="mt-4 flex max-h-48 flex-wrap gap-2 overflow-y-auto">
                  {members.length ? members.map((student) => <Link key={student.id} to={`/admin/students/${student.id}`} className="rounded-lg border border-border bg-surface-200/60 px-3 py-1.5 text-xs font-semibold admin-text-body hover:border-indigo-400">{student.full_name || student.username}</Link>) : <p className="text-sm admin-text-muted">{t('Bu guruhga hali o‘quvchi biriktirilmagan.')}</p>}
                </div>
              </section>
              <GroupLessonRelease key={selectedGroup.id} group={selectedGroup} />
            </div>
          )}
        </div>
      )}
      {editing && <GroupNameModal group={editing} onClose={() => setEditing(null)} onSaved={(group) => { setSelectedId(group.id); setRefreshKey((current) => current + 1); setEditing(null); }} />}
      {membersOpen && selectedGroup && <GroupMembersModal group={selectedGroup} students={students} onClose={() => setMembersOpen(false)} onSaved={() => { setMembersOpen(false); setRefreshKey((current) => current + 1); }} />}
    </div>
  );
}

function GroupModal({ title, onClose, children }) {
  const { t } = useLanguage();
  useEffect(() => {
    const handleKey = (event) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/65 p-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="group-modal-title">
      <button type="button" onClick={onClose} className="absolute inset-0" aria-label={t('Yopish')} />
      <div className="admin-card relative flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden rounded-2xl shadow-2xl">
        <div className="flex items-center justify-between border-b border-border p-5"><h2 id="group-modal-title" className="text-lg font-black admin-text-title">{title}</h2><button type="button" onClick={onClose} aria-label={t('Yopish')} className="admin-text-muted"><X size={20} /></button></div>
        {children}
      </div>
    </div>
  );
}

function GroupNameModal({ group, onClose, onSaved }) {
  const { t } = useLanguage();
  const [name, setName] = useState(group.name || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const save = async (event) => {
    event.preventDefault();
    setSaving(true); setError('');
    try {
      const { data } = group.id ? await api.patch(`/auth/student-groups/${group.id}/`, { name: name.trim() }) : await api.post('/auth/student-groups/', { name: name.trim() });
      onSaved(data);
    } catch (requestError) { setError(getApiErrorMessage(requestError)); }
    finally { setSaving(false); }
  };
  return <GroupModal title={t(group.id ? 'Guruh nomini tahrirlash' : 'Guruh qo‘shish')} onClose={onClose}><form onSubmit={save} className="space-y-4 p-5"><label className="block text-sm font-semibold admin-text-body">{t('Guruh nomi')}<input autoFocus value={name} onChange={(event) => setName(event.target.value)} required maxLength={100} placeholder={t('Masalan: 1-guruh')} className="admin-input mt-2" /></label>{error && <p role="alert" className="text-sm text-red-500">{error}</p>}<button type="submit" disabled={saving || !name.trim()} className="admin-btn-primary w-full justify-center disabled:opacity-50">{saving ? <Loader2 size={17} className="animate-spin" /> : <Save size={17} />}{t('Saqlash')}</button></form></GroupModal>;
}

function GroupMembersModal({ group, students, onClose, onSaved }) {
  const { t } = useLanguage();
  const [selected, setSelected] = useState(() => new Set(students.filter((student) => student.group?.id === group.id).map((student) => student.id)));
  const [query, setQuery] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const filtered = students.filter((student) => `${student.full_name} ${student.username}`.toLowerCase().includes(query.toLowerCase()));
  const movedCount = students.filter((student) => selected.has(student.id) && student.group && student.group.id !== group.id).length;
  const toggle = (id) => setSelected((current) => { const next = new Set(current); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  const save = async () => {
    setSaving(true); setError('');
    try { await api.patch(`/auth/student-groups/${group.id}/`, { student_ids: [...selected] }); onSaved(); }
    catch (requestError) { setError(getApiErrorMessage(requestError)); }
    finally { setSaving(false); }
  };
  return (
    <GroupModal title={`${group.name} · ${t('O‘quvchilarni tanlash')}`} onClose={onClose}>
      <div className="border-b border-border p-4"><div className="relative"><Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 admin-text-muted" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('Ism yoki login bo‘yicha qidirish')} className="admin-input !pl-9" /></div><p className="mt-2 text-xs admin-text-muted">{selected.size} {t('tanlandi')}</p></div>
      <div className="min-h-0 flex-1 space-y-1 overflow-y-auto p-3">
        {filtered.map((student) => <label key={student.id} className="flex cursor-pointer items-center gap-3 rounded-xl p-3 hover:bg-surface-200"><input type="checkbox" checked={selected.has(student.id)} onChange={() => toggle(student.id)} className="h-4 w-4 accent-indigo-600" /><span className="min-w-0 flex-1"><span className="block truncate text-sm font-bold admin-text-title">{student.full_name || student.username}</span><span className="block text-xs admin-text-muted">@{student.username} · {student.group?.name || t('Guruhsiz')}</span><span className="mt-1 block text-[11px] admin-text-muted">{student.levels?.map((level) => level.name).join(', ')}</span></span></label>)}
        {!filtered.length && <p className="py-10 text-center text-sm admin-text-muted">{t('O‘quvchilar topilmadi')}</p>}
      </div>
      <div className="space-y-3 border-t border-border p-4">
        {movedCount > 0 && <p className="rounded-xl bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">{t('{count} o‘quvchi avvalgi guruhidan shu guruhga ko‘chiriladi.', { count: movedCount })}</p>}
        {error && <p role="alert" className="text-sm text-red-500">{error}</p>}
        <button type="button" onClick={save} disabled={saving} className="admin-btn-primary w-full justify-center">{saving ? <Loader2 size={17} className="animate-spin" /> : <Save size={17} />}{t('Saqlash')}</button>
      </div>
    </GroupModal>
  );
}

function GroupLessonRelease({ group }) {
  const { language, t } = useLanguage();
  const [levels, setLevels] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api.get(`/courses/lesson-release-settings/?group_id=${group.id}`)
      .then(({ data }) => { if (!active) return; setLevels(data); const first = data.find((level) => level.lessons.length) || data[0]; setActiveId(first?.id); setSelectedId(first?.current_lesson_id || null); })
      .catch((requestError) => { if (active) setError(getApiErrorMessage(requestError)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [group.id, language]);
  const currentLevel = levels.find((level) => level.id === activeId);
  const selectedIndex = currentLevel?.lessons.findIndex((lesson) => lesson.id === selectedId) ?? -1;
  const currentIndex = currentLevel?.lessons.findIndex((lesson) => lesson.id === currentLevel.current_lesson_id) ?? -1;
  const save = async () => {
    setSaving(true); setSaved(false); setError('');
    try {
      const { data } = await api.patch('/courses/lesson-release-settings/', { group_id: group.id, level_id: activeId, current_lesson_id: selectedId });
      setLevels((current) => current.map((level) => level.id === data.id ? data : level)); setSaved(true);
    } catch (requestError) { setError(getApiErrorMessage(requestError)); }
    finally { setSaving(false); }
  };
  return (
    <section className="admin-card overflow-hidden">
      <div className="border-b border-border p-5 sm:p-6"><h2 className="flex items-center gap-2 text-lg font-black admin-text-title"><LockKeyhole size={19} className="text-indigo-500" />{t('Guruhning ochilgan darslari')}</h2><p className="mt-2 text-sm admin-text-muted">{t('Har bir daraja uchun joriy darsni tanlang. Keyingi mavzular shu guruh uchun yopiq bo‘ladi.')}</p><p className="mt-1 text-xs admin-text-muted">{t('Yangi guruhda standart holat — 1-dars. Oldingi testdan 60% olish talabi saqlanadi.')}</p></div>
      {loading ? <Loader2 size={28} className="mx-auto my-14 animate-spin text-indigo-500" /> : <>
        <div className="flex gap-2 overflow-x-auto border-b border-border px-5 py-3" role="tablist" aria-label={t('Darajalar')}>
          {levels.map((level) => <button key={level.id} type="button" role="tab" aria-selected={level.id === activeId} disabled={saving} onClick={() => { setActiveId(level.id); setSelectedId(level.current_lesson_id); setSaved(false); setError(''); }} className={`shrink-0 rounded-xl px-4 py-2 text-sm font-bold ${level.id === activeId ? 'bg-indigo-600 text-white' : 'bg-surface-200 admin-text-muted'}`}>{level.slug.toUpperCase()}</button>)}
        </div>
        <div className="p-4 sm:p-5">
          {currentLevel?.lessons.length ? <>
            <p className="mb-3 text-sm font-semibold admin-text-body">{t('Hozir ochiq: {count}-darsgacha', { count: currentIndex + 1 })}</p>
            <div className="grid max-h-[460px] gap-2 overflow-y-auto pr-1 sm:grid-cols-2">
              {currentLevel.lessons.map((lesson, index) => <button key={lesson.id} type="button" disabled={saving} onClick={() => { setSelectedId(lesson.id); setSaved(false); }} className={`flex items-center gap-3 rounded-xl border p-3 text-left transition ${selectedId === lesson.id ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/15' : 'border-border hover:border-indigo-400'}`}><span className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg text-sm font-black ${selectedId === lesson.id ? 'bg-indigo-600 text-white' : index <= selectedIndex ? 'bg-emerald-500/15 text-emerald-600' : 'bg-surface-200 admin-text-muted'}`}>{selectedId === lesson.id ? <Check size={17} /> : index + 1}</span><span className="min-w-0"><span className="block text-[10px] font-bold admin-text-muted">{index + 1}-{t('dars')}</span><span className="block truncate text-sm font-semibold admin-text-title">{lesson.title}</span></span></button>)}
            </div>
          </> : <p className="py-10 text-center text-sm admin-text-muted">{t('Bu darajaga hali dars biriktirilmagan.')}</p>}
          {error && <p role="alert" className="mt-3 text-sm text-red-500">{error}</p>}
        </div>
        <div className="flex items-center justify-between gap-3 border-t border-border p-4 sm:px-5"><p role="status" className="text-xs text-emerald-600 dark:text-emerald-300">{saved ? t('Saqlandi!') : ''}</p><button type="button" onClick={save} disabled={saving || !selectedId || selectedId === currentLevel?.current_lesson_id} className="admin-btn-primary disabled:opacity-50">{saving ? <Loader2 size={17} className="animate-spin" /> : <Save size={17} />}{t('Saqlash')}</button></div>
      </>}
    </section>
  );
}
