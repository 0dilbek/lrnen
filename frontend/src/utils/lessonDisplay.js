/** O'quvchiga ko'rsatish uchun dars sarlavhasini tozalash */
export function formatLessonTitle(title = '') {
  return title
    .replace(/^\[Book\s*\d+[^\]]*\]\s*/i, '')
    .replace(/^Unit\s*\d+\s*[—–-]\s*/i, '')
    .trim() || title;
}

export function formatLessonDescription(desc = '') {
  if (!desc) return '';
  if (/DK English|Level \d/i.test(desc)) return '';
  return desc;
}

export function getUnitNumber(title = '') {
  const m = title.match(/Unit\s*(\d+)/i);
  return m ? parseInt(m[1], 10) : null;
}