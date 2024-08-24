<template>
  <q-card bordered class="q-mt-lg column q-mx-md">
    <q-card-section class="row justify-between q-pa-md text-h6 text-secondary">
      <slot name="title" />
    </q-card-section>
    <q-separator />
    <q-card-section>
      <slot name="content" />
    </q-card-section>
  </q-card>
</template>
