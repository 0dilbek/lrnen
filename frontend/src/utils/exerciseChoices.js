export function shuffledIndices(values) {
  const indices = values.map((_, index) => index);
  for (let index = indices.length - 1; index > 0; index -= 1) {
    const next = Math.floor(Math.random() * (index + 1));
    [indices[index], indices[next]] = [indices[next], indices[index]];
  }
  return indices;
}

export function correctIndices(row) {
  if (Array.isArray(row.correct_indices)) return [...new Set(row.correct_indices)];
  return [row.correct ?? row.correct_index ?? 0];
}

export function isMultipleChoice(row) {
  return Array.isArray(row.correct_indices);
}

export function answerMatches(row, answer) {
  const expected = correctIndices(row).sort((a, b) => a - b);
  const selected = [...new Set(Array.isArray(answer) ? answer : answer === undefined ? [] : [answer])]
    .sort((a, b) => a - b);
  return expected.length === selected.length && expected.every((value, index) => value === selected[index]);
}

export function exampleCountFor(content, count) {
  const configured = content?.example_count;
  return Number.isInteger(configured)
    ? Math.max(0, Math.min(configured, count))
    : count >= 2 ? 1 : 0;
}
