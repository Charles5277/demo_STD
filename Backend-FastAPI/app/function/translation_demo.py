import os

# 設定 Google Cloud API 憑證檔案路徑
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp.json"

import asyncio

# 導入 Google Cloud 翻譯 API v3
from google.cloud import translate_v3
from text_to_speech_demo import synthesize_text


async def translate_demo(text):
    # 創建一個 API 客戶端
    client = translate_v3.TranslationServiceClient()

    # 輸出語言
    ip_target = "zh-TW"
    op_target = "en"

    # 翻譯文本
    result = client.translate_text(
        request={
            "parent": "projects/smart-translate-374404/locations/global",
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": ip_target,
            "target_language_code": op_target,
        }
    )

    # 輸出翻譯結果
    for translation in result.translations:
        result_text = format(translation.translated_text)
        print("翻譯結果：", result_text)
        # <> 傳入text_to_speech_demo
        await synthesize_text(result_text)


"""
if __name__ == '__main__':
    # 取得要翻譯的文本
    text = input("請輸入要翻譯的文本：")
    # 調用翻譯文本的函數
    asyncio.run(translate_demo(text))
"""
