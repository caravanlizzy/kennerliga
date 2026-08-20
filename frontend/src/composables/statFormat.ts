/**
 * Shared value formatting for the statistics dashboard, so the ranking
 * cards and the per-game leaderboard table render numbers the same way.
 */
export function formatStatValue(
  key: string,
  unit: string,
  value: number | null | undefined
): string {
  if (value === null || value === undefined) return '-';
  if (key === 'best_league_level') return `L${value}`;
  if (unit === '%') return `${value.toFixed(1)}%`;
  if (Number.isInteger(value)) return `${value}${unit ? ` ${unit}` : ''}`;
  return `${value.toFixed(2)}${unit ? ` ${unit}` : ''}`;
}
