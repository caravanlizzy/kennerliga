import { register } from 'register-service-worker';

register(process.env.SERVICE_WORKER_FILE, {
  error(error) {
    console.error('Service worker registration failed.', error);
  },
});
