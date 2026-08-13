/**
 * Shared helpers for normalizing API responses across services.
 * Keeps response-shape handling (paginated vs. plain arrays) in one place
 * instead of repeating `Array.isArray(data) ? data : data?.results || []`.
 */
export type PaginatedResponse<T> = {
  results: T[];
};

export function unwrapList<T>(
  data: T[] | PaginatedResponse<T> | null | undefined
): T[] {
  if (Array.isArray(data)) return data;
  return data?.results ?? [];
}
