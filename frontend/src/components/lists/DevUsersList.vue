<template>
  <q-dialog v-model="showDialog">
    <q-card>
      <q-card-section>
        <q-item-label>Login as</q-item-label>
      </q-card-section>
      <q-card-section>
        <q-list>
          <q-item
            v-for="user in users"
            :key="user"
            clickable
            @click="impersonate(user, 'test')"
          >
            <q-item-section>{{ user }}</q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-section>
        <q-btn label="Close" @click="closeDialog" />
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import { TUser } from 'src/types';
import { api } from 'boot/axios';
import { useUserStore } from 'stores/userStore';

const { login } = useUserStore();
const props = withDefaults(defineProps<{ showImpersonate: boolean }>(), {
  showImpersonate: false,
});
const emit = defineEmits(['update:showImpersonate']);
const showDialog = ref(props.showImpersonate);

const users = ref<TUser[]>([]);

async function impersonate(user: string) {
  try {
    await login(user, 'test');
    closeDialog();
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

function closeDialog() {
  showDialog.value = false;
  emit('update:showImpersonate', false);
}
</script>
