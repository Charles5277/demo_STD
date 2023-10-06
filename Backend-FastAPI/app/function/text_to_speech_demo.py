import os

# 設定 Google Cloud API 憑證檔案路徑
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp.json"

import asyncio

# 匯入 Google Cloud 的文字轉語音模組
from google.cloud import texttospeech_v1


# 定義一個名為 synthesize_text 的非同步函式，接受一個 text 參數
async def synthesize_text(text):
    # 創建一個文字轉語音客戶端
    client = texttospeech_v1.TextToSpeechAsyncClient()

    # 初始化請求參數
    synthesis_input = texttospeech_v1.SynthesisInput(text=text)
    voice = texttospeech_v1.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech_v1.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.MP3
    )

    # 發出請求
    response = await client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # 處理回應
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('已產生音檔 "output.mp3"')


"""
if __name__ == '__main__':
    # 執行 synthesize_text 函式，並傳入要轉換成語音的文字
    input_text = input('請輸入文字：')
    asyncio.run(synthesize_text(input_text))
"""
