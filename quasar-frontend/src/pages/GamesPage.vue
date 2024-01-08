<template>
  <q-page>
    <div v-for="game in data" :key="game.id"> {{game.name}}</div>
  </q-page>
</template>


<script setup lang="ts">
import axios from 'axios';
import { ref, onMounted } from 'vue';


const data = ref([]);
const getData = async() => {
  const response = await axios({
      method: 'get',
      url: 'http://localhost:8000/games',
  })
  console.log({ response });
  data.value = response.data;
}

onMounted(async() => getData())



</script>
