// src/composables/dialog.ts
import { ref } from 'vue'

export type DialogType = 'primary' | 'warning' | 'error' | 'success'

const showDialog = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogType = ref<DialogType>('primary')
const confirmLabel = ref('OK')

const onConfirm = ref<null | (() => void | Promise<void>)>(null)
const onCancel = ref<null | (() => void | Promise<void>)>(null)

function resetDialog() {
  showDialog.value = false
  dialogTitle.value = ''
  dialogMessage.value = ''
  dialogType.value = 'primary'
  confirmLabel.value = 'OK'
  onConfirm.value = null
  onCancel.value = null
}

export function useDialog() {
  function setDialog(
    title: string,
    message: string,
    type: DialogType = 'primary',
    _onConfirm?: () => void | Promise<void>,
    _onCancel?: () => void | Promise<void>,
    _confirmLabel = 'OK'
  ) {
    showDialog.value = true
    dialogTitle.value = title
    dialogMessage.value = message
    dialogType.value = type
    confirmLabel.value = _confirmLabel
    onConfirm.value = _onConfirm ?? null
    onCancel.value = _onCancel ?? null
  }

  return {
    showDialog,
    dialogTitle,
    dialogMessage,
    dialogType,
    confirmLabel,
    onConfirm,
    onCancel,
    setDialog,
    resetDialog,
  }
}
