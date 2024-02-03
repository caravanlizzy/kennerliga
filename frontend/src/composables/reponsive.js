import { useQuasar } from 'quasar';

export function useResponsive(){
  const $q = useQuasar();
  const isMobile = $q.platform.is.mobile;
  const iconSize = isMobile ? 'md' : 'lg';
  const buttonMargin = isMobile && '0 4px';
  return { iconSize, isMobile , buttonMargin };
}
