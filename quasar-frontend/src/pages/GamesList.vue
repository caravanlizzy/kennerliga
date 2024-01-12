<template>
    <q-table flat title="Spiele" :rows="data" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>


<script setup lang="ts">
import axios from 'axios';
import { ref, onMounted } from 'vue';


const data = ref([]);
const getData = async () => {
  const response = await axios({
    method: 'get',
    url: 'http://localhost:8000/games',
  })
  console.log({ response });
  data.value = response.data;
}

onMounted(async () => getData())

const columns = [
  {
    name: 'game',
    required: true,
    align: 'left',
    label: 'Spiel',
    field: data => data.name,
    sortable: true,
  },
  {
    name: 'platform',
    label: 'Plattform',
    required: false,
    align: 'center',
    field: x => x.platform,
    sortable: true,
  }
]


</script>
