"""
護照辨識系統使用範例

此範例展示如何使用 PassportRecognitionController 進行護照辨識。
"""

import os
from src.models.image_recognizer import ImageRecognizer
from src.controllers.passport_recognition_controller import PassportRecognitionController

def main():
    """主程式"""
    
    # 從環境變數取得 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("錯誤：請設定 GEMINI_API_KEY 環境變數")
        return
    
    # 初始化影像辨識器
    recognizer = ImageRecognizer(api_key=api_key)
    
    # 初始化控制器
    controller = PassportRecognitionController(recognizer=recognizer)
    
    # 指定護照圖片路徑
    image_path = "path/to/your/passport_image.jpg"
    
    try:
        # 執行護照辨識
        print("正在辨識護照資訊...")
        passport_info = controller.recognize_passport(image_path)
        
        # 顯示辨識結果
        print("\n=== 辨識結果 ===")
        print(f"護照號碼: {passport_info.passport_number or '無法辨識'}")
        print(f"性別: {passport_info.gender or '無法辨識'}")
        print(f"生日: {passport_info.birth_date or '無法辨識'}")
        print(f"中文姓名: {passport_info.chinese_name or '無法辨識'}")
        print(f"英文姓名: {passport_info.english_name or '無法辨識'}")
        
        print("\n=== 原始回應 ===")
        print(passport_info.raw_response)
        
        # 轉換為字典格式
        print("\n=== 字典格式 ===")
        print(passport_info.to_dict())
        
    except Exception as e:
        print(f"錯誤: {e}")


def example_with_custom_prompt():
    """使用自訂提示詞的範例"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("錯誤：請設定 GEMINI_API_KEY 環境變數")
        return
    
    recognizer = ImageRecognizer(api_key=api_key)
    controller = PassportRecognitionController(recognizer=recognizer)
    
    # 自訂提示詞（只辨識護照號碼）
    custom_prompt = """請辨識此護照圖片中的護照號碼，並以以下格式回傳：

護照號碼: [護照號碼]

如果無法辨識，請回傳「無法辨識」。"""
    
    image_path = "path/to/your/passport_image.jpg"
    
    try:
        print("正在使用自訂提示詞辨識...")
        raw_response = controller.recognize_passport_raw(
            image_path,
            custom_prompt=custom_prompt
        )
        print(f"辨識結果: {raw_response}")
        
    except Exception as e:
        print(f"錯誤: {e}")


if __name__ == "__main__":
    # 執行基本範例
    main()
    
    # 取消註解以執行自訂提示詞範例
    # example_with_custom_prompt()
