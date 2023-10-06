<template>
  <div class="demo">
    <div style="margin-bottom: 30px">
      <el-button @click="toggleSharing">
        {{ enabled ? '停止' : '开始' }} 共享我的屏幕
      </el-button>

      <el-button v-if="enabled && !recording" @click="startRecording">
        录制我的屏幕
      </el-button>

      <el-button v-if="recording" @click="stopRecording"> 停止录制 </el-button>
    </div>
    <video ref="video" muted autoplay controls style="height: 40rem" />
  </div>
</template>

<script setup>
  import { ref, watchEffect } from 'vue';
  import { useDisplayMedia } from '@vueuse/core';

  const video = ref(null);
  const stopRecordingShow = ref(false);
  const recording = ref(false);
  const videoStreaming = ref([]);

  const { stream, enabled } = useDisplayMedia({
    video: true,
  });

  watchEffect(() => {
    if (video.value) {
      video.value.srcObject = stream.value;
    }
  });

  let mediaRecorder;

  const toggleSharing = () => {
    if (enabled.value) {
      stopRecordingShow.value = false;
      if (recording.value) {
        stopRecording();
      }
    }
    enabled.value = !enabled.value;
  };

  const startRecording = () => {
    stopRecordingShow.value = true;
    recording.value = true;
    videoStreaming.value = [];

    mediaRecorder = new MediaRecorder(stream.value);

    mediaRecorder.addEventListener('dataavailable', (event) => {
      if (event.data.size > 0) {
        videoStreaming.value.push(event.data);
      }
    });

    mediaRecorder.addEventListener('stop', () => {
      const a = document.createElement('a');
      const blob = new Blob(videoStreaming.value, { type: 'video/mp4' });
      a.href = URL.createObjectURL(blob);
      a.setAttribute('download', '录制视频.mp4');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      recording.value = false;
    });

    mediaRecorder.start();
  };

  const stopRecording = () => {
    stopRecordingShow.value = false;
    if (mediaRecorder) {
      mediaRecorder.stop();
    }
    recording.value = false;
  };
</script>
