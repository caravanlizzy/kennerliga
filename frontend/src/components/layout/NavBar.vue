<template>
  <q-btn flat @click="goHome({name: 'home'})">
    <q-chip size="md" color="secondary" text-color="white">
      <q-icon name="psychology" class="q-mr-md" size="xs" color="white"></q-icon>
      Kennerliga
    </q-chip>
  </q-btn>
  <q-toolbar-title class="text-primary">
    <!--      <h6 class="text-italic" > Kennerliga </h6>-->
  </q-toolbar-title>
  <DevUsersList v-show="showDev"/>
  <KennerButton
    @click="() => showDev = !showDev"
    color="info"
    rounded
    dense
    flat
  > Dev</KennerButton>

  <KennerButton :to="{name: 'my-league'}" v-if="isAuthenticated" flat color="positive" icon="sports_esports">
    <KennerTooltip> Meine Liga </KennerTooltip>
  </KennerButton>
  <UserName v-if="isAuthenticated"/>
  <KennerButton color="primary" v-if="isAuthenticated" flat icon="menu" @click="onToggle"/>
  <KennerButton color="primary" v-else flat icon="login" :to="{name:'login'}"/>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import UserName from 'components/ui/UserName.vue';
import { useRouter } from 'vue-router';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import DevUsersList from 'components/lists/DevUsersList.vue';
import { ref } from 'vue';

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const router = useRouter();
const { isAuthenticated } = storeToRefs(store);
const showDev = ref(false);

function goHome() {
  router.push({ name: 'home' });
}

</script>
