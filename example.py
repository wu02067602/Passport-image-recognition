"""
護照辨識系統使用範例

此檔案展示如何使用護照辨識系統進行影像辨識。
"""

import os
from src.gemini_image_recognizer import GeminiImageRecognizer
from src.passport_recognition_controller import PassportRecognitionController


def main():
    """主程式範例"""
    
    # 從環境變數取得 API 金鑰
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("請設定環境變數 GEMINI_API_KEY")
        return
    
    # 建立辨識器
    recognizer = GeminiImageRecognizer(api_key=api_key)
    
    # 建立控制器
    controller = PassportRecognitionController(recognizer=recognizer)
    
    # 單張圖片辨識
    image_path = "/path/to/passport.jpg"
    
    try:
        result = controller.recognize_passport(image_path)
        print(f"護照號碼: {result.passport_number}")
        print(f"信心度: {result.confidence}")
        print(f"是否找到: {result.is_found()}")
        print(f"完整結果: {result.to_dict()}")
    except FileNotFoundError:
        print(f"找不到圖片檔案: {image_path}")
    except ValueError as e:
        print(f"驗證錯誤: {e}")
    except RuntimeError as e:
        print(f"API 調用失敗: {e}")
    
    # 批次辨識
    image_paths = [
        "/path/to/passport1.jpg",
        "/path/to/passport2.jpg",
        "/path/to/passport3.jpg"
    ]
    
    try:
        results = controller.batch_recognize_passports(image_paths)
        for path, result in results.items():
            print(f"\n圖片: {path}")
            print(f"護照號碼: {result.passport_number}")
            print(f"信心度: {result.confidence}")
    except ValueError as e:
        print(f"驗證錯誤: {e}")


if __name__ == "__main__":
    main()
