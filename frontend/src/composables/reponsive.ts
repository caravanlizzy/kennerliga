import { computed, type Ref } from 'vue'
import { useQuasar } from 'quasar'

/**
 * useResponsive
 * - smallScreen: reactive "screen below breakpoint" flag (default 'md')
 * - isMobile: platform/mobile (kept for compatibility with your existing code)
 * - buttonMargin: your original helper (now computed)
 *
 * Pass an optional reactive breakpoint ref if you want to control it from props.
 */
export function useResponsive(breakpoint?: Ref<'xs' | 'sm' | 'md' | 'lg' | 'xl'>) {
  const $q = useQuasar()

  // Keeps your original platform flag
  const isMobile: boolean | undefined = $q.platform.is.mobile

  // New: "smallScreen" based on screen breakpoint (separate from platform)
  const smallScreen = computed(() => {
    const bp = breakpoint?.value ?? 'md'
    return ($q.screen as any).lt[bp]
  })

  // Your original helper, but reactive
  const buttonMargin = computed(() => (isMobile ? '0 4px' : undefined))

  // A couple of convenient extras (optional to use)
  const isTouch = computed(() => !!($q.platform.has.touch))
  const screenName = computed(() => $q.screen.name as 'xs'|'sm'|'md'|'lg'|'xl')

  return {
    isMobile,
    buttonMargin,
    smallScreen,
    isTouch,
    screenName
  }
}
