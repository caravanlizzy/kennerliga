import { useQuasar } from 'quasar';

type TResponsive = {
  isMobile: boolean;
  buttonMargin: string|undefined;
}

export function useResponsive() {
  const $q = useQuasar();
  const isMobile: boolean|undefined = $q.platform.is.mobile;
  const buttonMargin = isMobile && '0 4px';
  return { isMobile , buttonMargin };
}
