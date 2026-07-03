import { ref, shallowRef, type Ref } from 'vue';

// ---------------------------------------------------------------------------
// useCachedResource
// ---------------------------------------------------------------------------
//
// Small stale-while-revalidate (SWR) helper mirroring the pattern that was
// introduced in `components/season/SeasonStandings.vue` after the "spinner
// on cached data" bug:
//
//   - `loading` is true only until we have the FIRST payload for the
//     current key (blocking spinner). If we already have cached data for
//     the same key, the fetch runs in the background and `refreshing`
//     is flipped instead — the UI keeps showing the cached data.
//   - `loadedKey` remembers which key produced the cached `data`.
//
// This makes the class of bug we fixed structurally impossible.
//
// Usage:
//   const { data, loading, refreshing, load, reset } = useCachedResource(
//     (seasonId: number) => api.get(`/season/${seasonId}/…`).then(r => r.data)
//   );
//   watch(() => props.seasonId, id => id ? load(id) : reset(), { immediate: true });
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
   * Optional cache key. When provided, the reactive state (`data`, `loading`,
   * `refreshing`, `loadedKey`) is stored in a module-level registry and shared
   * across every `useCachedResource` call using the same `cacheKey`.
   *
   * This makes the cache survive component unmount/remount — e.g. when the
   * user navigates away from a page and back. Without it, each call creates
   * fresh refs, so any component-local cache is thrown away on unmount and
   * the blocking spinner reappears on the next visit.
   */
  cacheKey?: string;
}

interface CachedResourceState<K, T> {
  data: Ref<T | null>;
  loading: Ref<boolean>;
  refreshing: Ref<boolean>;
  loadedKey: Ref<K | null>;
  inflight: Promise<T | null> | null;
}

// Module-level registry keyed by `cacheKey`. Any two `useCachedResource` calls
// with the same key share the exact same reactive state, so the cache
// survives component unmount/remount and route navigation.
const registry = new Map<string, CachedResourceState<unknown, unknown>>();

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
      state = {
        data: shallowRef<T | null>(null),
        loading: ref(false),
        refreshing: ref(false),
        loadedKey: ref(null) as Ref<K | null>,
        inflight: null,
      };
      registry.set(cacheKey, state as CachedResourceState<unknown, unknown>);
    }
  } else {
    state = {
      data: shallowRef<T | null>(null),
      loading: ref(false),
      refreshing: ref(false),
      loadedKey: ref(null) as Ref<K | null>,
      inflight: null,
    };
  }

  const { data, loading, refreshing, loadedKey } = state;

  async function load(key: K): Promise<T | null> {
    // Coalesce concurrent load() calls for the same key so we don't fire
    // duplicate requests when several consumers (or a re-mount) trigger a
    // fetch in the same tick.
    if (state.inflight && loadedKey.value === key) {
      return state.inflight;
    }
    // Stale-while-revalidate: if we already have data for THIS key cached,
    // keep it on screen and refresh in the background. When switching to a
    // different key (or on the very first load) we show the blocking
    // spinner because the cached data belongs to a different key.
    const isBackground = loadedKey.value !== null && loadedKey.value === key;
    const flag = isBackground ? refreshing : loading;
    flag.value = true;
    const promise = (async () => {
      try {
        const result = await loader(key);
        data.value = result;
        loadedKey.value = key;
        return result;
      } catch (e) {
        if (!keepDataOnError) {
          data.value = null;
          loadedKey.value = null;
        }
        if (onError) onError(e);
        else console.error('useCachedResource: load failed', e);
        return null;
      } finally {
        flag.value = false;
        state.inflight = null;
      }
    })();
    state.inflight = promise;
    return promise;
  }

  function reset(): void {
    data.value = null;
    loadedKey.value = null;
    loading.value = false;
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
