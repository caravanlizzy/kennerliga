<template>
  <ContentSection :isOpened="true" title="Kennerchat" color="info">
    <q-card
      flat
      class="chat-card"
      :class="isMobile ? 'chat-card--mobile' : 'chat-card--desktop'"
    >
<!--      &lt;!&ndash; Header &ndash;&gt;-->
<!--      <q-card-section-->
<!--        class="header-section"-->
<!--        :class="isMobile ? 'header-section&#45;&#45;mobile' : 'header-section&#45;&#45;desktop'"-->
<!--      >-->
<!--        <div class="header-content">-->
<!--          <div class="text-subtitle1 text-weight-light">Kennerchat</div>-->
<!--        </div>-->
<!--      </q-card-section>-->

<!--      <q-separator spaced />-->

      <!-- Chat list -->
      <q-scroll-area
        ref="scrollAreaRef"
        class="chat-area"
        @scroll="handleScroll"
        @mousedown="markAsRead"
        @wheel="markAsRead"
      >
        <div class="chat-messages q-pa-sm">
          <div
            v-for="(message, i) in messages"
            :key="message.id ?? `${message.datetime}-${i}`"
            class="message-wrapper"
            :class="{
              'message-mine': isMine(message),
              'message-wrapper--mobile': isMobile,
              'message-wrapper--desktop': !isMobile
            }"
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

            <!-- Username / timestamp -->
            <div class="message-header">
              <span
                class="username"
                :class="isMobile ? 'username--mobile' : 'username--desktop'"
                :style="{ color: userColor(message.sender) }"
              >
                {{ message.sender }}
              </span>
              <span
                class="timestamp"
                :class="isMobile ? 'timestamp--mobile' : 'timestamp--desktop'"
              >
                {{ formatDateTime(message.datetime) }}
              </span>
            </div>

            <!-- Message bubble -->
            <div
              class="message-bubble"
              :class="isMobile ? 'message-bubble--mobile' : 'message-bubble--desktop'"
            >
              <div class="message-text">
                {{ message.text }}
              </div>
            </div>
          </div>
        </div>
      </q-scroll-area>

      <!-- Unread indicator badge -->
      <transition name="fade">
        <div
          v-if="hasUnreadMessages && !isScrolledToBottom"
          class="unread-badge"
          :class="isMobile ? 'unread-badge--mobile' : 'unread-badge--desktop'"
          @click="scrollToBottomAndRead"
        >
          <q-badge color="info" floating rounded>
            {{ unreadCount }}
          </q-badge>
          <q-icon name="keyboard_arrow_down" size="sm" />
          <span class="unread-badge-text" v-if="!isMobile">New messages</span>
        </div>
      </transition>

      <q-separator />

      <!-- Composer -->
      <q-card-section
        v-if="isAuthenticated"
        class="composer-section"
        :class="isMobile ? 'composer-section--mobile' : 'composer-section--desktop'"
      >
        <div class="composer-wrapper">
          <q-input
            ref="inputRef"
            v-model="newMessage"
            outlined
            dense
            placeholder="Type a message..."
            color="info"
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
                color="info"
                size="sm"
                @click="send"
              />
            </template>
          </q-input>
        </div>
        <div
          class="text-caption text-grey-6 hint-text"
          :class="isMobile ? 'hint-text--mobile' : 'hint-text--desktop'"
        >
          Press Enter to send
        </div>
      </q-card-section>
    </q-card>
  </ContentSection>
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
import { useQuasar } from 'quasar';
import { formatDateTime } from 'src/helpers';
import { postMessage, fetchMessages } from 'src/services/chatService';
import { QInput, QScrollArea } from 'quasar';
import { TMessage } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';

const { user, isAuthenticated } = storeToRefs(useUserStore());
const $q = useQuasar();

const isMobile = computed(() => $q.screen.lt.md);

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
    if (markerFadeTimer) {
      clearTimeout(markerFadeTimer);
    }
    markerFadeTimer = window.setTimeout(() => {
      showUnreadMarker.value = false;
    }, 3000);
  } else if (newVal === true) {
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

  if (!isAutoScrolling.value) {
    isScrolledToBottom.value = isAtBottom;
  }
}

