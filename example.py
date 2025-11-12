"""使用範例

此檔案展示如何使用護照辨識系統。
"""

from src import PassportController, PassportField


def main():
    """主程式範例"""
    # 1. 初始化控制器（需要提供 Gemini API 金鑰）
    api_key = "YOUR_GEMINI_API_KEY"  # 請替換為您的 API 金鑰
    controller = PassportController(api_key=api_key)
    
    # 2. 辨識整本護照的所有資訊
    passport_image_path = "path/to/passport.jpg"
    
    try:
        result = controller.recognize_passport(passport_image_path)
        
        print("=== 護照辨識結果 ===")
        print(f"中文名稱: {result.get('中文名稱')}")
        print(f"英文名稱: {result.get('英文名稱')}")
        print(f"國籍: {result.get('國籍')}")
        print(f"護照號碼: {result.get('護照號碼')}")
        print(f"性別: {result.get('性別')}")
        print(f"出生年月日: {result.get('出生年月日')}")
        print(f"護照效期: {result.get('護照效期')}")
        
    except FileNotFoundError as e:
        print(f"錯誤：{e}")
    except ValueError as e:
        print(f"錯誤：{e}")
    except RuntimeError as e:
        print(f"API 呼叫錯誤：{e}")
    
    # 3. 只辨識單一欄位
    try:
        chinese_name = controller.recognize_single_field(
            passport_image_path,
            PassportField.CHINESE_NAME
        )
        print(f"\n單一欄位辨識 - 中文名稱: {chinese_name}")
        
    except FileNotFoundError as e:
        print(f"錯誤：{e}")
    except ValueError as e:
        print(f"錯誤：{e}")
    except RuntimeError as e:
        print(f"API 呼叫錯誤：{e}")


if __name__ == "__main__":
    main()
