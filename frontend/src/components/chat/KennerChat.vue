<template>
  <LoadingSpinner v-if="loading" />
  <q-card
    v-else
    flat
    class="column col bg-transparent"
    style="min-width: 350px; min-height: 400px"
  >
    <!-- Messages -->
    <q-card-section class="q-pa-none col column relative-position">
      <div class="relative-position col">
        <q-scroll-area
          :visible="false"
          class="absolute-full q-pa-md"
          ref="scrollAreaRef"
          @scroll="onScroll"
        >
          <div v-if="hasMoreOlder" class="flex flex-center q-mb-md">
            <KennerButton
              flat
              dense
              label="Load older messages"
              :loading="loadingOlder"
              @click="loadOlderMessages"
            />
          </div>
          <div v-else-if="messages.length > 0" class="text-center text-caption text-grey q-mb-md">
            No more messages
          </div>

          <template v-for="m in messages" :key="m.id">
            <q-chat-message
              v-if="m.label"
              :label="m.label"
              class="text-secondary text-weight-bold"
            />
            <q-chat-message
              v-else
              :sent="isMine(m)"
              :text="[m.text]"
              :name="isMine(m) ? undefined : m.sender"
              :stamp="timeAgo(m.datetime)"
              class="chat-message"
              :class="isMine(m) ? 'chat-message-sent' : 'chat-message-received'"
            />
          </template>
        </q-scroll-area>

        <div
          v-if="showScrollDown"
          class="absolute-bottom full-width flex flex-center q-pb-sm"
          style="pointer-events: none; z-index: 1"
        >
          <KennerButton
            flat
            round
            dense
            color="blue-grey-8"
            icon="expand_more"
            style="pointer-events: auto"
            @click="scrollToBottom(true, true)"
          />
        </div>
      </div>
    </q-card-section>

    <!-- Composer -->
    <q-card-section class="col-auto q-pa-md border-top-subtle" v-if="isAuthenticated">
      <KennerInput
        ref="inputRef"
        v-model="newMessage"
        class="col-auto composer-input"
        type="text"
        placeholder="Type a message..."
        :disable="sending"
        @keydown.enter.prevent="send"
      >
        <template #append>
          <KennerButton
            flat
            round
            dense
            icon="send"
            color="blue-grey-8"
            :loading="sending"
            @click="send"
          />
        </template>
      </KennerInput>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, type Ref, nextTick, onMounted, onUnmounted } from 'vue';
import { QScrollArea } from 'quasar';
import { postMessage, fetchMessages } from 'src/services/chatService';
import type { TMessageDto } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';

const { user, isAuthenticated } = storeToRefs(useUserStore());

// ---------- State ----------
let lastDateTime: string | undefined;

const loading = ref(false);
const loadingOlder = ref(false);
const hasMoreOlder = ref(true);
const messages: Ref<TMessageDto[]> = ref([]);
const newMessage = ref('');
const sending = ref(false);
const showScrollDown = ref(false);

const inputRef = ref<any>(null);
const scrollAreaRef = ref<QScrollArea | null>(null);

let pollTimer: number | undefined;

// ---------- Helpers ----------
async function onScroll(info: {
  verticalPosition: number;
  verticalSize: number;
  verticalContainerSize: number;
}) {
  const diff =
    info.verticalSize - info.verticalPosition - info.verticalContainerSize;
  showScrollDown.value = diff > 200;

  // Auto-load older messages when near top
  if (info.verticalPosition < 100 && !loadingOlder.value && hasMoreOlder.value && messages.value.length > 0) {
    await loadOlderMessages();
  }
}

function isMine(m: TMessageDto) {
  if (m.sender != null && user.value?.username != null) {
    return m.sender === user.value.username;
  }
  return false;
}

// Very simple "time ago" helper for stamp
function timeAgo(isoString: string): string {
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = now.getTime() - then.getTime();
  if (Number.isNaN(diffMs)) return '';

  const sec = Math.floor(diffMs / 1000);
  const min = Math.floor(sec / 60);
  const hr = Math.floor(min / 60);
  const day = Math.floor(hr / 24);

  if (sec < 10) return 'just now';
  if (sec < 60) return `${sec} seconds ago`;
  if (min < 60) return `${min} minute${min === 1 ? '' : 's'} ago`;
  if (hr < 24) return `${hr} hour${hr === 1 ? '' : 's'} ago`;
  if (day < 7) return `${day} day${day === 1 ? '' : 's'} ago`;

  return then.toLocaleDateString();
}

async function scrollToBottom(smooth = true, force = false) {
  await nextTick(); // wait for DOM update

  if (!scrollAreaRef.value) return;

  const target = scrollAreaRef.value.getScrollTarget();
  if (!target) return;

  const scrollInfo = scrollAreaRef.value.getScroll();
  const isNearBottom =
    target.scrollHeight - scrollInfo.verticalPosition - target.offsetHeight <
    100;

  if (!isNearBottom && smooth && !force) return;

  const duration = smooth ? 300 : 0;

  scrollAreaRef.value.setScrollPosition(
    'vertical',
    target.scrollHeight,
    duration
  );
}

