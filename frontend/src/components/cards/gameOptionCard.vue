<template>
  <q-card class=" q-mt-lg column q-mx-md">
    <q-card-section class="row justify-between bg-primary text-white q-pa-md">
      <slot name="cardHeader"/>
    </q-card-section>
    <q-card-section>
      <slot name="cardBody"/>
    </q-card-section>
  </q-card>
</template>
