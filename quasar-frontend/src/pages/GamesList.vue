<template>
    <KennerligaTable flat title="Spiele" :rows="data" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>


<script setup lang="ts">
import axios from 'axios';
import { ref, onMounted } from 'vue';
import KennerligaTable from 'components/KennerligaTable.vue';

console.log(process.env);
const data = ref([]);
const getData = async () => {
  const response = await axios({
    method: 'get',
    url: `${process.env.API_URL}games/`,
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
    field: x => x.name,
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
