// audio-processor.js

class AudioProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    for (let channel = 0; channel < input.length; channel++) {
      const inputData = input[channel];
      const outputData = output[channel];

      // 在這裡處理音頻數據，你可以將它傳送到 WebSocket
      // 例如：ws.send(inputData);

      outputData.set(inputData);
    }

    return true;
  }
}

registerProcessor('audio-processor', AudioProcessor);
