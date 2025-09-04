<template>
  <div class="row ">
    <q-chip
      v-for="user in users"
      :key="user"
      clickable
      dense
      square
      @click="impersonate(user, 'test')"
      color="orange-3"
      text-color="black"
      icon="person"
      class="cursor-pointer hover-shadow-2"
    >
      {{ user }}
    </q-chip>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { TUser } from 'src/types';
import { api } from 'boot/axios';
import { useUserStore } from 'stores/userStore';
import { useRouter } from 'vue-router';

const { login } = useUserStore();

const users = ref<TUser[]>([]);
const router = useRouter();
async function impersonate(user: string) {
  try {
    await login(user, 'test');
    await router.push({ name: 'my-league'})
  } catch (error) {
    console.error('Failed to impersonate user:', error);
  }
}

api
  .get('/user/users')
  .then((res) => {
    users.value = res.data.map((user: TUser) => user.username);
  })
  .catch((error) => {
    console.error('Failed to fetch users:', error);
  });

</script>
