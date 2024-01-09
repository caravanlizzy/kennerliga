<template>
  <div class="q-pa-md">
    <!--  <div v-for="game in data" :key="game.id"> {{game.name}}</div> -->
    <q-table flat title="Spiele" :rows="data" :columns="columns"/>
  </div>
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

const columns = [
  {
    name: "game",
    required: true,
    align: 'left',
    label: "Spiel",
    field: data => data.name,
    sortable: true,
  },
  {
    name: "platform",
    label: "Plattform",
    required: false,
    align: 'center',
    field: x => x.platform,
    sortable: true,
  }
]



</script>
