// Búsqueda lineal
export function linearSearch<T>(
  array: T[],
  predicate: (item: T) => boolean
): T | undefined {
  return array.find(predicate);
}

// Búsqueda binaria (requiere ordenado)
export function binarySearch(
  array: number[],
  target: number
): number | undefined {
  let left = 0;
  let right = array.length - 1;

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const midValue = array[mid];

    if (midValue === undefined) return undefined;

    if (midValue === target) return midValue;

    if (midValue < target) left = mid + 1;
    else right = mid - 1;
  }

  return undefined;
}