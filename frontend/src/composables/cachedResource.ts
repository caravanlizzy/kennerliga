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
}

export function useCachedResource<K, T>(
  loader: (key: K) => Promise<T>,
  options: UseCachedResourceOptions = {}
) {
  const { keepDataOnError = true, onError } = options;

  const data = shallowRef<T | null>(null);
  const loading = ref(false);
  const refreshing = ref(false);
  const loadedKey: Ref<K | null> = ref(null) as Ref<K | null>;

  async function load(key: K): Promise<T | null> {
    // Stale-while-revalidate: if we already have data for THIS key cached,
    // keep it on screen and refresh in the background. When switching to a
    // different key (or on the very first load) we show the blocking
    // spinner because the cached data belongs to a different key.
    const isBackground = loadedKey.value !== null && loadedKey.value === key;
    const flag = isBackground ? refreshing : loading;
    flag.value = true;
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
    }
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
