<template>
  <div
    :class="`announcement announcement-border bg-${background} column q-pa-xs ${
      props.type === 'NEUTRAL' ? 'text-primary' : 'text-white'
    }`"
  >
    <div class="flex-center row">
      <slot name="title" />
    </div>
    <p class="flex-center row">
      <slot name="content" />
    </p>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ type: string }>();

const typeToBackgroundMap: { [key: string]: string } = {
  WINNER: 'secondary',
  INFO: 'info',
  REGISTER: 'accent',
  WARNING: 'negative',
  NEUTRAL: 'grey-2',
};

const background = computed(() => {
  return typeToBackgroundMap[props.type];
});
</script>

<style scoped lang="scss">
.announcement-border {
  border: 0px solid $secondary;
}
.announcement {
  background-color: #f9f9f9; /* Light background for contrast */
  color: #333; /* Neutral text color for readability */
  border: 1px solid #ddd; /* Subtle border for structure */
  border-radius: 5px; /* Soft corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Light shadow for depth */
  padding: 1rem 2rem; /* Spacious padding for comfort */
  text-align: center; /* Center the text */
  font-size: 1rem; /* Standard text size */
  font-weight: 500; /* Slightly bold for emphasis */
}

.announcement p {
  margin: 0; /* Remove default paragraph margins */
}

.announcement a {
  color: #007bff; /* Accent color for links */
  text-decoration: underline; /* Highlight links */
  font-weight: 600; /* Emphasize links */
}

.announcement a:hover {
  text-decoration: none; /* Subtle hover effect */
  color: #0056b3; /* Darker shade on hover */
}

</style>
