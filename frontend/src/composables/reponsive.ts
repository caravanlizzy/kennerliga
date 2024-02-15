import { useQuasar } from 'quasar';

type TResponsive = {
  iconSize: 'md|lg';
  isMobile: boolean;
  buttonMargin: string|undefined;
}

export function useResponsive() {
  const $q = useQuasar();
  const isMobile: boolean|undefined = $q.platform.is.mobile;
  const iconSize = isMobile ? 'md' : 'lg';
  const buttonMargin = isMobile && '0 4px';
  return { iconSize, isMobile , buttonMargin };
}
