<template>
  <div class="q-pa-md">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6">
        <q-input
          v-model="note"
          label="Internal note (remember who you invited)"
          outlined
        />
      </div>
      <div class="col-12 col-sm-6">
        <KennerSelect
          v-if="allProfiles.length"
          v-model="selectedProfile"
          :options="profileOptions"
          label="Player Profile (optional)"
          outlined
          clearable
          use-input
          input-debounce="300"
          @filter="filterProfiles"
          :loading="loadingProfiles"
          option-value="id"
          option-label="profile_name"
          emit-value
          map-options
        />
      </div>
      <div class="col-12">
        <kenner-button
          color="positive"
          :loading="loading"
          @click="handleInvite"
        >
          Invite User
        </kenner-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';
import { useRouter } from 'vue-router';
import KennerSelect from 'components/base/KennerSelect.vue';

interface PlayerProfile {
  id: number;
  user: number | null;
  profile_name: string;
}

const $q = useQuasar();
const note = ref('');
const selectedProfile = ref<number | null>(null);
const profileOptions = ref<PlayerProfile[]>([]);
const allProfiles = ref<PlayerProfile[]>([]);
const loading = ref(false);
const loadingProfiles = ref(false);
const router = useRouter();

onMounted(async () => {
  await fetchProfiles();
});

const fetchProfiles = async () => {
  loadingProfiles.value = true;
  try {
    const { data } = await api.get('/user/profiles/?user__isnull=true/');
    allProfiles.value = Array.isArray(data) ? data : data.results || [];
    profileOptions.value = allProfiles.value;
  } catch (error) {
    console.error('Failed to fetch profiles:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load player profiles',
    });
  } finally {
    loadingProfiles.value = false;
  }
};

const filterProfiles = (val: string, update: (fn: () => void) => void) => {
  update(() => {
    if (val === '') {
      profileOptions.value = allProfiles.value;
    } else {
      const needle = val.toLowerCase();
      profileOptions.value = allProfiles.value.filter(
        (profile) => profile.profile_name?.toLowerCase().includes(needle)
      );
    }
  });
};

const handleInvite = async () => {
  loading.value = true;
  try {
    const payload: any = {
      label: note.value,
    };

    if (selectedProfile.value) {
      payload.player_profile = selectedProfile.value;
    }

    await api.post('/user/invitations/', payload);

    await router.push({ name: 'invitations' });
    $q.notify({
      type: 'positive',
      message: `User can now register. Internal note: ${note.value}`,
    });
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to invite user',
    });
    console.error('Invitation error:', error);
  } finally {
    loading.value = false;
  }
};
</script>