function markAsRead() {
  if (!userHasInteracted.value) {
    userHasInteracted.value = true;
  }

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

      const markerRect = unreadMarkerRef.value.getBoundingClientRect();
      const containerRect = scrollTarget.getBoundingClientRect();

      const markerOffsetInContainer = markerRect.top - containerRect.top;
      const targetPadding = 60; // slightly tighter
      const currentScrollTop = scrollTarget.scrollTop;
      const targetScrollTop =
        currentScrollTop + markerOffsetInContainer - targetPadding;

      if (Math.abs(markerOffsetInContainer - targetPadding) > 10) {
        scrollAreaRef.value.setScrollPosition('vertical', targetScrollTop, 250);
      }
    }
    setTimeout(() => {
      isAutoScrolling.value = false;
    }, 300);
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

    userHasInteracted.value = true;

    await loadMessages();

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

  const newMessages = data.reverse();

  messages.value = [...messages.value, ...newMessages];
  lastDateTime = messages.value[messages.value.length - 1].datetime;

  const hasNewMessagesFromOthers = newMessages.some((msg) => !isMine(msg));

  if (isScrolledToBottom.value) {
    if (!hasNewMessagesFromOthers) {
      lastReadIndex.value = messages.value.length - 1;
    }
  }

  if (isScrolledToBottom.value && !hasUnreadMessages.value) {
    scrollToBottom();
  } else if (hasUnreadMessages.value && unreadMarkerRef.value) {
    scrollToKeepMarkerAtTop();
  }
}

// username → stable color
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
    if (messages.value.length > 0) {
      lastReadIndex.value = messages.value.length - 1;
    }
  });

  pollTimer = window.setInterval(async () => {
    await loadMessages();
  }, 5000);

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
  if (event.key) {
    markAsRead();
  }
}
</script>

<style scoped lang="scss">
.chat-card {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.header-section {
  padding: 10px 14px;
}

.header-section--desktop {
  padding: 10px 16px;
}

.header-section--mobile {
  padding: 8px 10px;
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
  gap: 12px;
  min-height: 100%;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-width: 75%;
  animation: slideIn 0.15s ease-out;
}

.message-wrapper--mobile {
  max-width: 85%;
}

.message-wrapper--desktop {
  max-width: 70%;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(6px);
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
    padding: 4px 7px;
    background: var(--q-info);
    color: #ffffff;
    border-radius: 14px 14px 3px 14px;
    transition: all 0.15s ease-in-out;
  }
}

.message-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 2px;
  margin-bottom: 1px;
}

.username {
  font-weight: 500;
  letter-spacing: 0.2px;
}

.username--desktop {
  font-size: 0.82rem;
}

.username--mobile {
  font-size: 0.78rem;
}

.timestamp {
  color: #9e9e9e;
}

.timestamp--desktop {
  font-size: 0.74rem;
}

.timestamp--mobile {
  font-size: 0.7rem;
}

.message-bubble {
  padding: 4px 6px;
  background: #2f6781;
  color: white;
  border-radius: 3px 14px 14px 14px;
  transition: all 0.15s ease-in-out;
}

.message-bubble--desktop {
  font-size: 0.9rem;
}

.message-bubble--mobile {
  font-size: 0.86rem;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
  font-size: inherit;
}

/* Unread marker */
.unread-marker {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0;
  width: 100%;
}

.unread-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #26a69a, transparent);
}

.unread-text {
  font-size: 0.7rem;
  color: #26a69a;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Marker fade transition */
.marker-fade-enter-active {
  transition: opacity 0.2s ease;
}

.marker-fade-leave-active {
  transition: opacity 2s ease;
}

.marker-fade-enter-from,
.marker-fade-leave-to {
  opacity: 0;
}

/* Unread badge floating button */
.unread-badge {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.15s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
    transform: translateX(-50%) translateY(-1px);
  }
}

.unread-badge--mobile {
  bottom: 8px;
}

.unread-badge-text {
  font-size: 0.8rem;
  font-weight: 500;
  color: #424242;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}

.composer-section {
  background: #fafafa;
}

.composer-section--desktop {
  padding: 10px 14px;
}

.composer-section--mobile {
  padding: 8px 10px;
}

.composer-wrapper {
  margin-bottom: 2px;
}

.message-input {
  :deep(.q-field__control) {
    border-radius: 16px;
    background: white;
    min-height: 36px;
  }

  :deep(textarea) {
    max-height: 80px;
    font-size: 0.85rem;
  }
}

.hint-text {
  padding-left: 8px;
}

.hint-text--desktop {
  font-size: 0.7rem;
}

.hint-text--mobile {
  font-size: 0.68rem;
}
</style>
