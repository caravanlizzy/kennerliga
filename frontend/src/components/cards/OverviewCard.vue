<template>
  <q-card bordered class="q-mt-lg column q-mx-md">
    <q-card-section class="row justify-between q-pa-md text-h6 text-secondary">
      <slot name="cardHeader" />
    </q-card-section>
    <q-separator />
    <q-card-section>
      <slot name="cardBody" />
    </q-card-section>
  </q-card>
</template>
