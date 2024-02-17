<template>
  <div class="q-pa-md">
    <q-card>
      <q-card-section class="text-h6">
        Kennerchat
      </q-card-section>
      <q-separator color="accent" />
      <q-card-section class="q-px-lg">
        <div class="row justify-between q-py-xs" v-for="message of messages" :key="JSON.stringify(message)">
          <div class=""> {{ message.sender }} {{ message.time }}</div>
          <div> {{ message.text }}</div>
        </div>
      </q-card-section>
      <q-separator color="accent" />
      <q-card-section>
        <q-input filled label="Nachricht" color="accent">
          <template v-slot:append>
            <q-btn flat icon="send" color="accent"></q-btn>
          </template>
        </q-input>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">

type TMessage = {
  sender: string;
  text: string;
  time: string;
}
const messages: TMessage[] = [
  { sender: 'Marc', text: 'Warum?', time: '15:34' },
  { sender: 'Selina', text: 'Darum!', time: '14:34' },
  { sender: 'Eumel', text: 'Habt ihr schonmal überlegt was das bringen soll?', time: '13:22' },
  { sender: 'Eumel', text: 'Warum?', time: '14:34' },
  { sender: 'Eumel', text: 'Warum?', time: '14:34' },
  { sender: 'Eumel', text: 'Warum?', time: '14:34' },
  { sender: 'Selina', text: 'Warum?', time: '14:34' },
  { sender: 'Selina', text: 'Warum?', time: '14:34' },
  { sender: 'Selina', text: 'Warum?', time: '14:34' },
  { sender: 'Marc', text: 'Warum?', time: '14:34' },
  { sender: 'Marc', text: 'Warum?', time: '14:34' }
];
</script>

<style scoped lang="scss">
.chat-border {
  border: 2px solid $primary;
}
</style>


