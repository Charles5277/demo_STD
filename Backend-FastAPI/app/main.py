# 從websocket到speech_to_text_main

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.cloud import speech
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from six.moves import queue
import os

# FastAPI應用程式
app = FastAPI()

# 選擇性：設定CORS中間件以允許WebSocket跨域連接
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 這裡可以配置允許的跨域源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket路由
class WebSocketData:
    def __init__(self, data: str):
        self.data = data


# 建立一個字典來存儲不同用戶的WebSocket連接
active_connections: Dict[int, WebSocket] = {}

# Google語音識別相關參數
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/code/app/gcp.json"
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)


class ResumableMicrophoneStream:
    def __init__(self, rate, chunk_size):
        self.rate = rate
        self.chunk_size = chunk_size
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self.closed = True

    def _fill_buffer(self, in_data, *args, **kwargs):
        self._buff.put(in_data)

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses, stream):
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        confidence = result.alternatives[0].confidence

        # 在這裡你可以處理識別結果，例如將它發送回WebSocket連接
        print(f"Transcript: {transcript}, Confidence: {confidence}")


async def microphone_to_speech_api(stream, websocket):
    print("開始音訊串流")

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # 設定音訊的編碼格式
        sample_rate_hertz=SAMPLE_RATE,  # 設定音訊的取樣率
        language_code="zh-TW",  # 設定語言為繁體中文
        max_alternatives=1,  # 設定最大識別結果數量
        enable_automatic_punctuation=True,  # 啟用自動標點
    )

    audio_generator = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE).generator()

    # 將音訊數據拼接成一個完整的音訊文件
    audio_data = b"".join(audio_generator)

    audio = speech.RecognitionAudio(content=audio_data)

    # 調用 API 進行語音識別
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript = result.alternatives[0].transcript
        confidence = result.alternatives[0].confidence

        # 將識別結果發送回 WebSocket 連接
        await websocket.send_text(f"Transcript: {transcript}, Confidence: {confidence}")
        # 順便print出來f
        print(f"Transcript: {transcript}, Confidence: {confidence}")

    if stream.result_end_time > 0:
        stream.final_request_end_time = stream.is_final_end_time
    stream.result_end_time = 0
    stream.last_audio_input = []
    stream.last_audio_input = stream.audio_input
    stream.audio_input = []
    stream.restart_counter = stream.restart_counter + 1


# WebSocket端點處理音訊串流
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    print("WebSocket連接已建立")
    try:
        await websocket.accept()

        # 將 WebSocket 連接存儲在字典中
        active_connections[client_id] = websocket
        print("WebSocket連接成功")

        # 初始化音訊串流管理器
        mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
        with mic_manager as stream:
            while not stream.closed:
                try:
                    data = await websocket.receive_text()
                    print("接收到音頻數據：", data) 

                    if data == "start_streaming":
                        await websocket.send_text("Streaming started")
                        # 開始音頻串流
                        print("已收到音頻數據")
                        await microphone_to_speech_api(
                            stream, websocket
                        ) 
                        print("音頻處理已啟動")  

                    elif data == "stopStreaming": 
                        await websocket.send_text("Streaming stopped")
                        stream.closed = True
                        break
                except WebSocketDisconnect:
                    # WebSocket連接中斷
                    del active_connections[client_id]
                    break

    except WebSocketDisconnect:
        # 當WebSocket斷開連接時，刪除存儲的連接
        if client_id in active_connections:
            del active_connections[client_id]
    print("WebSocket連接已關閉") 


if __name__ == "__main__":
    # 啟動FastAPI應用程式
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
