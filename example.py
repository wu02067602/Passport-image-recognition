"""
護照辨識系統使用範例

此檔案展示如何使用護照辨識系統進行影像辨識。
"""

import os
from src.gemini_image_recognizer import GeminiImageRecognizer
from src.passport_recognition_controller import PassportRecognitionController


def example_with_gcloud():
    """使用 gcloud 認證的範例"""
    print("=== 使用 gcloud 認證 ===\n")
    
    # 使用 gcloud 認證（需先執行 gcloud auth application-default login）
    recognizer = GeminiImageRecognizer()
    
    # 建立控制器
    controller = PassportRecognitionController(recognizer=recognizer)
    
    # 單張圖片辨識
    image_path = "/path/to/passport.jpg"
    
    try:
        result = controller.recognize_passport(image_path)
        print(f"護照號碼: {result.passport_number}")
        print(f"信心度: {result.confidence}")
        print(f"是否找到: {result.is_found()}")
    except FileNotFoundError:
        print(f"找不到圖片檔案: {image_path}")
    except ValueError as e:
        print(f"驗證錯誤: {e}")
    except RuntimeError as e:
        print(f"API 調用失敗: {e}")


def example_with_api_key():
    """使用 API 金鑰的範例"""
    print("\n=== 使用 API 金鑰 ===\n")
    
    # 從環境變數取得 API 金鑰
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("未設定環境變數 GEMINI_API_KEY，跳過此範例")
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


def main():
    """主程式範例"""
    print("護照辨識系統使用範例\n")
    print("=" * 50)
    
    # 預設使用 gcloud 認證
    example_with_gcloud()
    
    # 若有設定 API 金鑰，也展示使用 API 金鑰的方式
    example_with_api_key()


if __name__ == "__main__":
    main()
