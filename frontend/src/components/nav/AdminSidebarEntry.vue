<template>
  <div>
    <q-item dark clickable :to="{ name: routeName }">
      <q-item-section v-if="icon" avatar>
        <q-icon :name="icon" />
      </q-item-section>

      <q-item-section>
        <q-item-label>{{ title }}</q-item-label>
        <q-item-label caption>{{ caption }}</q-item-label>
      </q-item-section>
    </q-item>
  </div>
</template>

<script setup lang="ts">

export interface AdminLinkProps {
  title: string;
  caption?: string;
  routeName?: string;
  icon?: string;
}
withDefaults(defineProps<AdminLinkProps>(), {
  title: '',
  caption: '',
  routeName: '',
  icon: '',
});
</script>
