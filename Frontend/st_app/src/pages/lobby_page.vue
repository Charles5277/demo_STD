<template>
  <q-page class="flex flex-center">
    <div>
      <q-form class="full-width q-px-xl" @submit="check_cr()">
        <div
          class="full-width text-center q-mb-md"
          style="font-size: 32px; font-weight: bold"
        >
          聊天室
        </div>
        <label class="text-info-input q-mb-sm">房號</label>
        <q-input
          v-model="form_cr.room_id"
          placeholder="請輸入房號"
          outlined
          bg-color="white "
          :input-style="{ fontSize: '20px' }"
        >
          <template #prepend>
            <q-icon name="meeting_room" />
          </template>
        </q-input>
        <div class="y-spacer"></div>
        <label class="text-info-input q-mb-sm">密碼</label>
        <q-input
          v-model="form_cr.password"
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
        <q-btn
          class="full-width"
          color="primary"
          label="加入"
          rounded
          size="xs"
          type="submit"
          style="font-size: 20px; font-weight: bold"
        ></q-btn>
        <div class="y-spacer"></div>
        <q-btn
          class="full-width"
          color="positive"
          label="創建房間"
          rounded
          size="xs"
          style="font-size: 20px; font-weight: bold"
          :to="{ name: 'room' }"
        ></q-btn>
      </q-form>
    </div>
    <div>
      <ul>
        <!-- <li v-for="todo in todos" :key="todo.id">
          <span>{{ todo.text }}</span>
        </li> -->
      </ul>
    </div>
  </q-page>
</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { ref as dbRef, set, get, push, update } from 'firebase/database';
  import { db, auth } from '../firebase';
  import { onAuthStateChanged } from 'firebase/auth';

  const router = useRouter();

  const form_cr = ref({
    room_id: '', // 房號
    password: '', // 密碼
  });
  const isPwd = ref(false); // 是否顯示密碼

  const user_data = ref({
    uid: '',
    int_uid: '',
    language: '',
  });

  const check_cr = async () => {
    try {
      const cr_ref = dbRef(db, 'chatrooms');
      const cr_snapshot = await get(cr_ref);
      if (cr_snapshot.exists()) {
        const cr_exists = Object.keys(cr_snapshot.val()).some(
          (room_id) => (room_id) => room_id === form_cr.value.room_id,
        );
        if (cr_exists) {
          join_cr();
        } else {
          console.log('此聊天室不存在');
        }
      } else {
        console.log('在RTDB中找不到chatroom');
      }
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };

  // - 加入聊天室
  const join_cr = async () => {
    try {
      const cr_ref = dbRef(db, `chatrooms/${form_cr.value.room_id}`);
      const cr_snapshot = await get(cr_ref);

      const cr_password = cr_snapshot.val().password;
      if (cr_password === form_cr.value.password) {
        console.log('密碼正確');
        await update(
          // - 補寫int_uid回users
          dbRef(db, `users/${user_data.value.uid}`),
          {
            int_uid: user_data.value.int_uid,
          },
        );
        await set(
          // - 將聊天室members清單加入當前user資料
          dbRef(
            db,
            `chatrooms/${form_cr.value.room_id}/members/${user_data.value.uid}`,
          ),
          {
            uid: user_data.value.uid,
            int_uid: user_data.value.int_uid,
            language: user_data.value.language,
          },
        );
        await set(
          // - 將使用者狀態加入當前聊天室
          dbRef(db, `user_status/${user_data.value.uid}`),
          {
            room_id: form_cr.value.room_id,
          },
        );
        await router.push({ name: 'room' });
      } else {
        console.log('密碼錯誤');
      }
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };

  // - 初始化當前使用者資料
  const init_user_data = () => {
    try {
      onAuthStateChanged(auth, async (user) => {
        if (user) {
          user_data.value.int_uid = user.providerData[0].uid;
          user_data.value.uid = user.uid;
          const user_ref = dbRef(db, `users/${user_data.value.uid}`);
          const users_snapshot = await get(user_ref);
          user_data.value.language = users_snapshot.val().language;
        } else {
          console.log('使用者尚未登入');
        }
      });
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };

  onMounted(() => {
    init_user_data();
  });
</script>
