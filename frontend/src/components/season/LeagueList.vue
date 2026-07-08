<template>
  <q-card
    flat
    class="league-card"
    :class="{ 'league-card--clickable': isAdmin, 'league-card--complete': league.is_completed }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <!-- Header -->
    <div class="q-px-md q-py-md row items-center no-wrap q-gutter-x-md">
      <div class="league-avatar" :class="`league-avatar--lvl${league.level}`">
        <span>L{{ league.level }}</span>
      </div>
      <div class="col">
        <div class="text-subtitle1 text-weight-bolder league-card__title">League {{ league.level }}</div>
      </div>
      <div class="col-auto column items-end q-gutter-y-xs">
        <div class="member-pill">
          <q-icon name="group" size="14px" class="q-mr-xs" />
          <span>{{ league.members?.length || 0 }}</span>
        </div>
        <div v-if="league.is_completed" class="complete-pill">
          <q-icon name="check_circle" size="12px" class="q-mr-xs" />
          <span>COMPLETE</span>
        </div>
        <KennerButton
          v-if="isAdmin"
          flat
          dense
          no-caps
          color="primary"
          icon="settings"
          size="sm"
          label="Manage"
          class="manage-btn"
          @click.stop="goToLeague(league)"
        />
      </div>
    </div>

    <div class="league-card__divider" />

    <!-- Members -->
    <div class="q-px-md q-pt-sm q-pb-md">
      <div class="text-caption text-grey-6 q-mb-xs text-weight-medium">Users</div>
      <div v-if="league.members?.length" class="row q-col-gutter-xs">
        <q-chip
          v-for="m in league.members"
          :key="m.id"
          dense
          clickable
          icon="person"
          class="member-chip q-mr-xs q-mb-xs"
          @click.stop
        >
          {{ m.profile_name }}
        </q-chip>
      </div>
      <div v-else class="text-caption text-grey-5 italic">No users assigned</div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { TLeagueDto } from 'src/types';
import { useRouter } from 'vue-router';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{ league: TLeagueDto }>();

const router = useRouter();
const { isAdmin } = storeToRefs(useUserStore());

function goToLeague(league: TLeagueDto) {
  router.push({
    name: 'league-manager',
    params: { id: league.season, leagueId: league.id },
  });
}
</script>

<style scoped lang="scss">
.league-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.league-card--clickable {
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(54, 64, 88, 0.1);
    border-color: rgba(54, 64, 88, 0.16);
  }
}

.league-card--complete {
  border-color: rgba(33, 186, 69, 0.25);
}

.league-card__title {
  color: #1f2937;
  letter-spacing: -0.2px;
}

.league-card__divider {
  height: 1px;
  background: linear-gradient(to right, transparent 0%, rgba(54, 64, 88, 0.1) 50%, transparent 100%);
}

.league-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: -0.3px;
  color: #fff;
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-accent) 100%);
  box-shadow: 0 4px 12px rgba(54, 64, 88, 0.18);
  flex: 0 0 auto;
}

.league-avatar--lvl1 {
  background: linear-gradient(135deg, #ffd54f 0%, #ffb300 100%);
  color: #5d4037;
  box-shadow: 0 4px 12px rgba(255, 179, 0, 0.35);
}

.league-avatar--lvl2 {
  background: linear-gradient(135deg, #eceff1 0%, #b0bec5 100%);
  color: #37474f;
  box-shadow: 0 4px 12px rgba(176, 190, 197, 0.4);
}

.league-avatar--lvl3 {
  background: linear-gradient(135deg, #d7a17a 0%, #a1683a 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(161, 104, 58, 0.35);
}

.member-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.06);
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.complete-pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(33, 186, 69, 0.15) 0%, rgba(33, 186, 69, 0.05) 100%);
  color: #1b8a3a;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  border: 1px solid rgba(33, 186, 69, 0.25);
}

.manage-btn {
  border-radius: 8px;
  font-weight: 600;
}

.member-chip {
  background: rgba(54, 64, 88, 0.05) !important;
  border: 1px solid rgba(54, 64, 88, 0.06);
  color: #334155;
  font-weight: 500;
  transition: background 0.2s ease, border-color 0.2s ease;

  &:hover {
    background: rgba(54, 64, 88, 0.1) !important;
    border-color: rgba(54, 64, 88, 0.12);
  }
}

:global(.body--dark) .league-card {
  background: rgba(30, 30, 30, 0.8);
  border-color: rgba(255, 255, 255, 0.08);
}

:global(.body--dark) .league-card__header {
  background: linear-gradient(135deg, rgba(40, 40, 40, 0.6) 0%, rgba(30, 30, 30, 0.3) 100%);
}

:global(.body--dark) .league-card__title {
  color: #ececec;
}

:global(.body--dark) .member-pill {
  background: rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

:global(.body--dark) .member-chip {
  background: rgba(255, 255, 255, 0.06) !important;
  border-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;

  &:hover {
    background: rgba(255, 255, 255, 0.12) !important;
  }
}
</style>
