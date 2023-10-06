<template>
  <q-page class="flex flex-center">
    <q-form class="full-width q-px-xl" @submit.prevent="login">
      <label class="text-info-input q-mb-sm">帳號</label>
      <q-input
        v-model="username"
        placeholder="請輸入帳號"
        outlined
        bg-color="white "
        :input-style="{ fontSize: '20px' }"
      >
        <template #prepend>
          <q-icon name="badge" />
        </template>
      </q-input>
      <div class="y-spacer"></div>
      <label class="text-info-input q-mb-sm">密碼</label>
      <q-input
        v-model="password"
        :type="isPwd ? 'password' : 'text'"
        placeholder="請輸入密碼"
        outlined
        bg-color="white"
        :input-style="{ fontSize: '20px' }"
      >
        <template #prepend>
          <q-icon name="lock" />
        </template>
        <template #append>
          <q-icon
            :name="isPwd ? 'visibility_off' : 'visibility'"
            class="cursor-pointer"
            @click="isPwd = !isPwd"
          />
        </template>
      </q-input>
      <div class="y-spacer"></div>
      <div class="row">
        <div class="col-12">
          <q-btn
            class="full-width"
            color="primary"
            label="登入"
            rounded
            size="xs"
            type="submit"
            style="font-size: 20px; font-weight: bold"
            @click="login()"
          ></q-btn>
        </div>
      </div>
      <div class="row q-mt-lg">
        <div class="col-12">
          <q-btn
            class="full-width"
            color="positive"
            label="以Google登入"
            no-caps
            rounded
            size="xs"
            style="font-size: 20px; font-weight: bold"
            @click="access_google()"
            v-if="!userGoogle"
          ></q-btn>
        </div>
      </div>
    </q-form>
  </q-page>
</template>

<script setup>
  import { ref, inject } from 'vue';
  import { useRouter } from 'vue-router';
  import { GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';
  import { auth } from '../firebase';
  import { ref as dbRef, get, set } from 'firebase/database';
  import { db } from '../firebase';
  import { useUserStore } from '../stores/current_user.js';

  const api = inject('api');
  const userGoogle = inject('userGoogle');
  const router = useRouter();

  const username = ref('');
  const password = ref('');
  const isPwd = ref(true);
  const userLanguage = navigator.language || navigator.userLanguage;

  const user_data = ref({
    uid: '',
    int_uid: 'null',
    username: '',
    email: '',
    language: userLanguage,
  });

  const login = () => {
    api
      .post('/login', {
        username: username.value,
        password: password.value,
      })
      .then(() => {
        console.log('login success');
        router.push({ name: 'lobby' });
      })
      .catch((err) => {
        console.log(err);
      });
  };

  // - Google登入
  const access_google = async () => {
    try {
      const provider = new GoogleAuthProvider();
      provider.setCustomParameters({ prompt: 'select_account' });

      const user = await signInWithPopup(auth, provider);

      user_data.value.uid = user.user.uid;
      user_data.value.username = user.user.displayName;
      user_data.value.email = user.user.email;
      user_data.value.language = userLanguage;

      await check_user_exist();

      console.log('login google success');
      router.push({ name: 'lobby' });
    } catch (err) {
      console.log(err);
    }
  };

  // - 檢查使用者是否存在於資料庫中
  const check_user_exist = async () => {
    try {
      const users_ref = dbRef(db, 'users');
      const users_snapshot = await get(users_ref);

      if (users_snapshot.exists()) {
        const userExists = Object.keys(users_snapshot.val()).some(
          (uid) => uid === user_data.value.uid,
        );

        if (userExists) {
          console.log('用戶已註冊');
        } else {
          console.log('用戶未註冊');
          await sing_up_user();
        }
      } else {
        console.log('在RTDB中找不到users');
      }
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };

  // - 註冊使用者資料
  const sing_up_user = async () => {
    try {
      const user_ref = dbRef(db, `users/${user_data.value.uid}`);
      await set(user_ref, user_data.value);
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };
</script>
