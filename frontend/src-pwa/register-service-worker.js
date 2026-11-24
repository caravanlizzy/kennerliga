import { register } from 'register-service-worker';
import {
  setServiceWorkerRegistration,
  onServiceWorkerUpdated,
} from 'src/services/appUpdateService';

register(process.env.SERVICE_WORKER_FILE, {
  ready(registration) {
    setServiceWorkerRegistration(registration);
  },
  registered(registration) {
    setServiceWorkerRegistration(registration);
  },
  updated(registration) {
    onServiceWorkerUpdated(registration);
  },
  error(error) {
    console.error('Service worker registration failed.', error);
  },
});
