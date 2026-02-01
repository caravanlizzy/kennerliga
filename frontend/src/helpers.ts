import { api } from 'boot/axios';

export function createRandomId(power = 10) {
  return Math.floor(Math.random() * 10 ** power);
}

export function formatDateTime(dateTime: string): string {
  const date = new Date(dateTime);
  return date.toLocaleString('de-DE', {
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: false,  // Use 12-hour format. Set to false for 24-hour format
  })
}

export function loadToken(): void {
  const userStore = JSON.parse(<string>localStorage.getItem('userStore'));
  if(!userStore) return;
  if(userStore.isAuthenticated){
    const token = userStore.user.token;
    if (token) {
      api.defaults.headers['Authorization'] = 'Token ' + token;
    }
  }
}

export function truncateString(input: string, maxLength = 17): string {
  if (input.length <= maxLength) {
    return input;
  }
  return input.substring(0, maxLength) + '...';
}

export function formatNumbers(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '';
  return num.toString();
}

/**
 * Decodes common HTML entities like &quot;, &amp;, &lt;, &gt;, &#39;, and others.
 * Use this to display strings that might have been escaped on the backend.
 */
export function decodeHtmlEntities(text: string | null | undefined): string {
  if (!text) return '';
  const entities: Record<string, string> = {
    '&quot;': '"',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&#39;': "'",
    '&apos;': "'",
    '&Auml;': 'Ä',
    '&auml;': 'ä',
    '&Ouml;': 'Ö',
    '&ouml;': 'ö',
    '&Uuml;': 'Ü',
    '&uuml;': 'ü',
    '&szlig;': 'ß',
    '&nbsp;': ' ',
  };
  return text.replace(/&[a-zA-Z0-9#]+;/g, (match) => entities[match] || match);
}
