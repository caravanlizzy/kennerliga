<template>
  <SideAccentBox color="accent">
    <q-card bordered square flat class="chat-card">
      <!-- Header with unread chip -->
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Kennerchat</div>

        <q-chip
          v-show="showUnread"
          dense
          color="accent"
          text-color="white"
          icon="mark_chat_unread"
          clickable
          @click="onUnreadChipClick"
        >
          {{ unreadCount }} new
        </q-chip>
      </q-card-section>

      <q-separator color="accent" />

      <!-- Chat list -->
      <div class="chat-wrap">
        <q-card-section
          ref="chatEl"
          class="q-px-lg chat"
          aria-live="polite"
          @scroll.passive="onScroll"
          @pointerdown.passive="markChatRead"
          @mousedown.passive="markChatRead"
          @touchstart.passive="markChatRead"
          @wheel.passive="markChatRead"
        >
          <div
            class="row no-wrap items-start q-py-xs msg-row"
            v-for="(message, i) in messages"
            :key="message.id ?? `${message.datetime}-${i}`"
            :style="{ '--uclr': userColor(message.sender) }"
          >
            <!-- username + dot -->
            <div class="col-auto q-pr-sm username q-pt-xs flex items-center">
              <span class="text-caption text-weight-medium">
                {{ message.sender }}
              </span>
              <span class="color-dot q-mr-xs" />
              <KennerTooltip anchor="top middle" self="bottom middle">
                {{ formatDateTime(message.datetime) }}
              </KennerTooltip>
            </div>

            <!-- message bubble -->
            <div class="col msg-right">
              <div
                class="bubble q-pa-sm rounded-borders bg-grey-1 text-dark"
                :class="{ mine: isMine(message) }"
              >
                <div class="prewrap">{{ message.text }}</div>
              </div>
            </div>
          </div>

          <div ref="bottomAnchor" aria-hidden="true" />
        </q-card-section>
      </div>

      <q-separator color="accent" />

      <!-- Composer -->
      <q-card-section>
        <q-input
          ref="inputRef"
          v-model="newMessage"
          filled
          label="Message"
          color="accent"
          type="textarea"
          autogrow
          :disable="sending"
          @keydown.enter.exact.prevent="send"
          @focus="onInputFocus"
          @blur="onInputBlur"
        >
          <template #append>
            <q-btn
              :loading="sending"
              flat
              icon="send"
              color="accent"
              @click="send"
            />
          </template>
        </q-input>
        <div class="text-caption text-grey-7 q-mt-xs">
          Enter = send · Shift+Enter = line break
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
  watch,
  onMounted,
  onUnmounted,
  computed,
} from 'vue';
import { formatDateTime } from 'src/helpers';
import {
  postMessage,
  fetchMessages,
} from 'src/services/chatService';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import SideAccentBox from 'components/base/SideAccentBox.vue';
import { QInput } from 'quasar';
import { TMessage } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const { user } = storeToRefs(useUserStore());
/**
 * Identify current user — PREFER an ID from your auth/session store.
 * Fill these with your real values (e.g. from Pinia, cookies, etc.)
 */

// ---------- State ----------
let lastDateTime: string | undefined;

const messages: Ref<TMessage[]> = ref([]);
const newMessage = ref('');
const sending = ref(false);

const chatEl = ref<HTMLElement | null>(null);
const bottomAnchor = ref<HTMLElement | null>(null);
const inputRef = ref<QInput | null>(null);

const notAtBottom = ref(false);
const unreadCount = ref(0);
const inputFocused = ref(false);
let pollTimer: number | undefined;

const showUnread = computed(() => notAtBottom.value && unreadCount.value > 0);

// ---------- Helpers ----------
const norm = (s?: string | null) => (s ?? '').trim().toLowerCase();

function isMine(m: TMessage) {
  if (m.sender != null && user.value?.username != null) {
    return m.sender === user.value.username;
  }
  return false;
}

function isNearBottom(threshold = 60) {
  const el = chatEl.value;
  if (!el) return true;
  const delta = el.scrollHeight - el.scrollTop - el.clientHeight;
  return delta <= threshold;
}

