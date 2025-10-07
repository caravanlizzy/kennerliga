<template>
  <SideAccentBox color="accent">
    <q-card bordered flat class="chat-card">
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
            class="row justify-between q-py-xs"
            v-for="(message, i) in messages"
            :key="message.id ?? `${message.datetime}-${i}`"
          >
            <div>
              {{ message.sender }}
              <KennerTooltip anchor="top middle" self="bottom middle">
                {{ formatDateTime(message.datetime) }}
              </KennerTooltip>
            </div>
            <div>{{ message.text }}</div>
          </div>

          <!-- sentinel to scroll to bottom -->
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
import { ref, type Ref, nextTick, watch, onMounted, computed } from 'vue';
import { formatDateTime } from 'src/helpers';
import {
  addMessage,
  getMessages,
  type TMessage,
} from 'src/services/chatService';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import SideAccentBox from 'components/base/SideAccentBox.vue';

/**
 * Identify current user — PREFER an ID from your auth/session store.
 * Fill these with your real values (e.g. from Pinia, cookies, etc.)
 */
const currentUserId: string | number | null = null; // e.g. useAuthStore().user.id
const currentUserName: string | null = null; // e.g. useAuthStore().user.username

// ---------- State ----------
let lastDateTime: string | undefined;

const messages: Ref<TMessage[]> = ref([]);
const newMessage = ref('');
const sending = ref(false);

const chatEl = ref<HTMLElement | null>(null);
const bottomAnchor = ref<HTMLElement | null>(null);
const inputRef = ref<any>(null);

const notAtBottom = ref(false);
const unreadCount = ref(0);
const inputFocused = ref(false);

const showUnread = computed(() => notAtBottom.value && unreadCount.value > 0);

// ---------- Helpers ----------
const norm = (s?: string | null) => (s ?? '').trim().toLowerCase();

function isMine(m: TMessage) {
  const anyMsg = m as any;
  if (anyMsg.sender_id != null && currentUserId != null) {
    return anyMsg.sender_id === currentUserId;
  }
  if (currentUserName) {
    return norm(anyMsg.sender) === norm(currentUserName);
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
    await addMessage(text);
    newMessage.value = '';
    await loadMessages();
    jumpToBottom(true);
  } finally {
    sending.value = false;
    nextTick(() => inputRef.value?.focus());
  }
}

async function loadMessages() {
  const { data } = await getMessages(lastDateTime);
  if (!data || data.length === 0) return;

  // Append in chronological order
  messages.value = [...messages.value, ...data.reverse()];
  lastDateTime = messages.value[messages.value.length - 1].datetime;
}

// When messages change, decide auto-scroll & unread count
watch(
  () => messages.value.length,
  (newLen, oldLen) => {
    if (newLen === 0) return;

    const wasNear = isNearBottom();
    const added = newLen - (oldLen ?? 0) || 0;

    if (!oldLen) {
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
    nextTick(() => inputRef.value?.focus());
  });

  // polling for new messages
  setInterval(async () => {
    await loadMessages();
    if (isNearBottom()) jumpToBottom(true);
  }, 5000);
});
</script>

<style scoped lang="scss">
.chat-card {
  position: relative;
}
.chat-wrap {
  position: relative;
}

.chat {
  max-height: 300px;
  overflow-y: auto;
  scroll-behavior: smooth; /* smooth user-initiated scrolls */
}
</style>
