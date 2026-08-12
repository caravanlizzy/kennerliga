<template>
  <div v-if="user" class="profile-hero bg-primary text-white q-pa-md relative-position overflow-hidden">
    <div class="max-width-container q-mx-auto">
      <div class="hero-content row items-center q-col-gutter-md relative-position z-index-1">
        <div class="col-12 col-md-auto flex justify-center">
          <div class="avatar-wrapper shadow-24 rounded-borders bg-white q-pa-xs">
            <UserAvatar
              :display-username="user.username"
              size="100px"
              shape="rounded"
            />
          </div>
        </div>
        <div class="col-12 col-md column items-center items-md-start">
          <div class="row items-center q-gutter-x-md justify-center justify-md-start">
            <h1 class="text-h3 text-weight-bolder q-ma-none tracking-tighter">{{ user.username }}</h1>
            <q-badge v-if="user.admin" color="amber-8" class="text-dark text-weight-bolder q-px-sm" label="ADMIN" style="height: 24px; border-radius: 6px;" />
          </div>
          <div v-if="user.profile?.name" class="text-subtitle1 text-white text-opacity-90 text-weight-light q-mt-xs">
            {{ user.profile.name }}
          </div>
          <div class="row q-gutter-x-xl q-mt-sm justify-center justify-md-start">
            <div class="column items-center items-md-start">
              <div class="text-h4 text-weight-bolder">{{ leagueStats.totalLeagues }}</div>
              <div class="text-caption text-uppercase letter-spacing-2 text-white text-opacity-60">Leagues</div>
            </div>
            <q-separator vertical dark color="white" class="opacity-20 q-mx-md gt-xs" style="height: 30px" />
            <div class="column items-center items-md-start">
              <div class="text-h4 text-weight-bolder">{{ gameStatsCount }}</div>
              <div class="text-caption text-uppercase letter-spacing-2 text-white text-opacity-60">Games</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Decorative background elements -->
    <div class="hero-bg-overlay absolute-full" />
    <q-icon name="sports_esports" class="hero-watermark absolute-bottom-right text-white" size="300px" />
  </div>
</template>

<script setup lang="ts">
import UserAvatar from 'components/ui/UserAvatar.vue';
import { TUserDto } from 'src/types';

defineProps<{
  user: TUserDto;
  leagueStats: { totalLeagues: number };
  gameStatsCount: number;
}>();
</script>

<style scoped lang="scss">
.profile-hero {
  min-height: 160px;
  background: linear-gradient(135deg, var(--q-primary) 0%, #1e293b 100%);
  display: flex;
  align-items: center;
}

.max-width-container {
  max-width: var(--kenner-max-width);
  width: 100%;
}

.hero-bg-overlay {
  background-image: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-watermark {
  opacity: 0.04;
  right: -50px;
  bottom: -80px;
  transform: rotate(-15deg);
  pointer-events: none;
}

.avatar-wrapper {
  border-radius: 24px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  &:hover {
    box-shadow: 0 12px 30px rgba(0,0,0,0.3);
  }
}

.text-white-80 { color: rgba(255,255,255,0.8); }
.text-white-60 { color: rgba(255,255,255,0.6); }

.text-opacity-80 { opacity: 0.8; }
.text-opacity-60 { opacity: 0.6; }

.tracking-tighter { letter-spacing: -1.5px; }
.letter-spacing-2 { letter-spacing: 2px; }

@media (max-width: 599px) {
  .profile-hero { padding: 16px 16px !important; min-height: 140px; }
  .text-h3 { font-size: 2.2rem; }
  .text-h4 { font-size: 1.6rem; }
}

.z-index-1 { z-index: 1; }
</style>
