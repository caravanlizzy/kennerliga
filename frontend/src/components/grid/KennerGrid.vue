<template>
  <div class="grid-container">
    <div class="grid-item" v-for="(item, index) in items" :key="index" :class="{'highlighted': item.isHighlighted}">
      <slot :item="item"/>
    </div>
  </div>
</template>

<style scoped lang="scss">
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 0px;
}

.grid-item {
  padding: 20px;
  border: 1px solid #fceedb;
  //border-radius: 8px;
}

.highlighted {
  background: #f8f0ed;
}

</style>


<script setup lang="ts">
defineProps<{ items: any[] }>();
</script>
