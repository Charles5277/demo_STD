<template>
  <q-layout view="hHh lpR lFr">
    <q-header reveal bordered class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          dense
          flat
          round
          icon="menu"
          size="lg"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title
          class="text-center text-weight-bold q-my-md q-pa-none"
          style="font-size: 25px"
        >
          即時同步語音翻譯系統
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      side="left"
      behavior="mobile"
      :width="300"
      style="
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      "
    >
      <q-field borderless bg-color="primary" style="align-items: center">
        <template #control>
          <div
            class="text-white q-ml-md"
            style="font-size: 20px; font-weight: bold"
          >
            功能選單
          </div>
        </template>
      </q-field>
      <q-list bordered class="full-height" style="position: relative">
        <q-item v-if="!userGoogle" clickable v-ripple :to="{ name: 'login' }">
          <q-item-section avatar>
            <q-avatar color="primary" text-color="white" icon="home" />
          </q-item-section>

          <q-item-section>登入</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'lobby' }">
          <q-item-section avatar>
            <q-avatar color="positive" text-color="white" icon="key" />
          </q-item-section>

          <q-item-section>免驗證存取</q-item-section>
        </q-item>

        <q-item
          v-if="userGoogle"
          clickable
          v-ripple
          @click="dialog_check_logout = true"
          class="full-width"
          style="position: absolute; bottom: 0"
        >
          <q-item-section avatar>
            <q-avatar color="negative" text-color="white" icon="logout" />
          </q-item-section>
          <q-item-section>登出</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
    <q-dialog v-model="dialog_check_logout" persistent>
      <q-card style="width: 20vw">
        <q-card-section
          class="row"
          style="display: flex; justify-content: center; align-items: center"
        >
          <q-icon name="info" size="sm" class="q-mr-xs" />
          <span class="text-dialog">您確定要登出嗎</span>
        </q-card-section>

        <q-card-actions align="center" class="q-mt-md">
          <q-btn
            filled
            label="返回"
            color="primary"
            class="q-mx-md"
            v-close-popup
          />
          <q-btn
            filled
            label="登出"
            color="negative"
            class="q-mx-md"
            v-close-popup
            @click="logout_google"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
  import { ref, provide, inject } from 'vue';
  import { useRouter } from 'vue-router';

  const router = useRouter();
  const confirm_leave = ref(true);
  provide('contentChanged', confirm_leave);

  const leftDrawerOpen = ref(false);
  const dialog_check_logout = ref(false);

  const toggleLeftDrawer = () => {
    leftDrawerOpen.value = !leftDrawerOpen.value;
  };
</script>
