<template>
  <q-table flat title="SpielerInnen" :rows="data" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>

<script setup lang="ts">
import axios from'axios';
import {ref, onMounted} from "vue";

const data = ref([]);
const getData = async () => {
  const response = await axios({
    method:'get',
    url: 'http://localhost:8000/users',
  })
  data.value = response.data;
}

onMounted(async () => getData())


const columns = [
  {
    name: 'user',
    required: true,
    align: 'left',
    label: 'Name',
    field: x => x.username,
    sortable: true,
  },
  {
    name: 'bga_name',
    label: 'BGA Name',
    required: false,
    align: 'center',
    field: x => x.bga_name,
    sortable: true,
  },
  {
    name: 'email',
    label: 'Email',
    required: false,
    align: 'center',
    field: x => x.email,
    sortable: true,
  }
]
</script>
