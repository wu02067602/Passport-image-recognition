"""護照辨識 API 測試腳本

此腳本用於測試護照辨識 API 的功能是否完善。
"""

import base64
import json
import sys
from pathlib import Path

import requests


def image_to_base64(image_path: str) -> str:
    """將圖片檔案轉換為 BASE64 編碼字串
    
    Args:
        image_path (str): 圖片檔案路徑
    
    Returns:
        str: BASE64 編碼的圖片字串
    
    Examples:
        >>> base64_str = image_to_base64("passport.jpg")
        >>> isinstance(base64_str, str)
        True
    
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
        ValueError: 當檔案無法讀取或不是有效的圖片時
    """
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
    
    if not path.is_file():
        raise ValueError(f"路徑不是檔案: {image_path}")
    
    try:
        with open(path, 'rb') as image_file:
            image_bytes = image_file.read()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_string
    except IOError as e:
        raise ValueError(f"無法讀取圖片檔案: {str(e)}") from e


def test_passport_api(
    image_path: str,
    api_url: str = "http://localhost:8080/api/passport/recognize"
) -> None:
    """測試護照辨識 API
    
    Args:
        image_path (str): 要測試的圖片檔案路徑
        api_url (str): API 端點 URL，預設為 http://localhost:8080/api/passport/recognize
    
    Examples:
        >>> test_passport_api("passport.jpg")
        >>> test_passport_api("passport.jpg", "http://localhost:8080/api/passport/recognize")
    
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
        ValueError: 當圖片無法讀取時
        requests.RequestException: 當 API 請求失敗時
    """
    print(f"正在讀取圖片: {image_path}")
    
    try:
        # 轉換圖片為 BASE64
        base64_image = image_to_base64(image_path)
        print(f"✓ 圖片已轉換為 BASE64 (長度: {len(base64_image)} 字元)")
    except FileNotFoundError as e:
        print(f"✗ 錯誤: {e}")
        raise
    except ValueError as e:
        print(f"✗ 錯誤: {e}")
        raise
    
    # 準備請求資料
    payload = {
        "image": base64_image
    }
    
    print(f"\n正在發送請求到: {api_url}")
    
    try:
        # 發送 POST 請求
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # 設定 60 秒超時
        )
        
        # 顯示回應狀態
        print(f"✓ HTTP 狀態碼: {response.status_code}")
        
        # 解析回應
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            print(f"✗ 無法解析 JSON 回應: {e}")
            print(f"回應內容: {response.text[:500]}")
            return
        
        # 顯示結果
        print("\n=== API 回應 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 檢查回應是否成功
        if response.status_code == 200 and result.get('success'):
            print("\n✓ API 測試成功！")
            if 'data' in result:
                print("\n=== 辨識結果 ===")
                data = result['data']
                for key, value in data.items():
                    print(f"{key}: {value}")
        else:
            print(f"\n✗ API 測試失敗")
            if 'error' in result:
                print(f"錯誤訊息: {result['error']}")
    
    except requests.Timeout as e:
        print(f"✗ 請求超時: {e}")
        raise
    except requests.ConnectionError as e:
        print(f"✗ 連線錯誤: 無法連接到 API 伺服器")
        print(f"請確認 API 伺服器是否正在運行 (預設: http://localhost:8080)")
        raise
    except requests.RequestException as e:
        print(f"✗ 請求錯誤: {e}")
        raise


def main():
    """主程式
    
    從命令列參數讀取圖片路徑並執行測試。
    
    Examples:
        >>> # 從命令列執行
        >>> # python test.py passport.jpg
        >>> # python test.py passport.jpg http://localhost:8080/api/passport/recognize
    """
    if len(sys.argv) < 2:
        print("使用方法: python test.py <圖片路徑> [API_URL]")
        print("範例: python test.py passport.jpg")
        print("範例: python test.py passport.jpg http://localhost:8080/api/passport/recognize")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8080/api/passport/recognize"
    
    try:
        import time
        start_time = time.time()
        test_passport_api(image_path, api_url)
        end_time = time.time()
        print(f'總耗時：{time.time() - start_time:.2f} 秒')
    except (FileNotFoundError, ValueError) as e:
        print(f"\n測試失敗: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"\n測試失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

