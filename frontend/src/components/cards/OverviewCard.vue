<template>
  <q-card bordered class="q-mt-lg column q-mx-md ">
    <q-card-section class="row justify-center q-pa-md text-h6">
      <div>
        <slot name="cardHeader" />
      </div>
    </q-card-section>
    <q-card-section>
      <slot name="cardBody"/>
    </q-card-section>
  </q-card>
</template>

<style scoped>
</style>
