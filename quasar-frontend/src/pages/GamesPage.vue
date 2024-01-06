<template>
  <div>test</div>
</template>


<script setup lang="ts">
import axios from 'axios';

const response = await axios({
    method: 'get',
    url: 'http://localhost:8000/games',
    headers: {
     'Access-Control-Allow-Origin' : '*'
    }
})

console.log(response);

</script>
