<template>
  <div class="row ">
    <q-chip
      v-for="user in users"
      :key="user"
      clickable
      square
      color="primary"
      @click="impersonate(user, 'test')"
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
import { TUserDto } from 'src/types';
import { api } from 'boot/axios';
import { useUserStore } from 'stores/userStore';
import { useRouter } from 'vue-router';

const { login } = useUserStore();

const users = ref<TUserDto[]>([]);
const router = useRouter();
async function impersonate(user: string) {
  try {
    await login(user, 'test', { ignorePermission: true });
    await router.push({ name: 'my-league'})
  } catch (error) {
    console.error('Failed to impersonate user:', error);
  }
}

api
  .get('/user/users')
  .then((res) => {
    users.value = res.data.map((user: TUserDto) => user.username);
  })
  .catch((error) => {
    console.error('Failed to fetch users:', error);
  });

</script>
