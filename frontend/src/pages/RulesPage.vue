<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%" class="q-px-sm">
      <!-- Header / Hero -->
      <div class="rules-hero-card q-pa-lg q-mb-lg row items-center justify-between">
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="gavel" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              Tournament Rules
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Guidelines, formats, scoring structures, and seasonal timeline.
          </div>
        </div>
      </div>

      <div class="row q-col-gutter-lg">
        <!-- Purpose -->
        <div class="col-12">
          <q-card flat class="rules-card q-pa-md">
            <q-card-section>
              <div class="text-subtitle1 text-weight-bold q-mb-xs text-dark row items-center q-gutter-x-xs">
                <q-icon name="emoji_objects" color="primary" size="20px" />
                <span>Purpose of the League</span>
              </div>
              <div class="text-body2 text-grey-8">
                Designed for experienced board gamers to demonstrate consistent, high-level performance across a wide variety of games. Success requires adaptability, rules mastery, and strategic depth.
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Tournament Structure -->
        <div class="col-12 col-md-6">
          <ContentSection title="Structure" icon="account_tree" color="primary" :bordered="false">
            <q-list dense>
              <q-item class="q-px-none">
                <q-item-section avatar><q-icon name="calendar_today" color="primary" size="20px" /></q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Seasons</q-item-label>
                  <q-item-label caption>Monthly cycles, normally 12 per year. Requires min. 6 players.</q-item-label>
                </q-item-section>
              </q-item>
              <q-item class="q-px-none">
                <q-item-section avatar><q-icon name="devices" color="primary" size="20px" /></q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Platforms</q-item-label>
                  <q-item-label caption>Yucata, BoardGameArena, boardgamers.space</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </ContentSection>
        </div>

        <!-- League System -->
        <div class="col-12 col-md-6">
          <ContentSection title="League System" icon="reorder" color="secondary" :bordered="false">
            <q-list dense>
              <q-item class="q-px-none">
                <q-item-section avatar><q-icon name="groups" color="secondary" size="20px" /></q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Composition</q-item-label>
                  <q-item-label caption>Groups of 4 players (L1 is always 4). New players start at the bottom.</q-item-label>
                </q-item-section>
              </q-item>
              <q-item class="q-px-none">
                <q-item-section avatar><q-icon name="trending_up" color="secondary" size="20px" /></q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Promotion & Relegation</q-item-label>
                  <q-item-label caption>1st place moves up, last place moves down.</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </ContentSection>
        </div>

        <!-- Timeline & Selection -->
        <div class="col-12">
          <ContentSection title="Monthly Timeline & Game Selection" icon="schedule" color="accent" :bordered="false">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <div class="text-subtitle2 text-weight-bold q-mb-sm text-dark">Timeline</div>
                <ul class="q-pl-md text-body2 text-grey-8">
                  <li><strong>Days 1–2:</strong> Game selection</li>
                  <li><strong>Days 3–9:</strong> Learning/testing phase</li>
                  <li><strong>Day 10–End:</strong> Playing phase (must finish by end of month)</li>
                </ul>
              </div>
              <div class="col-12 col-sm-6">
                <div class="text-subtitle2 text-weight-bold q-mb-sm text-dark">Selection Rounds</div>
                <ol class="q-pl-md text-body2 text-grey-8">
                  <li><strong>Nomination:</strong> Players nominate games in order.</li>
                  <li><strong>Ban Phase:</strong> Players may ban one opponent's game.</li>
                  <li><strong>Replacement:</strong> Banned games are replaced (replacements cannot be banned).</li>
                </ol>
              </div>
            </div>
          </ContentSection>
        </div>

        <!-- Execution & Reporting -->
        <div class="col-12 col-md-6">
          <ContentSection title="Execution" icon="play_circle" color="warning" :bordered="false">
            <q-list dense>
              <q-item class="q-px-none">
                <q-item-section>
                  <q-item-label class="text-weight-bold">Responsibilities</q-item-label>
                  <q-item-label caption>Create your selected game by Day 9. Ensure everyone accepts invitations.</q-item-label>
                </q-item-section>
              </q-item>
              <q-item class="q-px-none">
                <q-item-section>
                  <q-item-label class="text-weight-bold">Reporting Results</q-item-label>
                  <q-item-label caption>Winner must report results within 24h of completion.</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </ContentSection>
        </div>

        <!-- Scoring -->
        <div class="col-12 col-md-6">
          <ContentSection title="Scoring" icon="score" color="info" :bordered="false">
            <div class="text-body2 text-grey-8 q-mb-sm">Points based on player count:</div>
            <q-markup-table flat bordered dense class="scoring-table q-mb-sm rounded-borders">
              <thead>
                <tr class="bg-grey-1">
                  <th class="text-left text-weight-bold">Players</th>
                  <th class="text-left text-weight-bold">Points (1st / 2nd / 3rd / 4th)</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>4</td><td><span class="text-weight-bold text-primary">6</span> / 3 / 1 / 0</td></tr>
                <tr><td>3</td><td><span class="text-weight-bold text-primary">6</span> / 3 / 0</td></tr>
                <tr><td>2</td><td><span class="text-weight-bold text-primary">6</span> / 0</td></tr>
              </tbody>
            </q-markup-table>
            <div class="text-caption text-grey-7 italic">Ties split points evenly. Victory point % used as tiebreaker.</div>
          </ContentSection>
        </div>

        <!-- Hall of Fame -->
        <div class="col-12">
          <ContentSection title="Hall of Fame & Cup" icon="emoji_events" color="amber-9" :bordered="false">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <div class="text-subtitle2 text-weight-bold q-mb-xs text-dark">Kenner Cup</div>
                <div class="text-body2 text-grey-8">Awarded to the player with the most L1 titles in a calendar year.</div>
              </div>
              <div class="col-12 col-sm-6">
                <div class="text-subtitle2 text-weight-bold q-mb-xs text-dark">Ranking Priority</div>
                <div class="text-body2 text-grey-8">Historical rank is based on L1 titles, then runner-ups, then L1 placements.</div>
              </div>
            </div>
          </ContentSection>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import ContentSection from 'src/components/base/ContentSection.vue';
</script>

<style scoped lang="scss">
.rules-hero-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.rules-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.scoring-table {
  border: 1px solid rgba(0, 0, 0, 0.06);
}

ul, ol {
  margin: 0;
}
</style>
