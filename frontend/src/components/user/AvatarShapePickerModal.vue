<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <q-card class="avatar-customizer-dialog surface-card">
      <q-card-section class="row items-center q-pb-none q-pt-md q-px-md">
        <div class="row items-center q-gutter-x-sm">
          <q-icon name="palette" color="primary" size="24px" />
          <div class="text-h6 text-weight-bolder text-dark">
            Customize Avatar
          </div>
        </div>
        <q-space />
        <q-btn
          v-close-popup
          icon="close"
          flat
          round
          dense
          color="grey-7"
        />
      </q-card-section>

      <!-- Live Preview Banner -->
      <q-card-section class="preview-banner q-py-sm q-px-md flex flex-center">
        <div class="row items-center q-gutter-x-md">
          <UserAvatar
            :display-username="username"
            :shape="selectedShape"
            :color="selectedColor"
            size="64px"
          />
          <div class="column justify-center">
            <div class="text-subtitle1 text-weight-bolder text-dark">
              {{ username }}
            </div>
            <div class="row items-center q-gutter-x-xs text-caption text-grey-7">
              <span class="text-weight-medium text-capitalize">{{ selectedShape }}</span>
              <span>•</span>
              <span class="text-weight-medium">{{ currentColorName }}</span>
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Navigation Tabs -->
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey-7 customizer-tabs"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="shape" icon="interests" label="Shape" class="text-weight-medium" />
        <q-tab name="color" icon="palette" label="Color" class="text-weight-medium" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated class="customizer-tab-panels">
        <!-- Shape Selection Panel -->
        <q-tab-panel name="shape" class="q-pa-md shape-grid-section">
          <div class="row q-col-gutter-sm">
            <div
              v-for="opt in AVATAR_SHAPE_OPTIONS"
              :key="opt.id"
              class="col-6 col-sm-4 col-md-3"
            >
              <q-card
                flat
                class="shape-option-card cursor-pointer column items-center justify-center text-center q-pa-sm"
                :class="{
                  'shape-option-card--selected': selectedShape === opt.id,
                }"
                @click="selectShape(opt.id)"
              >
                <div class="avatar-preview-wrap relative-position q-mb-sm">
                  <UserAvatar
                    :display-username="username"
                    :shape="opt.id"
                    :color="selectedColor"
                    size="48px"
                  />
                  <div
                    v-if="selectedShape === opt.id"
                    class="selected-badge flex flex-center shadow-2"
                  >
                    <q-icon name="check" size="14px" color="white" />
                  </div>
                </div>

                <div class="text-subtitle2 text-weight-bold text-dark ellipsis full-width">
                  {{ opt.name }}
                </div>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- Color Selection Panel -->
        <q-tab-panel name="color" class="q-pa-md color-grid-section">
          <div class="row items-center justify-between q-mb-sm">
            <div class="text-subtitle2 text-weight-bold text-dark">
              Color Palette
            </div>
            <div class="row items-center q-gutter-x-sm">
              <q-btn
                flat
                dense
                no-caps
                size="sm"
                color="primary"
                icon="colorize"
                label="Custom Hex"
                class="custom-hex-btn"
              >
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-color
                    v-model="customColorInput"
                    no-header
                    default-view="palette"
                    @change="selectColor"
                  />
                </q-popup-proxy>
              </q-btn>
            </div>
          </div>

          <div class="row q-col-gutter-xs">
            <div
              v-for="c in AVATAR_COLOR_OPTIONS"
              :key="c.hex || 'auto'"
              class="col-6 col-sm-4 col-md-3"
            >
              <q-card
                flat
                class="color-option-card cursor-pointer row items-center q-pa-xs"
                :class="{
                  'color-option-card--selected': selectedColor.toLowerCase() === c.hex.toLowerCase(),
                }"
                @click="selectColor(c.hex)"
              >
                <div class="color-swatch flex flex-center q-mr-sm" :style="getSwatchStyle(c.hex)">
                  <q-icon
                    v-if="selectedColor.toLowerCase() === c.hex.toLowerCase()"
                    name="check"
                    size="16px"
                    :color="c.hex ? (getContrastColor(c.hex) === '#ffffff' ? 'white' : 'dark') : 'white'"
                  />
                  <q-icon
                    v-else-if="!c.hex"
                    name="auto_awesome"
                    size="14px"
                    color="white"
                  />
                </div>
                <div class="column ellipsis" style="min-width: 0; flex: 1;">
                  <span class="text-caption text-weight-bold text-dark ellipsis">{{ c.name }}</span>
                  <span class="text-caption text-grey-6 text-uppercase" style="font-size: 10px;">{{ c.hex || 'Auto' }}</span>
                </div>
              </q-card>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>

      <q-separator />

      <q-card-actions align="right" class="q-pa-sm q-px-md">
        <q-btn
          v-close-popup
          flat
          color="primary"
          label="Done"
          class="text-weight-bold"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Notify } from 'quasar';
