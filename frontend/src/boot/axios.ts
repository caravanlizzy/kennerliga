import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { loadToken } from 'src/helpers';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({ baseURL: process.env.API_URL });

/**
 * Called when the API rejects our token. Registered by the user store so
 * this module doesn't have to import it (which would create a cycle:
 * userStore -> boot/axios -> userStore).
 */
let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  onUnauthorized = handler;
}

// A token can expire or be revoked server-side while the SPA still believes
// it is signed in. Without this the app keeps rendering an authenticated
// shell and every request fails silently in a component-local catch.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const isLoginAttempt = String(error?.config?.url ?? '').includes('login/');
    if (status === 401 && !isLoginAttempt && onUnauthorized) {
      onUnauthorized();
    }
    return Promise.reject(error);
  }
);

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  // guarantee the token to be set in headers if available.

  loadToken();
});

/**
 * Single place responsible for attaching/removing the auth token on the
 * shared Axios instance. Callers (userStore, helpers.loadToken, ...) should
 * use this instead of mutating `api.defaults.headers` themselves, so token
 * handling isn't spread across multiple Axios-aware places.
 */
export function setAuthToken(token: string | null | undefined): void {
  if (token) {
    api.defaults.headers.common['Authorization'] = 'Token ' + token;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

export { api };
