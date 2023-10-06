# [START speech_transcribe_infinite_streaming]
# 開始進行無限串流辨識的程式碼

import os

# 設定 Google Cloud API 憑證檔案路徑
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp.json"

import re
import sys
import time

from google.cloud import speech
import pyaudio
from six.moves import queue
from translation_demo import translate_demo
import asyncio

# 音頻錄製參數
STREAMING_LIMIT = 240000  # 4 分鐘
SAMPLE_RATE = 16000  # 取樣率
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 每個 chunk 的長度 (100 毫秒)

RED = "\033[0;31m"  # 紅色文字
GREEN = "\033[0;32m"  # 綠色文字
YELLOW = "\033[0;33m"  # 黃色文字


def get_current_time():
    """回傳當前時間的毫秒數"""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """開啟錄音串流，並將錄音分成一個一個 chunk 的音頻"""

    def __init__(self, rate, chunk_size):
        self._rate = rate  # 取樣率
        self.chunk_size = chunk_size  # 每個 chunk 的長度
        self._num_channels = 1
        self._buff = queue.Queue()  # 儲存音頻 chunk 的 queue
        self.closed = True  # 判斷 stream 是否已經被關閉
        self.start_time = get_current_time()  # 開始錄音的時間
        self.restart_counter = 0
        self.audio_input = []  # 儲存所有的音頻
        self.last_audio_input = []  # 儲存最後一個音頻 chunk
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False  # 判斷最後一個辨識結果是否已經確定
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()  # 透過 PyAudio 進行錄音
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,  # 聲音的格式為 Int16
            channels=self._num_channels,  # 單聲道
            rate=self._rate,  # 取樣率
            input=True,  # 設定為錄音輸入
            frames_per_buffer=self.chunk_size,  # 設定每個 chunk 的長度
            # 開啟 callback function 讓錄音以非同步的方式進行，以免佔用主線程的資源
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):
        # 初始化 closed 屬性為 False，表示麥克風串流還未關閉
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        # 停止串流音訊，關閉串流物件，設定 closed 屬性為 True
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # 向 buffer 物件中放入 None，以終止串流音訊，避免阻塞流程終止
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """從麥克風串流中連續收集音訊資料至 buffer 物件。"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """從麥克風流式傳輸音頻到API並寫入本地緩衝區"""

        while not self.closed:
            data = []

            # 如果有新的串流和上次錄音的數據
            if self.new_stream and self.last_audio_input:
                # 計算每個小塊的時間，用於拆分數據
                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:
                    # 計算拆分的起點和終點
                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    # 計算下次拆分的起點
                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    # 拆分數據
                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # 從緩衝區取出一個音頻數據塊，如果是None，則結束迭代
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)

            # 從緩衝區獲取其他數據塊並寫入本地緩衝區
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            # 合併數據塊
            yield b"".join(data)


def listen_print_loop(responses, stream):
    """迭代遍歷伺服器回應並輸出。

    傳遞的 responses 為生成器，會阻塞直到伺服器提供回應。

    每個回應可能包含多個結果，每個結果可能包含多個替代方案；
    詳細資訊請參閱 https://goo.gl/tjCPAU。這裡只列印最佳替代方案的轉錄。

    在這種情況下，即使是臨時結果也會提供回應。如果回應是臨時的，
    請在結尾處打印換行符，以允許下一個結果覆蓋它，直到回應為最終結果。
    對於最終結果，請打印換行符以保留最終的轉錄。
    """

    for response in responses:
        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_micros = 0

        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.microseconds:
            result_micros = result.result_end_time.microseconds

        stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))

        corrected_time = (
            stream.result_end_time
            - stream.bridging_offset
            + (STREAMING_LIMIT * stream.restart_counter)
        )
        # 顯示中間結果，但在行尾加上換行符，以便後續行可以覆蓋它們。

        if result.is_final:
            sys.stdout.write(GREEN)
            sys.stdout.write("\033[K")
            sys.stdout.write(str(corrected_time) + ": " + transcript + "\n")
            # <> 傳入translate_demo
            asyncio.run(translate_demo(transcript))

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # 如果任何轉錄的短語是我們的關鍵字之一，則退出辨識。
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                sys.stdout.write(YELLOW)
                sys.stdout.write("正在退出...\n")
                stream.closed = True
                break

        # else:
        #     sys.stdout.write(RED)
        #     sys.stdout.write("\033[K")
        #     sys.stdout.write(str(corrected_time) + ": " + transcript + "\r")

        #     stream.last_transcript_was_final = False


def speech_to_text_main():
    """開始雙向串流，從麥克風輸入到語音API"""

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # 設定音訊的編碼格式
        sample_rate_hertz=SAMPLE_RATE,  # 設定音訊的取樣率
        language_code="zh-TW",  # 設定語言為繁體中文
        max_alternatives=1,  # 設定最大識別結果數量
        enable_automatic_punctuation=True,  # 啟用自動標點
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True  # 設定識別結果即時回傳
    )

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)  # 初始化麥克風串流管理器
    print(mic_manager.chunk_size)
    sys.stdout.write(YELLOW)
    sys.stdout.write("=====================================================\n")

    with mic_manager as stream:
        while not stream.closed:
            sys.stdout.write(YELLOW)
            sys.stdout.write(
                "\n" + str(STREAMING_LIMIT * stream.restart_counter) + ": 語音轉文字系統啟動\n"
            )

            stream.audio_input = []
            audio_generator = stream.generator()

            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)  # 設定串流請求內容
                for content in audio_generator
            )

            responses = client.streaming_recognize(
                streaming_config, requests
            )  # 透過串流請求送出音訊，取得識別結果

            # 現在，使用識別結果
            listen_print_loop(responses, stream)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write("\n")
            stream.new_stream = True


if __name__ == "__main__":
    speech_to_text_main()
