<template>
  <SideAccentBox color="accent">
    <q-card flat class="chat-card">
      <!-- Header -->
      <q-card-section class="header-section">
        <div class="header-content">
          <div class="text-h6 text-weight-light">Kennerchat</div>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Chat list -->
      <q-scroll-area
        ref="scrollAreaRef"
        class="chat-area"
        @scroll="handleScroll"
        @mousedown="markAsRead"
        @wheel="markAsRead"
      >
        <div class="chat-messages q-pa-md">
          <div
            v-for="(message, i) in messages"
            :key="message.id ?? `${message.datetime}-${i}`"
            class="message-wrapper"
            :class="{ 'message-mine': isMine(message) }"
          >
            <!-- Unread marker -->
            <transition name="marker-fade">
              <div
                v-if="i === firstUnreadIndex && showUnreadMarker"
                :ref="(el: unknown) => unreadMarkerRef = el as HTMLElement"
                class="unread-marker"
              >
                <div class="unread-line"></div>
                <div class="unread-text">New messages</div>
                <div class="unread-line"></div>
              </div>
            </transition>

            <!-- Username -->
            <div class="message-header">
              <span
                class="username"
                :style="{ color: userColor(message.sender) }"
              >
                {{ message.sender }}
              </span>
              <span class="timestamp">
                {{ formatDateTime(message.datetime) }}
              </span>
            </div>

            <!-- Message bubble -->
            <div class="message-bubble">
              <div class="message-text">{{ message.text }}</div>
            </div>
          </div>
        </div>
      </q-scroll-area>

      <!-- Unread indicator badge -->
      <transition name="fade">
        <div
          v-if="hasUnreadMessages && !isScrolledToBottom"
          class="unread-badge"
          @click="scrollToBottomAndRead"
        >
          <q-badge color="accent" floating rounded>
            {{ unreadCount }}
          </q-badge>
          <q-icon name="keyboard_arrow_down" size="sm" />
          <span class="unread-badge-text">New messages</span>
        </div>
      </transition>

      <q-separator />

      <!-- Composer -->
      <q-card-section v-if="isAuthenticated" class="composer-section">
        <div class="composer-wrapper">
          <q-input
            ref="inputRef"
            v-model="newMessage"
            outlined
            dense
            placeholder="Type a message..."
            color="accent"
            type="textarea"
            autogrow
            :maxlength="500"
            :disable="sending"
            class="message-input"
            @keydown.enter.exact.prevent="send"
            @focus="markAsRead"
          >
            <template #append>
              <q-btn
                :loading="sending"
                flat
                round
                dense
                icon="send"
                color="accent"
                size="sm"
                @click="send"
              />
            </template>
          </q-input>
        </div>
        <div class="text-caption text-grey-6 hint-text">
          Press Enter to send
        </div>
      </q-card-section>
    </q-card>
  </SideAccentBox>
</template>

<script setup lang="ts">
import {
  ref,
  type Ref,
  nextTick,
  onMounted,
  onUnmounted,
  computed,
  watch,
} from 'vue';
import { formatDateTime } from 'src/helpers';
import { postMessage, fetchMessages } from 'src/services/chatService';
import SideAccentBox from 'components/base/SideAccentBox.vue';
import { QInput, QScrollArea } from 'quasar';
import { TMessage } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const { user, isAuthenticated } = storeToRefs(useUserStore());

// ---------- State ----------
let lastDateTime: string | undefined;

const messages: Ref<TMessage[]> = ref([]);
const newMessage = ref('');
const sending = ref(false);

const inputRef = ref<QInput | null>(null);
const scrollAreaRef = ref<QScrollArea | null>(null);
const unreadMarkerRef = ref<HTMLElement | null>(null);

let pollTimer: number | undefined;
let markerFadeTimer: number | undefined;

// Unread tracking
const lastReadIndex = ref<number>(-1);
const isScrolledToBottom = ref(true);
const userHasInteracted = ref(false);
const isAutoScrolling = ref(false);
const showUnreadMarker = ref(true);

// ---------- Computed ----------
const firstUnreadIndex = computed(() => {
  if (
    lastReadIndex.value === -1 ||
    lastReadIndex.value >= messages.value.length - 1
  ) {
    return -1;
  }
  return lastReadIndex.value + 1;
});

