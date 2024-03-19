import { useQuasar } from 'quasar';

export function useResponsive() {
  const $q = useQuasar();
  const isMobile: boolean|undefined = $q.platform.is.mobile;
  const buttonMargin = isMobile && '0 4px';
  return { isMobile , buttonMargin };
}
