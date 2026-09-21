<template>
  <div class="q-pa-md">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6">
        <KennerInput
          v-model="note"
          label="Internal note (remember who you invited)"
        />
      </div>
      <div class="col-12 col-sm-6">
        <KennerSelect
          v-if="allProfiles.length"
          v-model="selectedProfile"
          :options="profileOptions"
          label="Player Profile (optional)"
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
        <KennerButton
          color="positive"
          :loading="loading"
          @click="handleInvite"
        >
          Invite User
        </KennerButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';
import { useRouter } from 'vue-router';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { createInvitation, fetchProfiles } from 'src/services/userService';
import type { TPlayerProfileDto } from 'src/types';

const $q = useQuasar();
const note = ref('');
const selectedProfile = ref<number | null>(null);
const profileOptions = ref<TPlayerProfileDto[]>([]);
const allProfiles = ref<TPlayerProfileDto[]>([]);
const loading = ref(false);
const loadingProfiles = ref(false);
const router = useRouter();

onMounted(async () => {
  await loadProfiles();
});

const loadProfiles = async () => {
  loadingProfiles.value = true;
  try {
    allProfiles.value = await fetchProfiles({ unlinkedOnly: true });
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
    const payload: { label: string; player_profile?: number } = {
      label: note.value,
    };

    if (selectedProfile.value) {
      payload.player_profile = selectedProfile.value;
    }

    await createInvitation(payload);

    await router.push({ name: 'invitations' });
    $q.notify({
      type: 'positive',
      message: `User can now sign up. Internal note: ${note.value}`,
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
