// Suma
export function sum(array: number[]): number {
  return array.reduce((acc, val) => acc + val, 0);
}

// Promedio
export function average(array: number[]): number {
  if (!array.length) return 0;
  return sum(array) / array.length;
}

// Máximo
export function max(array: number[]): number {
  return Math.max(...array);
}

// Conteo
export function countBy<T>(
  array: T[],
  keyFn: (item: T) => string
): Record<string, number> {
  return array.reduce((acc, item) => {
    const key = keyFn(item);
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
}