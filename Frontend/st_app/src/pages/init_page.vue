<template>Go To Login</template>

<script setup>
  import { useRouter } from 'vue-router';

  const router = useRouter();

  router.push({ name: 'test' });
</script>
