<template>
  <div class="q-pa-md row justify-center">
    <div style="width: 100%; max-width: 400px">
      <q-chat-message
        :text="['Have you seen Quasar?']"
        sent
        text-color="white"
        bg-color="primary"
      >
        <template v-slot:name>me</template>
        <template v-slot:stamp>7 minutes ago</template>
        <template v-slot:avatar>
          <img
            class="q-message-avatar q-message-avatar--sent"
            src="https://cdn.quasar.dev/img/avatar4.jpg"
          />
        </template>
      </q-chat-message>

      <q-chat-message bg-color="amber">
        <template v-slot:name>Mary</template>
        <template v-slot:avatar>
          <img
            class="q-message-avatar q-message-avatar--received"
            src="https://cdn.quasar.dev/img/avatar2.jpg"
          />
        </template>

        <div>
          Already building an app with it...
          <img
            src="https://cdn.quasar.dev/img/discord-qeart.png"
            class="my-emoji"
          />
        </div>

        <q-spinner-dots size="2rem" />
      </q-chat-message>
      <!-- 麥克風按鈕 -->
      <button @click="toggleMicrophone">
        {{ isMicrophoneOn ? '關閉麥克風' : '開啟麥克風' }}
      </button>
    </div>
  </div>
</template>

<script setup>
  import { onMounted, onBeforeUnmount, onBeforeMount, inject, ref } from 'vue';
  import { onBeforeRouteLeave } from 'vue-router';
  import { ref as dbRef, get } from 'firebase/database';
  import { db, auth } from '../firebase';
  import { onAuthStateChanged } from 'firebase/auth';

  const confirm_leave = inject('contentChanged');

  const user_data = ref({
    int_uid: '',
    uid: '',
  });

  // - 語音傳輸
  // > start
  // WebSocket連接
  const receivedMessage = ref(''); // 接收到的消息
  let ws;
  const init_ws_server = () => {
    const socketUrl = `ws://localhost:8000/ws/${user_data.value.int_uid}`;
    ws = new WebSocket(socketUrl);

    ws.onopen = () => {
      console.log('WebSocket已連接');

      // 在連結成功後，延遲3秒發送測試資料到後端
      setTimeout(() => {
        console.log('WebSocket狀態：', ws.readyState);
        sendMessageToBackend();
        startStreaming();
      }, 3000);
    };

    // WebSocket接收到消息時執行
    ws.onmessage = (event) => {
      // 在receivedMessage中存储接收到的消息
      receivedMessage.value = event.data;
      console.log('接收到消息', event.data);
    };

    // WebSocket關閉時執行
    ws.onclose = () => {
      console.log('WebSocket已關閉');
    };
  };

  // - 測試websocket連通
  // > start
  const testData = ref('這是測試資料'); // 您的測試資料

  const sendMessageToBackend = () => {
    // 檢查WebSocket是否已經初始化
    if (ws && ws.readyState === WebSocket.OPEN) {
      // 發送測試資料到後端
      ws.send(testData.value);
      console.log('已發送測試資料到後端');
    } else {
      console.log('WebSocket未連接或尚未初始化');
    }
  };
  // > end

  const isMicrophoneOn = ref(false); // 麥克風初始狀態為關閉

  const toggleMicrophone = () => {
    if (isMicrophoneOn.value) {
      stopStreaming();
      isMicrophoneOn.value = false;
    } else {
      init_ws_server();
      isMicrophoneOn.value = true;
    }
  };

  let mediaRecorder;

  const startStreaming = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // 發送開始音頻串流的消息到後端
      ws.send('start_audio_streaming');

      // 啟動麥克風串流
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
          .getUserMedia({
            audio: {
              sampleRate: 16000,
              channelCount: 2,
              volume: 1.0,
            },
          })
          .then((stream) => {
            if (ws && ws.readyState === WebSocket.OPEN) {
              mediaRecorder = new MediaRecorder(stream);
              mediaRecorder.ondataavailable = (event) => {
                console.log('音頻數據：', event.data.size);
                if (event.data.size > 0) {
                  console.log('音頻傳輸中...');
                  const audioBlob = new Blob([event.data], {
                    type: 'audio/wav',
                  });
                  console.log(audioBlob);
                  // - 將audioBlob存為檔案並提供下載
                  // > start
                  const url = URL.createObjectURL(audioBlob);
                  const a = document.createElement('a');
                  document.body.appendChild(a);
                  a.style = 'display: none';
                  a.href = url;
                  a.download = 'audio.wav';
                  a.click();
                  window.URL.revokeObjectURL(url);
                  // > end

                  ws.send(audioBlob);
                  // - 檢查ws.send是否成功
                  // > start
                  setTimeout(() => {
                    if (ws.bufferedAmount === 0) {
                      console.log('音頻數據已發送到後端');
                    } else {
                      console.log('音頻數據發送失敗');
                    }
                  }, 2000); // 增加等待時間（1秒），可以根據需要調整
                }
              };
              mediaRecorder.start();
              console.log('MediaRecorder狀態：', mediaRecorder.state);
              // 更新界面按钮文字
              isMicrophoneOn.value = true;
            } else {
              console.log('WebSocket未連接或尚未初始化');
            }
          })
          .catch((error) => {
            console.error('無法使用麥克風：', error);
          });
      }
    } else {
      console.log('WebSocket未連接或尚未初始化');
    }
  };

  const stopStreaming = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // 發送停止音頻串流的消息到後端
      ws.send('stopStreaming'); // 修改消息為 "stopStreaming"
      // 停止MediaRecorder和關閉麥克風串流
      if (isMicrophoneOn.value && mediaRecorder) {
        // 停止MediaRecorder
        mediaRecorder.stop();
        // 更新界面按鈕文字
        isMicrophoneOn.value = false;
      }
    } else {
      console.log('WebSocket未連接或尚未初始化');
    }
  };

  // > end

  // - 頁面偵測跳轉提示
  // > start
  onBeforeRouteLeave((to, from, next) => {
    if (confirm_leave.value) {
      console.log(confirm_leave.value);
      const acceptToLeave = window.confirm('變更尚未儲存，確定要離開嗎？');
      acceptToLeave ? next() : next(false);
    } else {
      next();
    }
  });

  onMounted(() => {
    window.onbeforeunload = () => {
      return '';
    };
  });

  onBeforeUnmount(() => {
    window.onbeforeunload = null;
  });
  // > end

  // - 寫入user_data
  // > start
  // - 初始化當前使用者資料
  const init_user_data = () => {
    try {
      onAuthStateChanged(auth, async (user) => {
        if (user) {
          user_data.value.uid = user.uid;
          const user_ref = dbRef(db, `users/${user_data.value.uid}`);
          const users_snapshot = await get(user_ref);
          user_data.value.int_uid = users_snapshot.val().int_uid;
        } else {
          console.log('使用者尚未登入');
        }
      });
    } catch (error) {
      console.error('伺服器錯誤', error);
    }
  };

  onBeforeMount(() => {
    init_user_data();
  });
  // > end
</script>

<style lang="scss">
  .my-emoji {
    vertical-align: middle;
    height: 2em;
    width: 2em;
  }
</style>
