<template>
  <div class="row ">
    <q-chip
      v-for="user in users"
      :key="user"
      clickable
      square
      color="primary"
      @click="impersonate(user)"
      text-color="white"
      icon="person"
      class="cursor-pointer"
    >
      {{ user }}
    </q-chip>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { fetchUsers } from 'src/services/userService';
import { useUserStore } from 'stores/userStore';
import { useRouter } from 'vue-router';

const { login } = useUserStore();

const users = ref<string[]>([]);
const router = useRouter();
async function impersonate(user: string) {
  try {
    await login(user, 'test', { ignorePermission: true });
    await router.push({ name: 'my-league'})
  } catch (error) {
    console.error('Failed to impersonate user:', error);
  }
}

void fetchUsers()
  .then((rows) => {
    users.value = rows.map((row) => row.username);
  })
  .catch((error) => {
    console.error('Failed to fetch users:', error);
  });

</script>