const hasUnreadMessages = computed(() => {
  return (
    firstUnreadIndex.value !== -1 &&
    firstUnreadIndex.value < messages.value.length
  );
});

const unreadCount = computed(() => {
  if (firstUnreadIndex.value === -1) return 0;
  return messages.value.length - firstUnreadIndex.value;
});

// Watch for when unread messages disappear to trigger fade out
watch(hasUnreadMessages, (newVal, oldVal) => {
  if (oldVal === true && newVal === false) {
    // Unread messages just disappeared, start fade out timer
    if (markerFadeTimer) {
      clearTimeout(markerFadeTimer);
    }
    markerFadeTimer = window.setTimeout(() => {
      showUnreadMarker.value = false;
    }, 3000); // 3 second delay before fading
  } else if (newVal === true) {
    // Unread messages appeared, show marker immediately
    showUnreadMarker.value = true;
    if (markerFadeTimer) {
      clearTimeout(markerFadeTimer);
      markerFadeTimer = undefined;
    }
  }
});

// ---------- Helpers ----------
function isMine(m: TMessage) {
  if (m.sender != null && user.value?.username != null) {
    return m.sender === user.value.username;
  }
  return false;
}

function handleScroll(info: {
  verticalPosition: number;
  verticalSize: number;
  verticalContainerSize: number;
}) {
  const threshold = 50;
  const isAtBottom =
    info.verticalSize - info.verticalPosition - info.verticalContainerSize <
    threshold;

  // Only update isScrolledToBottom if this is not an automatic scroll
  if (!isAutoScrolling.value) {
    isScrolledToBottom.value = isAtBottom;
  }
}

function markAsRead() {
  if (!userHasInteracted.value) {
    userHasInteracted.value = true;
  }

  // Mark all messages as read
  if (messages.value.length > 0) {
    lastReadIndex.value = messages.value.length - 1;
  }
}

function scrollToBottom(smooth = true) {
  isAutoScrolling.value = true;
  nextTick(() => {
    if (scrollAreaRef.value) {
      const scrollTarget = scrollAreaRef.value.getScrollTarget();
      scrollAreaRef.value.setScrollPosition(
        'vertical',
        scrollTarget.scrollHeight,
        smooth ? 300 : 0
      );
    }
    // Reset after scroll animation completes
    setTimeout(
      () => {
        isAutoScrolling.value = false;
      },
      smooth ? 350 : 50
    );
  });
}

function scrollToKeepMarkerAtTop() {
  isAutoScrolling.value = true;
  nextTick(() => {
    if (scrollAreaRef.value && unreadMarkerRef.value) {
      const scrollTarget = scrollAreaRef.value.getScrollTarget();

      // Get the position of the unread marker relative to the scroll container
      const markerRect = unreadMarkerRef.value.getBoundingClientRect();
      const containerRect = scrollTarget.getBoundingClientRect();

      // Calculate how far from the top of the container the marker is
      const markerOffsetInContainer = markerRect.top - containerRect.top;

      // Target position: keep marker at top with some padding (e.g., 80px from top)
      const targetPadding = 80;
      const currentScrollTop = scrollTarget.scrollTop;
      const targetScrollTop =
        currentScrollTop + markerOffsetInContainer - targetPadding;

      // Only scroll if marker is not already at the target position
      if (Math.abs(markerOffsetInContainer - targetPadding) > 10) {
        scrollAreaRef.value.setScrollPosition('vertical', targetScrollTop, 300);
      }
    }
    // Reset after scroll animation completes
    setTimeout(() => {
      isAutoScrolling.value = false;
    }, 350);
  });
}

function scrollToBottomAndRead() {
  markAsRead();
  scrollToBottom();
}

// ---------- Actions ----------
async function send() {
  const text = newMessage.value.trim();
  if (!text || sending.value) return;

  sending.value = true;
  try {
    await postMessage(text);
    newMessage.value = '';

    // Mark as interaction BEFORE loading new messages
    userHasInteracted.value = true;

    await loadMessages();

    // After loading, mark everything as read (including your own message)
    lastReadIndex.value = messages.value.length - 1;

    scrollToBottom();
  } finally {
    sending.value = false;
    nextTick(() => inputRef.value?.focus());
  }
}

