<template>
  <q-dialog v-model="showDialog">
    <q-card class="q-pa-sm">
      <!-- Header with color -->
      <q-card-section
        class="text-h6 text-white"
        :class="`bg-${dialogType}`"
      >
        {{ dialogTitle }}
      </q-card-section>

      <!-- Message -->
      <q-card-section v-if="dialogMessage" class="q-mt-sm">
        {{ dialogMessage }}
      </q-card-section>

      <!-- Actions -->
      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancel"
          color="secondary"
          @click="handleCancel"
        />
        <q-btn
          flat
          :label="confirmLabel"
          :color="dialogType"
          @click="handleConfirm"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useDialog } from 'src/composables/dialog'

const {
  showDialog,
  dialogTitle,
  dialogMessage,
  dialogType,
  confirmLabel,
  onConfirm,
  onCancel,
  resetDialog
} = useDialog()

async function handleConfirm() {
  try {
    await onConfirm?.value?.()
  } finally {
    resetDialog()
  }
}

async function handleCancel() {
  try {
    await onCancel?.value?.()
  } finally {
    resetDialog()
  }
}
</script>
