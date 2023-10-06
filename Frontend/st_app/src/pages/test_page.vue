<template>
  <div class="q-pa-md row justify-center">
    <div style="width: 100%; max-width: 400px">
      <!-- 麥克風按鈕 -->
      <button @click="toggleMicrophone">
        {{ isMicrophoneOn ? '關閉麥克風' : '開啟麥克風' }}
      </button>
    </div>
  </div>
</template>

<script setup>
  import { onBeforeMount, ref } from 'vue';


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