async function loadMessages() {
  const { data } = await fetchMessages(lastDateTime);
  if (!data || data.length === 0) return;

  const previousLength = messages.value.length;
  const newMessages = data.reverse();

  // Append in chronological order
  messages.value = [...messages.value, ...newMessages];
  lastDateTime = messages.value[messages.value.length - 1].datetime;

  // Check if any new messages are from other users
  const hasNewMessagesFromOthers = newMessages.some((msg) => !isMine(msg));

  // Only update lastReadIndex if:
  // 1. User is at bottom and already has read everything
  // 2. OR if the new messages are only from the current user
  if (isScrolledToBottom.value) {
    if (!hasNewMessagesFromOthers) {
      // All new messages are from you, mark as read
      lastReadIndex.value = messages.value.length - 1;
    }
  }

  // Smart scrolling behavior:
  if (isScrolledToBottom.value && !hasUnreadMessages.value) {
    // User is at bottom, no unread messages - keep following
    scrollToBottom();
  } else if (hasUnreadMessages.value && unreadMarkerRef.value) {
    // There are unread messages - keep the marker at the top
    scrollToKeepMarkerAtTop();
  }
}

// helpers for username → stable color
function userColor(name?: string | null) {
  const s = (name ?? '').trim();
  if (!s) return 'hsl(0, 0%, 70%)';
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  const hue = Math.abs(h) % 360;
  return `hsl(${hue}, 70%, 50%)`;
}

// ---------- Lifecycle ----------
onMounted(() => {
  loadMessages().then(() => {
    scrollToBottom(false);
    // Initially mark as read on mount
    if (messages.value.length > 0) {
      lastReadIndex.value = messages.value.length - 1;
    }
  });

  // polling for new messages
  pollTimer = window.setInterval(async () => {
    await loadMessages();
  }, 5000);

  // Listen for keyboard events on the whole component
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = undefined;
  }

  if (markerFadeTimer) {
    clearTimeout(markerFadeTimer);
    markerFadeTimer = undefined;
  }

  window.removeEventListener('keydown', handleKeydown);
});

function handleKeydown(event: KeyboardEvent) {
  // Mark as read on any keyboard input when chat is visible
  if (event.key) {
    markAsRead();
  }
}
</script>

<style scoped lang="scss">
.chat-card {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.header-section {
  padding: 16px 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-area {
  flex: 1;
  height: 100%;
  position: relative;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100%;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 75%;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-mine {
  align-self: flex-end;

  .message-header {
    justify-content: flex-end;
  }

  .message-bubble {
    padding: 5px 7px;
    background: var(--q-accent);
    color: #ffffff;
    border-radius: 18px 18px 4px 18px;
    transition: all 0.2s ease-in-out;
  }
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
  margin-bottom: 2px;
}

.username {
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.timestamp {
  font-size: 0.75rem;
  color: #9e9e9e;
}

.message-bubble {
  padding: 5px 7px;
  background: #f7f7f7;
  border-radius: 4px 18px 18px 18px;
  transition: all 0.2s ease-in-out;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
  font-size: 0.9rem;
}

/* Unread marker */
.unread-marker {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  width: 100%;
}

.unread-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #26a69a, transparent);
}

.unread-text {
  font-size: 0.75rem;
  color: #26a69a;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Marker fade transition */
.marker-fade-enter-active {
  transition: opacity 0.3s ease;
}

.marker-fade-leave-active {
  transition: opacity 3s ease;
}

.marker-fade-enter-from,
.marker-fade-leave-to {
  opacity: 0;
}

/* Unread badge floating button */
.unread-badge {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 8px 16px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    transform: translateX(-50%) translateY(-2px);
  }
}

.unread-badge-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #424242;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.composer-section {
  padding: 16px 20px;
  background: #fafafa;
}

.composer-wrapper {
  margin-bottom: 4px;
}

.message-input {
  :deep(.q-field__control) {
    border-radius: 20px;
    background: white;
  }

  :deep(textarea) {
    max-height: 100px;
  }
}

.hint-text {
  padding-left: 12px;
  font-size: 0.7rem;
}

/* Mobile responsive */
@media (max-width: 600px) {
  .chat-card {
    height: 500px;
  }

  .message-wrapper {
    max-width: 85%;
  }

  .header-section,
  .composer-section {
    padding: 12px 16px;
  }

  .unread-badge-text {
    display: none;
  }
}
</style>
