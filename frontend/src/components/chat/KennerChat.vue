<template>
  <div class="q-pa-md">
    <q-card bordered flat>
      <q-card-section class="text-h6">
        Kennerchat
      </q-card-section>
      <q-separator color="accent"/>
      <q-card-section class="q-px-lg">
        <div class="row justify-between q-py-xs" v-for="message of messages" :key="JSON.stringify(message)">
          <div class="">
            {{ message.sender }}
            <KennerTooltip anchor="top middle" self="bottom middle">
              {{ formatDateTime(message.datetime) }}
            </KennerTooltip>
          </div>
          <div> {{ message.text }}</div>
        </div>
      </q-card-section>
      <q-separator color="accent"/>
      <q-card-section>
        <q-input @keyup.enter="send" v-model="newMessage" filled label="Nachricht" color="accent">
          <template v-slot:append>
            <q-btn @click="send()" flat icon="send" color="accent"></q-btn>
          </template>
        </q-input>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">

import { formatDateTime } from 'src/helpers';
import { Ref, ref } from 'vue';
import { addMessage, getMessages, TMessage } from 'src/services/chatService';
import KennerTooltip from 'components/base/KennerTooltip.vue';

let lastDateTime: string | undefined;

const messages: Ref<TMessage[]> = ref([]);
const newMessage = ref('');

loadMessages();
setInterval(() => loadMessages(), 5000);


async function send() {
  await addMessage(newMessage.value);
  newMessage.value = '';
  await loadMessages();
}

async function loadMessages() {
  const { data } = await getMessages(lastDateTime);
  if(data.length === 0) return;
  messages.value = [...messages.value, ...data.reverse()];
  lastDateTime = messages.value[messages.value.length - 1].datetime;
}

</script>


