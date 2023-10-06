<template>
  <router-view />
</template>

<script>
  import { defineComponent } from 'vue';

  export default defineComponent({
    name: 'App',
  });
</script>

<script setup>
  import { ref, provide } from 'vue';
  import { onAuthStateChanged } from 'firebase/auth';
  import { auth } from './firebase';

  const userGoogle = ref(false);
  provide('userGoogle', userGoogle);

  onAuthStateChanged(auth, (user) => {
    userGoogle.value = user;
  });
</script>
