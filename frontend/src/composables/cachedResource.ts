import { computed, ref, shallowRef, type ComputedRef, type Ref } from 'vue';

// ---------------------------------------------------------------------------
// useCachedResource
// ---------------------------------------------------------------------------
//
// Stale-while-revalidate (SWR) helper with **multi-key** caching.
//
// The cache stores one payload per resource key (e.g. one per `seasonId`,
// one per `year`, …). Switching back to a previously loaded key is
// therefore instant — the cached data is shown immediately and a background
// refresh is kicked off.
//
//   - `loading` is true only until we have the FIRST payload for the
//     currently requested key (blocking spinner). If cached data already
//     exists for that key, the fetch runs in the background and
//     `refreshing` is flipped instead — the UI keeps showing the cached
//     data.
//   - `data` always reflects the payload for the currently requested key
//     (or `null` if that key has never been loaded).
//   - `loadedKey` remembers which key produced the currently visible
//     `data`.
//
// Usage:
//   const { data, loading, refreshing, load, reset } = useCachedResource(
//     (seasonId: number) => api.get(`/season/${seasonId}/…`).then(r => r.data),
//     { cacheKey: 'season-standings' }
//   );
//   watch(() => props.seasonId, id => id && load(id), { immediate: true });
// ---------------------------------------------------------------------------

export interface UseCachedResourceOptions {
  /**
   * When `true`, keep previous data on error instead of clearing it.
   * Defaults to `true` (aligns with SWR semantics).
   */
  keepDataOnError?: boolean;
  /** Optional error hook. */
  onError?: (err: unknown) => void;
  /**
   * Optional cache key. When provided, the reactive state (per-resource-key
   * entries, `currentKey`, `refreshing`) is stored in a module-level
   * registry and shared across every `useCachedResource` call using the
   * same `cacheKey`.
   *
   * This makes the cache survive component unmount/remount — e.g. when the
   * user navigates away from a page and back. Without it, each call creates
   * fresh refs, so any component-local cache is thrown away on unmount and
   * the blocking spinner reappears on the next visit.
   */
  cacheKey?: string;
}

interface CachedResourceState<K, T> {
  // One entry per resource key — this is what makes switching between
  // already-loaded keys (e.g. seasons) instant.
  entries: Ref<Map<K, T>>;
  // The key that consumers are currently interested in.
  currentKey: Ref<K | null>;
  refreshing: Ref<boolean>;
  // In-flight loads, keyed by resource key, so concurrent load() calls for
  // the same key don't fan out into duplicate requests.
  inflight: Map<K, Promise<T | null>>;
}

// Module-level registry keyed by `cacheKey`. Any two `useCachedResource` calls
// with the same key share the exact same reactive state, so the cache
// survives component unmount/remount and route navigation.
const registry = new Map<string, CachedResourceState<unknown, unknown>>();

function createState<K, T>(): CachedResourceState<K, T> {
  return {
    entries: shallowRef(new Map<K, T>()) as Ref<Map<K, T>>,
    currentKey: ref(null) as Ref<K | null>,
    refreshing: ref(false),
    inflight: new Map<K, Promise<T | null>>(),
  };
}

export function useCachedResource<K, T>(
  loader: (key: K) => Promise<T>,
  options: UseCachedResourceOptions = {}
) {
  const { keepDataOnError = true, onError, cacheKey } = options;

  let state: CachedResourceState<K, T>;
  if (cacheKey) {
    const existing = registry.get(cacheKey) as
      | CachedResourceState<K, T>
      | undefined;
    if (existing) {
      state = existing;
    } else {
      state = createState<K, T>();
      registry.set(cacheKey, state as CachedResourceState<unknown, unknown>);
    }
  } else {
    state = createState<K, T>();
  }

  const { entries, currentKey, refreshing } = state;

  // `data` always reflects the payload for the currently requested key.
  const data: ComputedRef<T | null> = computed(() => {
    const key = currentKey.value;
    if (key === null) return null;
    return entries.value.get(key) ?? null;
  });

  // Blocking spinner: only true while we don't yet have data for the
  // current key AND a fetch for it is in flight.
  const loading: ComputedRef<boolean> = computed(() => {
    const key = currentKey.value;
    if (key === null) return false;
    if (entries.value.has(key)) return false;
    return state.inflight.has(key);
  });

  // Kept for API compatibility. Equals `currentKey` iff we have cached
  // data for it, otherwise `null`.
  const loadedKey: ComputedRef<K | null> = computed(() => {
    const key = currentKey.value;
    if (key === null) return null;
    return entries.value.has(key) ? key : null;
  });

  function commitEntry(key: K, value: T): void {
    // Replace the Map so shallowRef reactivity kicks in.
    const next = new Map(entries.value);
    next.set(key, value);
    entries.value = next;
  }

  function deleteEntry(key: K): void {
    if (!entries.value.has(key)) return;
    const next = new Map(entries.value);
    next.delete(key);
    entries.value = next;
  }

  async function load(key: K): Promise<T | null> {
    // Mark this key as the one consumers care about — `data`, `loading`
    // and `loadedKey` immediately reflect the cached value (if any).
    currentKey.value = key;

    // Coalesce concurrent load() calls for the same key.
    const existing = state.inflight.get(key);
    if (existing) return existing;

    // Stale-while-revalidate: if we already have data for THIS key cached,
    // keep it on screen and refresh in the background. Otherwise the
    // blocking `loading` flag flips on automatically (it's a computed
    // derived from `entries` + `inflight`).
    const isBackground = entries.value.has(key);
    if (isBackground) {
      refreshing.value = true;
    }

    const promise = (async () => {
      try {
        const result = await loader(key);
        commitEntry(key, result);
        return result;
      } catch (e) {
        if (!keepDataOnError) {
          deleteEntry(key);
        }
        if (onError) onError(e);
        else console.error('useCachedResource: load failed', e);
        return null;
      } finally {
        state.inflight.delete(key);
        if (isBackground && state.inflight.size === 0) {
          refreshing.value = false;
        }
      }
    })();
    state.inflight.set(key, promise);
    return promise;
  }

  function reset(): void {
    entries.value = new Map<K, T>();
    currentKey.value = null;
    refreshing.value = false;
  }

  return {
    data,
    loading,
    refreshing,
    loadedKey,
    load,
    reset,
  };
}