function jumpToBottom(smooth = false) {
  nextTick(() => {
    bottomAnchor.value?.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
      block: 'end',
    });
  });
}

function markChatRead() {
  unreadCount.value = 0;
}

function onUnreadChipClick() {
  markChatRead();
  jumpToBottom(true);
}

// ---------- Events ----------
function onScroll() {
  const near = isNearBottom();
  notAtBottom.value = !near;
  if (near) unreadCount.value = 0; // if newest is visible, they're read
}

function onInputFocus() {
  inputFocused.value = true;
  unreadCount.value = 0; // typing: treat incoming as read
}

function onInputBlur() {
  inputFocused.value = false;
}

// ---------- Actions ----------
async function send() {
  const text = newMessage.value.trim();
  if (!text || sending.value) return;

  sending.value = true;
  try {
    await postMessage(text);
    newMessage.value = '';
    await loadMessages();
    jumpToBottom(true);
  } finally {
    sending.value = false;
    // focus ONLY after sending
    nextTick(() => inputRef.value?.focus());
  }
}

async function loadMessages() {
  const { data } = await fetchMessages(lastDateTime);
  console.log({ data });
  if (!data || data.length === 0) return;

  // Append in chronological order
  messages.value = [...messages.value, ...data.reverse()];
  lastDateTime = messages.value[messages.value.length - 1].datetime;
}

// helpers for username → stable color
function userColor(name?: string | null) {
  const s = (name ?? '').trim();
  if (!s) return 'hsl(0, 0%, 70%)';
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  const hue = Math.abs(h) % 360;
  return `hsl(${hue}, 65%, 55%)`;
}

// When messages change, decide auto-scroll & unread count
watch(
  () => messages.value.length,
  (newLen, oldLen) => {
    if (newLen === 0) return;

    const wasNear = isNearBottom();
    const prevLen = oldLen ?? 0;
    const added = newLen - prevLen;

    if (prevLen === 0) {
      // First render
      jumpToBottom(false);
      return;
    }

    if (added > 0) {
      const newMessages = messages.value.slice(-added);
      const foreignMessages = newMessages.filter((m) => !isMine(m));

      if (wasNear) {
        // already at bottom -> stick
        jumpToBottom(true);
      } else if (inputFocused.value) {
        // typing -> don't count
        /* no-op */
      } else if (foreignMessages.length > 0) {
        unreadCount.value += foreignMessages.length;
        notAtBottom.value = true;
      }
    }
  }
);

// ---------- Lifecycle ----------
onMounted(() => {
  loadMessages().then(() => {
    jumpToBottom(false);
  });

  // polling for new messages
  pollTimer = window.setInterval(async () => {
    await loadMessages();
    if (isNearBottom()) jumpToBottom(true);
  }, 5000);
});

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = undefined;
  }
});
</script>

<style scoped lang="scss">
.chat {
  max-height: 400px;
  min-height: 200px;
  overflow-y: auto;
  scroll-behavior: smooth;
  padding-right: 4px;
}

/* message row */
.msg-row {
  align-items: flex-start;
}

/* username + color dot */
.username {
  min-width: 5.5rem;
}

/* softer, smaller dot */
.color-dot {
  width: 6px; /* was 8px */
  height: 6px;
  border-radius: 50%;
  background-color: var(--uclr);
  opacity: 0.5; /* very light */
  margin-left: 6px; /* space after name */
  box-shadow: none; /* remove glow */
  flex: 0 0 auto;
}

/* right side aligns bubble to the right */
.msg-right {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

/* message bubble */
.bubble {
  max-width: 45%;
  min-width: 220px;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
}

/* slightly accentuate your own messages */
.mine {
  border-right: 2px solid teal;
  border-left: 2px solid teal;
}

/* preserve line breaks */
.prewrap {
  white-space: pre-wrap;
}

/* mobile: relax bubble cap a bit */
@media (max-width: 600px) {
  .bubble {
    max-width: 80%;
    min-width: 160px;
  }
}
</style>
