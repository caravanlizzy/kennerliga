<!-- eslint-disable vue/no-mutating-props -->
<template>
  <q-card flat bordered class="member-card shadow-1">
    <q-card-section class="q-pa-md">
      <div class="row items-center q-mb-md">
        <q-avatar size="sm" color="primary" text-color="white" class="q-mr-sm">
          {{ member.profile_name.charAt(0).toUpperCase() }}
        </q-avatar>
        <div class="text-subtitle1 text-weight-bold ellipsis">
          {{ member.profile_name }}
        </div>
      </div>

      <div class="column q-gutter-sm">
        <!-- Points (for points-based games) -->
        <KennerInput
          v-if="winConditionIsPoints"
          v-model.number="entry.points"
          type="number"
          step="any"
          inputmode="decimal"
          label="Points"
          class="points-input"
          :rules="[(v: number | null) => (v !== null && v !== '') || 'Required']"
        />

        <!-- Position (for non-points games) -->
        <div v-else-if="!winConditionIsOption && !winConditionIsPoints">
          <div class="text-caption text-grey-7 q-mb-xs">Final Position</div>
          <div class="row q-gutter-xs justify-center">
            <KennerButton
              v-for="pos in membersCount"
              :key="pos"
              size="sm"
              round
              unelevated
              :color="entry.position === pos ? 'primary' : 'grey-2'"
              :text-color="entry.position === pos ? 'white' : 'grey-9'"
              :label="String(pos)"
              class="position-btn shadow-1"
              @click="$emit('setPosition', member.id, pos)"
            />
          </div>
          <!-- Notes for position -->
          <KennerInput
            v-model="entry.notes"
            label="Position Note"
            placeholder="Explain position reason..."
            class="q-mt-sm"
            type="textarea"
            autogrow
            :input-style="{ minHeight: '40px' }"
          />
        </div>

        <!-- Factions by Level -->
        <div v-if="resultConfig?.is_asymmetric">
          <KennerSelect
            v-for="level in sortedFactionLevels"
            :key="level"
            v-model="entry.faction_ids[level]"
            :options="factionsByLevel[level]"
            option-label="name"
            option-value="id"
            emit-value
            map-options
            :label="level === 0 ? 'Faction' : `Level ${level} Faction`"
            clearable
            options-dense
            class="q-mb-xs"
          />
        </div>

        <!-- Starting position -->
        <div v-if="resultConfig?.has_starting_player_order">
          <div class="text-caption text-grey-7 q-mb-xs" style="font-size: 11px">
            Starting Position
          </div>
          <div class="row q-gutter-xs justify-center">
            <KennerButton
              v-for="pos in membersCount"
              :key="pos"
              size="sm"
              round
              :outline="entry.starting_position !== pos"
              :unelevated="entry.starting_position === pos"
              :color="entry.starting_position === pos ? 'secondary' : 'grey-5'"
              :text-color="entry.starting_position === pos ? 'white' : 'grey-7'"
              :label="String(pos)"
              class="starting-position-btn"
              @click="$emit('swapStartingPosition', member.id, pos)"
            />
          </div>
        </div>

        <!-- Starting Points -->
        <KennerInput
          v-if="
            resultConfig?.starting_points_system_code &&
            resultConfig.starting_points_system_code === 'DYNAMIC'
          "
          v-model.number="entry.starting_points"
          type="number"
          step="any"
          inputmode="decimal"
          label="Starting Points"
          class="q-mt-xs"
          :rules="[
            (v: number | null) => (v !== null && v !== '') || 'Required'
          ]"
        />

        <!-- Win Condition Option (only for OPTION-type WCs) -->
        <div
          v-if="winConditionIsOption && selectedWinCondition?.options?.length"
          class="q-mt-xs"
        >
          <div class="text-caption text-grey-7 q-mb-xs">
            {{ selectedWinCondition?.name || 'Outcome' }}
          </div>
          <q-option-group
            v-model="entry.win_condition_option"
            :options="
              (selectedWinCondition?.options ?? [])
                .slice()
                .sort((a, b) => a.order - b.order)
                .map((o) => ({ label: o.name, value: o.id }))
            "
            color="primary"
            type="radio"
            inline
          />
        </div>

        <!-- Tie-Breaker (Appears only when a tie needs resolving) -->
        <div v-if="tieBreakerRequired && needsTieBreaker" class="q-mt-sm">
          <KennerInput
            v-model.number="entry.tie_breaker_value"
            :label="requiredTieBreaker?.name || 'Tie-breaker Value'"
            type="number"
            inputmode="decimal"
            color="orange-8"
            :rules="[(v: number | null) => (v !== null && v !== '') || 'Tie-breaker value required']"
          >
            <template #prepend>
              <q-icon name="balance" size="xs" color="orange-9" />
            </template>
          </KennerInput>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import type {
  TLeagueMemberDto,
  TResultConfigDto,
  TTieBreakerDto,
  TWinConditionDto,
} from 'src/types';

export type Faction = { id: number; name: string; level: number };

export type FormDataEntry = {
  player_profile: number;
  selected_game: number;
  points: number | null;
  position: number | null;
  notes: string;
  starting_position: number | null;
  starting_points: number | null;
  faction_ids: Record<number, number | null>;
  tie_breaker_value: number | null;
  win_condition_option: number | null;
};

defineProps<{
  member: TLeagueMemberDto;
  entry: FormDataEntry;
  membersCount: number;
  winConditionIsPoints: boolean;
  winConditionIsOption: boolean;
  selectedWinCondition?: TWinConditionDto | null;
  resultConfig?: TResultConfigDto | null;
  sortedFactionLevels: number[];
  factionsByLevel: Record<number, Faction[]>;
  tieBreakerRequired: boolean;
  needsTieBreaker: boolean;
  requiredTieBreaker?: TTieBreakerDto | null;
}>();

defineEmits<{
  (e: 'setPosition', memberId: number, pos: number): void;
  (e: 'swapStartingPosition', memberId: number, pos: number): void;
}>();
</script>

<style scoped>
.member-card {
  border-radius: 10px;
  background: var(--kenner-card-bg);
}
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.position-btn {
  min-width: 40px;
  min-height: 40px;
  font-weight: 500;
  font-size: 15px;
}
</style>
