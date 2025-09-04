import { defineStore } from 'pinia';
import { ref } from 'vue';

const isDev = ref(false);

export const useUiStore = defineStore('ui', () => {
    function showDev(){
      isDev.value = true;
    }
    function hideDev(){
      isDev.value = false;
    }

    function toggleDev(){
      isDev.value = !isDev.value;
    }
    return { isDev, showDev, hideDev, toggleDev }
})
