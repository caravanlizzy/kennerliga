<template>
  <q-list class="row">
    <q-item
      v-for="user in users"
      :key="user"
      clickable
      @click="impersonate(user, 'test')"
      class="col-auto text-black"
    >
      <q-item-section>{{ user }}</q-item-section>
    </q-item>
  </q-list>
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
