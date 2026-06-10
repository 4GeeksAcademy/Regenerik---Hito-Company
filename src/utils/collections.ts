// Filtrar
export function filterBy<T>(array: T[], predicate: (item: T) => boolean): T[] {
  if (!array.length) return [];
  return array.filter(predicate);
}

// Ordenar
export function sortBy<T>(
  array: T[],
  compareFn: (a: T, b: T) => number
): T[] {
  return [...array].sort(compareFn);
}

// Agrupar
export function groupBy<T, K extends string | number>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  return array.reduce((acc, item) => {
    const key = keyFn(item);
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<K, T[]>);
}