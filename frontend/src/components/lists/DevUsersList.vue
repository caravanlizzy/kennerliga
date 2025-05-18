<template>
  <q-list class="row">
    <q-item
      v-for="user in users"
      :key="user"
      clickable
      @click="impersonate(user, 'test')"
      class="col-auto"
    >
      <q-item-section>{{ user }}</q-item-section>
    </q-item>
  </q-list>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import { TUser } from 'src/types';
import { api } from 'boot/axios';
import { useUserStore } from 'stores/userStore';
import { useRouter } from 'vue-router';

const { login } = useUserStore();
const props = withDefaults(defineProps<{ showImpersonate: boolean }>(), {
  showImpersonate: false,
});
const showDialog = ref(props.showImpersonate);
const router = useRouter();

const users = ref<TUser[]>([]);

async function impersonate(user: string) {
  try {
    await login(user, 'test');
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

watch(
  () => props.showImpersonate,
  (newVal) => {
    showDialog.value = newVal;
  }
);

</script>