// ---------- Actions ----------
async function send() {
  const text = newMessage.value.trim();
  if (!text || sending.value) return;

  const tempId = Date.now();
  const optimisticMsg: TMessageDto = {
    id: tempId,
    text,
    datetime: new Date().toISOString(),
    sender: user.value?.username || 'Me',
    user: user.value?.id || 0,
  };

  messages.value.push(optimisticMsg);
  newMessage.value = '';
  scrollToBottom();

  sending.value = true;
  try {
    const { data: sentMsg } = await postMessage(text);
    // Replace the optimistic message with the real one from the server
    const index = messages.value.findIndex(m => m.id === tempId);
    if (index !== -1) {
      messages.value[index] = sentMsg;
    } else {
      messages.value.push(sentMsg);
    }

    // Update lastDateTime so the next poll doesn't fetch this message again
    if (!lastDateTime || sentMsg.datetime > lastDateTime) {
      lastDateTime = sentMsg.datetime;
    }

    scrollToBottom();
  } catch (e) {
    // If it fails, remove the optimistic message
    messages.value = messages.value.filter(m => m.id !== tempId);
    console.error('Failed to send message', e);
  } finally {
    sending.value = false;
    nextTick(() => inputRef.value?.focus());
  }
}

async function loadMessages() {
  const { data } = await fetchMessages({ last_datetime: lastDateTime, limit: 20 });
  if (!data) return;

  if (!lastDateTime) {
    // Initial load
    if (data.length < 20) {
      hasMoreOlder.value = false;
    }
  }

  if (data.length === 0) return;

  const newMessages = data.reverse();

  // De-duplicate: only add messages that aren't already in the list
  const existingIds = new Set(messages.value.map(m => m.id));
  const uniqueNewMessages = newMessages.filter(m => !existingIds.has(m.id));

  if (uniqueNewMessages.length === 0) return;

  messages.value = [...messages.value, ...uniqueNewMessages];
  const lastRealMessage = [...messages.value].reverse().find(m => {
    // Optimistic messages have a Date.now() id, which is > 10^12.
    // Database IDs are usually smaller.
    return m.id < 1000000000000;
  });
  if (lastRealMessage) {
    lastDateTime = lastRealMessage.datetime;
  }
}

async function loadOlderMessages() {
  if (loadingOlder.value || !hasMoreOlder.value) return;

  const firstMsg = messages.value[0];
  if (!firstMsg) return;

  loadingOlder.value = true;
  try {
    const { data } = await fetchMessages({
      before_datetime: firstMsg.datetime,
      limit: 20
    });

    if (!data || data.length === 0) {
      hasMoreOlder.value = false;
      return;
    }

    if (data.length < 20) {
      hasMoreOlder.value = false;
    }

    // Keep track of previous scroll height to maintain position
    const scrollTarget = scrollAreaRef.value?.getScrollTarget();
    const oldScrollHeight = scrollTarget?.scrollHeight || 0;

    const olderMessages = data.reverse();

    // De-duplicate: only add messages that aren't already in the list
    const existingIds = new Set(messages.value.map(m => m.id));
    const uniqueOlderMessages = olderMessages.filter(m => !existingIds.has(m.id));

    if (uniqueOlderMessages.length > 0) {
      messages.value = [...uniqueOlderMessages, ...messages.value];
    } else {
      // If we got data but none were unique, it means we reached the end or something is wrong
      hasMoreOlder.value = false;
      return;
    }

    await nextTick();

    // Adjust scroll position after messages are added to avoid jump
    if (scrollAreaRef.value && scrollTarget) {
      const newScrollHeight = scrollTarget.scrollHeight;
      const heightDiff = newScrollHeight - oldScrollHeight;
      const currentPos = scrollAreaRef.value.getScroll().verticalPosition;
      scrollAreaRef.value.setScrollPosition('vertical', currentPos + heightDiff, 0);
    }
  } catch (err) {
    console.error('Failed to load older messages', err);
  } finally {
    loadingOlder.value = false;
  }
}

// ---------- Lifecycle ----------
onMounted(async () => {
  loading.value = true;
  try {
    await loadMessages();
  } finally {
    loading.value = false; // show q-card
  }

  await scrollToBottom(false); // now the scroll area exists
  pollTimer = window.setInterval(async () => {
    await loadMessages();
    await scrollToBottom(); // optional / conditional
  }, 5000);
});

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = undefined;
  }
});
</script>

<style lang="scss" scoped>
.chat-message {
  margin-bottom: 8px;

  :deep(.q-message-name) {
    font-size: 0.75rem;
    font-weight: 700;
    color: #546e7a; // blue-grey-7
    margin-bottom: 4px;
    opacity: 0.9;
  }

  :deep(.q-message-stamp) {
    font-size: 0.7rem;
    opacity: 0.6;
    margin-top: 4px;
  }

  :deep(.q-message-text) {
    border-radius: 12px !important;
    padding: 10px 14px;
    line-height: 1.5;
    min-height: unset;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);

    &:before {
      display: none;
    }
  }

  &.chat-message-sent {
    :deep(.q-message-text) {
      background: #546e7a !important;
      color: white !important;
      border-bottom-right-radius: 4px !important;
    }
    :deep(.q-message-text-content) {
      color: white !important;
    }
  }

  &.chat-message-received {
    :deep(.q-message-text) {
      background: #f1f3f5 !important;
      color: #2c3e50 !important;
      border-bottom-left-radius: 4px !important;
    }
    :deep(.q-message-text-content) {
      color: #2c3e50 !important;
    }
  }
}

.composer-input {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(8px);
  border-radius: 12px !important;
  padding: 0 4px 0 16px !important;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;

  &:hover {
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(0, 0, 0, 0.12) !important;
  }

  &.q-field--focused {
    background: white !important;
    border-color: #546e7a !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
  }

  :deep(.q-field__control) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
  }

  :deep(.q-field__native) {
    font-weight: 500 !important;
    font-size: 0.95rem;
  }
}
</style>
