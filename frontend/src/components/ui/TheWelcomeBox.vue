<template>
  <div class="q-pa-md">
    <q-card bordered flat :class="['q-pa-lg', '']">
      <q-card-section class="text-h5 text-secondary">
        Kennerliga - eine Website. Aber warum denn nur?
      </q-card-section>

      <q-separator inset color="info" />
      <q-card-section>
        <div class="">
          <q-list class="text-primary row">
            <q-item
              :class="[isMobile ? 'col-12' : 'col-6']"
              v-for="item of items"
              :key="item"
            >
              <q-item-section>
                <div class="">
                  <q-icon left label="item" name="circle" color="info" />
                  <span class="">
                    {{ item }}
                  </span>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';

const { isMobile } = useResponsive();

const items: string[] = [
  'Excel Tabellen Goodbye',
  'Zentrale Liste aller Ergebnisse',
  'Ergebnisse werden hier hochgeladen',
  'Neue Saison und Ligen werden automatisch angelegt',
  'Spielauswahl und Bannen im Browser',
  'Hall of Fame',
  'Awards zum Beispiel für best game picker',
  'Kennerliga Chat',
];
</script>

<style scoped lang="scss">
.welcome-box {
  border: 2px solid $secondary;
}
</style>
