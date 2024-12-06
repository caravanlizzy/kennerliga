<template>
  <q-card bordered class="q-pa-lg">
    <div>Current user: {{ user.username }}</div>
    <div style="max-width: 150px" class="q-pa-xs">
      <div>
        <kenner-button
          color="accent"
          outline
          @click="loginAsUser"
        >
          Login as
        </kenner-button>
      </div>
      <div>
        <kenner-select
          v-model="userSelection"
          :options="allUsers"
          option-value="username"
          option-label="username"
          label="new user"
        />
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { useUserStore } from 'stores/userStore';
import KennerButton from 'components/buttons/KennerButton.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { ref } from 'vue';
import { storeToRefs } from 'pinia';

const userStore = useUserStore();
const { listUsers, login } = userStore;
const { user } = storeToRefs(userStore);

// Decouple userSelection from the store's user
const userSelection = ref(null); // Start as null or a default value
const allUsers = await listUsers();

function loginAsUser() {
  if (userSelection.value) {
    login(userSelection.value.username, 'test'); // Update the store explicitly
  }
}
</script>
