<template>
  <LoadingSpinner v-if="loading" />
  <q-card
    v-else
    flat
    class="column col"
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
          <template v-for="m in messages" :key="m.datetime">
            <q-chat-message
              v-if="m.label"
              :label="m.label"
              class="text-accent text-weight-bold"
            />
            <q-chat-message
              v-else
              :sent="isMine(m)"
              :text="[m.text]"
              :name="m.sender"
              :stamp="timeAgo(m.datetime)"
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
            color="white"
            text-color="accent"
            icon="expand_more"
            style="pointer-events: auto"
            @click="scrollToBottom(true, true)"
          />
        </div>
      </div>
    </q-card-section>

    <!-- Composer -->
    <q-card-section class="col-auto" v-if="isAuthenticated">
      <KennerInput
        ref="inputRef"
        v-model="newMessage"
        class="col-auto"
        type="text"
        filled
        placeholder="Type a message"
        :disable="sending"
        @keydown.enter.prevent="send"
      >
        <template #append>
          <KennerButton
            flat
            round
            dense
            icon="send"
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
const messages: Ref<TMessageDto[]> = ref([]);
const newMessage = ref('');
const sending = ref(false);
const showScrollDown = ref(false);

const inputRef = ref<any>(null);
const scrollAreaRef = ref<QScrollArea | null>(null);

let pollTimer: number | undefined;

// ---------- Helpers ----------
function onScroll(info: {
  verticalPosition: number;
  verticalSize: number;
  verticalContainerSize: number;
}) {
  const diff =
    info.verticalSize - info.verticalPosition - info.verticalContainerSize;
  showScrollDown.value = diff > 200;
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

  sending.value = true;
  try {
    await postMessage(text);
    newMessage.value = '';

    await loadMessages();
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
