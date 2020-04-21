export function samePositions(a, b) {
  if (a === undefined || b === undefined) {
    return false;
  }

  return a[0] === b[0] && a[1] === b[1];
}