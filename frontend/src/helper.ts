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
  if(userStore.isAuthenticated){
    const token = userStore.user.token;
    if (token) {
      api.defaults.headers['Authorization'] = 'Token ' + token;
    }
  }
}
