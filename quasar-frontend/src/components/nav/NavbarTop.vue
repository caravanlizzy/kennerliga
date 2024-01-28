<template>
  <div class="q-px-md q-py-xs q-gutter-sm bg-black">
    <q-breadcrumbs separator="-->" class="text-secondary" active-color="secondary">
      <template v-slot:separator>
        <q-icon
          aize="1.2em"
          name="arrow_right"
          color="secondary"
        />
      </template>
      <q-breadcrumbs-el icon="home" :to="{ name:'home' }"/>
      <q-breadcrumbs-el label="Components" icon="widgets" />
      <q-breadcrumbs-el label="Breadcrumbs" icon="navigation" />
    </q-breadcrumbs>
  </div>
</template>

<script setup lang="ts">

</script>
<style scoped>

</style>