import { useUserStore } from 'stores/userStore';
import UserAvatar from 'components/ui/UserAvatar.vue';
import {
  AvatarShape,
  AVATAR_SHAPE_OPTIONS,
  AVATAR_COLOR_OPTIONS,
  getContrastTextColor,
} from 'src/types/avatar';

const props = defineProps<{
  modelValue: boolean;
  username: string;
  currentShape?: AvatarShape;
  currentColor?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'shape-updated', shape: AvatarShape): void;
  (e: 'color-updated', color: string): void;
  (e: 'updated', payload: { shape: AvatarShape; color: string }): void;
}>();

const userStore = useUserStore();
const activeTab = ref<'shape' | 'color'>('shape');
const selectedShape = ref<AvatarShape>(props.currentShape || 'squircle');
const selectedColor = ref<string>(props.currentColor || '');
const customColorInput = ref<string>(props.currentColor || '#2563eb');

const currentColorName = computed(() => {
  if (!selectedColor.value) return 'Auto (Default)';
  const matched = AVATAR_COLOR_OPTIONS.find(
    (c) => c.hex.toLowerCase() === selectedColor.value.toLowerCase()
  );
  return matched ? matched.name : selectedColor.value.toUpperCase();
});

watch(
  () => props.currentShape,
  (newVal) => {
    if (newVal) selectedShape.value = newVal;
  },
  { immediate: true }
);

watch(
  () => props.currentColor,
  (newVal) => {
    if (newVal !== undefined) selectedColor.value = newVal || '';
  },
  { immediate: true }
);

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      selectedShape.value =
        props.currentShape ||
        (userStore.user?.avatar_shape as AvatarShape) ||
        'squircle';
      selectedColor.value =
        props.currentColor ??
        userStore.user?.avatar_color ??
        '';
      customColorInput.value = selectedColor.value || '#2563eb';
    }
  }
);

async function selectShape(shape: AvatarShape) {
  if (selectedShape.value === shape) return;
  selectedShape.value = shape;
  emit('shape-updated', shape);
  emit('updated', {
    shape,
    color: selectedColor.value,
  });

  const success = await userStore.changeAvatarShape(shape);
  if (!success) {
    Notify.create({
      type: 'negative',
      message: 'Failed to update avatar shape.',
    });
  }
}

async function selectColor(color: string) {
  const normalizedColor = color || '';
  if (selectedColor.value.toLowerCase() === normalizedColor.toLowerCase()) return;
  selectedColor.value = normalizedColor;
  customColorInput.value = normalizedColor || '#2563eb';
  emit('color-updated', normalizedColor);
  emit('updated', {
    shape: selectedShape.value,
    color: normalizedColor,
  });

  const success = await userStore.changeAvatarColor(normalizedColor);
  if (!success) {
    Notify.create({
      type: 'negative',
      message: 'Failed to update avatar color.',
    });
  }
}

function getSwatchStyle(hex: string) {
  if (!hex) {
    return {
      background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
    };
  }
  return {
    backgroundColor: hex,
  };
}

function getContrastColor(hex: string) {
  return getContrastTextColor(hex);
}
</script>

<style scoped lang="scss">
.avatar-customizer-dialog {
  width: 95vw;
  max-width: 680px;
  border-radius: 16px !important;
  background: #ffffff;
  overflow: hidden;
}

.preview-banner {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.customizer-tabs {
  background: #ffffff;
}

.customizer-tab-panels {
  background: #ffffff;
}

.shape-grid-section,
.color-grid-section {
  max-height: 55vh;
  overflow-y: auto;
}

.shape-option-card {
  border-radius: 12px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  background: #f8fafc;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: var(--q-primary);
    background: #f0fdf4;
    transform: translateY(-2px);
  }

  &--selected {
    border-color: var(--q-primary) !important;
    background: #ecfdf5 !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
  }
}

.color-option-card {
  border-radius: 10px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  background: #f8fafc;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  height: 52px;

  &:hover {
    border-color: var(--q-primary);
    background: #f0fdf4;
    transform: translateY(-1px);
  }

  &--selected {
    border-color: var(--q-primary) !important;
    background: #ecfdf5 !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
  }
}

.color-swatch {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.avatar-preview-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--q-primary);
  border: 2px solid #ffffff;
  z-index: 2;
}
</style>
