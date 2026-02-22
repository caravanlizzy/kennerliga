import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';

export const useUpdateStore = defineStore('update', () => {
  const lastUpdateCheck = ref(new Date().toISOString());
  const topics = ref<Set<string>>(new Set());
  const listeners = ref<Map<string, Array<() => void | Promise<void>>>>(new Map());
  let pollTimer: number | undefined;

  async function checkUpdates() {
    if (topics.value.size === 0) return;

    try {
      const { data } = await api.get<{ updates: string[] }>(
        `/needs-update/?since=${encodeURIComponent(lastUpdateCheck.value)}`
      );

      const now = new Date().toISOString();
      const receivedUpdates = data.updates;

      if (receivedUpdates.length > 0) {
        for (const topic of topics.value) {
          if (receivedUpdates.some(u => u.includes(topic))) {
            const topicListeners = listeners.value.get(topic);
            if (topicListeners) {
              for (const listener of topicListeners) {
                try {
                  await listener();
                } catch (e) {
                  console.error(`Error in update listener for topic ${topic}:`, e);
                }
              }
            }
          }
        }
      }
      lastUpdateCheck.value = now;
    } catch (e) {
      console.error('Error checking for updates:', e);
    }
  }

  function subscribe(topic: string, callback: () => void | Promise<void>) {
    topics.value.add(topic);
    if (!listeners.value.has(topic)) {
      listeners.value.set(topic, []);
    }
    listeners.value.get(topic)?.push(callback);

    if (!pollTimer) {
      startPolling();
    }

    return () => unsubscribe(topic, callback);
  }

  function unsubscribe(topic: string, callback: () => void | Promise<void>) {
    const topicListeners = listeners.value.get(topic);
    if (topicListeners) {
      const index = topicListeners.indexOf(callback);
      if (index !== -1) {
        topicListeners.splice(index, 1);
      }
      if (topicListeners.length === 0) {
        listeners.value.delete(topic);
        topics.value.delete(topic);
      }
    }

    if (topics.value.size === 0 && pollTimer) {
      stopPolling();
    }
  }

  function startPolling() {
    if (pollTimer) return;
    pollTimer = window.setInterval(checkUpdates, 5000);
  }

  function stopPolling() {
    if (pollTimer) {
      window.clearInterval(pollTimer);
      pollTimer = undefined;
    }
  }

  return {
    subscribe,
    unsubscribe
  };
});
