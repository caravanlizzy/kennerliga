import { ref, shallowRef, type Ref, type ShallowRef } from 'vue';

/**
 * Minimal one-shot loader for a service call.
 *
 * Fills the same role `useAxios` from `@vueuse/integrations` used to, but
 * takes a plain promise factory instead of a URL plus an Axios instance —
 * so pages fetch through `src/services/*` like everything else and stay
 * unaware of the transport.
 *
 * The request starts immediately, exactly as `useAxios` did.
 */
export function useAsyncData<T>(
  loader: () => Promise<T>,
  initial: T
): {
  data: ShallowRef<T>;
  isFinished: Ref<boolean>;
  error: ShallowRef<Error | null>;
  reload: () => Promise<void>;
} {
  const data = shallowRef<T>(initial) as ShallowRef<T>;
  const isFinished = ref(false);
  const error = shallowRef<Error | null>(null);

  async function reload(): Promise<void> {
    isFinished.value = false;
    error.value = null;
    try {
      data.value = await loader();
    } catch (e) {
      error.value = e instanceof Error ? e : new Error(String(e));
    } finally {
      isFinished.value = true;
    }
  }

  void reload();

  return { data, isFinished, error, reload };
}
