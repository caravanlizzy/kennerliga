<template>
  <div class="feedback-form q-pa-md">
    <q-form @submit="onSubmit" class="q-gutter-md">
      <q-input
        v-model="feedback"
        label="Your Feedback"
        type="textarea"
        filled
        :rules="[(val) => !!val || 'Feedback is required']"
      />

      <KennerButton label="Submit" type="submit" color="primary" class="q-mt-md" />
    </q-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import KennerButton from 'components/base/KennerButton.vue';

const $q = useQuasar();
const router = useRouter();

const feedback = ref('');
async function onSubmit() {
  try{
    await api.post('/user/feedback/', { message: feedback.value });
    $q.notify({
      title: 'Feedback Sent',
      message: 'Thank you for your feedback!',
      color: 'positive'
    })
    router.push({name: "home"})
  } catch(error){
    $q.notify({
      type: 'negative',
      message: 'Failed to send feedback'
    })
  }
}
</script>
