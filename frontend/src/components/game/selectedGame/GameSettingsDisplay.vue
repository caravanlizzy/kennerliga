<!-- GameSettingsOptionsDisplay.vue -->
<template>
  <div class="game-settings-options">
    <div
      v-for="selected in selectedOptions"
      :key="selected.id"
      class="option-row"
    >
      <!-- Option Name -->
      <div class="option-name">
        {{ selected.game_option.name }}
      </div>

      <!-- Value / Choice -->
      <div class="option-value">
        <!-- mit Choices -->
        <template v-if="selected.game_option.has_choices">
          <span class="choice-pill">
            {{ getChoiceLabel(selected) }}
          </span>
        </template>

        <!-- Boolean true/false -->
        <template v-else>
          <span
            class="boolean-pill"
            :class="{
              'boolean-true': selected.value === true,
              'boolean-false': selected.value === false,
              'boolean-null': selected.value === null
            }"
          >
            <!-- Text kannst du natürlich anpassen -->
            <span v-if="selected.value === true">On</span>
            <span v-else-if="selected.value === false">Off</span>
            <span v-else>–</span>
          </span>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface GameOption {
  id: number
  name: string
  has_choices: boolean
  // weitere Felder, falls nötig:
  only_if_value: boolean | null
  game: number
  only_if_option: number | null
  only_if_choice: number | null
}

interface Choice {
  id: number
  // passe das an dein echtes Modell an
  name?: string
  label?: string
  // ...
}

interface SelectedOption {
  id: number
  game_option: GameOption
  choice: Choice | null
  value: boolean | null
}

const props = defineProps<{
  selectedOptions: SelectedOption[]
}>()

/**
 * Liefert den anzuzeigenden Text für eine Choice-Option
 */
const getChoiceLabel = (selected: SelectedOption): string => {
  if (!selected.choice) {
    return 'Keine Auswahl'
  }

  // Passen je nach Choice-Modell an:
  return selected.choice.name ?? selected.choice.label ?? `Choice #${selected.choice.id}`
}
</script>

<style scoped>
.game-settings-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Eine Reihe mit Name links, Wert rechts */
.option-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.6rem;
  border-radius: 0.4rem;
  background: #f6f6f8;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.option-name {
  font-weight: 500;
  flex: 1 1 auto;
  min-width: 0;
}

/* rechter Teil (Wert) */
.option-value {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

/* On small screens, force wrap to 2 rows */
@media (max-width: 600px) {
  .option-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .option-value {
    width: 100%;
    justify-content: flex-start;
  }
}

/* Badge für Boolean-Wert */
.boolean-pill {
  padding: 0.1rem 0.6rem;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid transparent;
}

.boolean-true {
  background: #e1f8e6;
  border-color: #7ac28a;
}

.boolean-false {
  background: #fde3e3;
  border-color: #e58a8a;
}

.boolean-null {
  background: #eeeeee;
  border-color: #cccccc;
}

/* Badge für Choice-Wert */
.choice-pill {
  padding: 0.1rem 0.6rem;
  border-radius: 999px;
  font-size: 0.85rem;
  background: #e4ecff;
  border: 1px solid #9db4ff;
}
</style>
