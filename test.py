"""護照辨識 API 測試腳本

此腳本用於測試護照辨識 API 的功能是否完善，支援單張與批次辨識測試。
"""

import base64
import json
import sys
from pathlib import Path

import requests


# API 基本設定
DEFAULT_BASE_URL = "http://localhost:8080"
SINGLE_ENDPOINT = "/api/passport/recognize"
BATCH_ENDPOINT = "/api/passport/recognize/batch"


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
    base_url: str = DEFAULT_BASE_URL
) -> None:
    """測試單張護照辨識 API
    
    Args:
        image_path (str): 要測試的圖片檔案路徑
        base_url (str): API 基本 URL，預設為 http://localhost:8080
    
    Examples:
        >>> test_passport_api("passport.jpg")
        >>> test_passport_api("passport.jpg", "http://localhost:8080")
    
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
        ValueError: 當圖片無法讀取時
        requests.RequestException: 當 API 請求失敗時
    """
    api_url = f"{base_url}{SINGLE_ENDPOINT}"
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
        "image": base64_image,
        "id": "test_single_001"
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
            print(f"ID: {result.get('id')}")
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
        print(f"請確認 API 伺服器是否正在運行 (預設: {DEFAULT_BASE_URL})")
        raise
    except requests.RequestException as e:
        print(f"✗ 請求錯誤: {e}")
        raise


def test_passport_batch_api(
    image_paths: list[str],
    base_url: str = DEFAULT_BASE_URL
) -> None:
    """測試批次護照辨識 API
    
    Args:
        image_paths (list[str]): 要測試的圖片檔案路徑列表
        base_url (str): API 基本 URL，預設為 http://localhost:8080
    
    Examples:
        >>> test_passport_batch_api(["passport1.jpg", "passport2.jpg"])
        >>> test_passport_batch_api(["passport.jpg"], "http://localhost:8080")
    
    Raises:
        FileNotFoundError: 當任一圖片檔案不存在時
        ValueError: 當任一圖片無法讀取時
        requests.RequestException: 當 API 請求失敗時
    """
    api_url = f"{base_url}{BATCH_ENDPOINT}"
    print(f"正在準備批次辨識測試，共 {len(image_paths)} 張圖片")
    
    images_payload = []
    for idx, image_path in enumerate(image_paths):
        try:
            print(f"  [{idx + 1}/{len(image_paths)}] 正在讀取: {image_path}")
            base64_image = image_to_base64(image_path)
            
            # 使用檔名作為 ID，或自動生成
            path_obj = Path(image_path)
            image_id = f"{path_obj.name}_{idx}"
            
            images_payload.append({
                "id": image_id,
                "image": base64_image
            })
            print(f"    ✓ 已轉換 (ID: {image_id}, 長度: {len(base64_image)} 字元)")
        except FileNotFoundError as e:
            print(f"    ✗ 錯誤: {e}")
            raise
        except ValueError as e:
            print(f"    ✗ 錯誤: {e}")
            raise
    
    # 準備請求資料
    payload = {
        "images": images_payload
    }
    
    print(f"\n正在發送批次請求到: {api_url}")
    
    try:
        # 發送 POST 請求，批次處理可能需要更長時間
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 設定 5 分鐘超時（批次處理需要更長時間）
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
        print("\n=== API 回應摘要 ===")
        
        if response.status_code == 200 and result.get('success'):
            data = result.get('data', {})
            print(f"總數: {data.get('total', 0)}")
            print(f"成功: {data.get('successful', 0)}")
            print(f"失敗: {data.get('failed', 0)}")
            
            print("\n=== 詳細結果 ===")
            for item in data.get('results', []):
                item_id = item.get('id', '?')
                success = item.get('success', False)
                status = "✓" if success else "✗"
                print(f"\n[ID: {item_id}] {status}")
                
                if success:
                    passport_data = item.get('data', {})
                    for key, value in passport_data.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"    錯誤: {item.get('error', '未知錯誤')}")
            
            print(f"\n✓ 批次 API 測試完成！")
        else:
            print(f"\n✗ 批次 API 測試失敗")
            if 'error' in result:
                print(f"錯誤訊息: {result['error']}")
    
    except requests.Timeout as e:
        print(f"✗ 請求超時: {e}")
        raise
    except requests.ConnectionError as e:
        print(f"✗ 連線錯誤: 無法連接到 API 伺服器")
        print(f"請確認 API 伺服器是否正在運行 (預設: {DEFAULT_BASE_URL})")
        raise
    except requests.RequestException as e:
        print(f"✗ 請求錯誤: {e}")
        raise


def print_usage() -> None:
    """顯示使用說明
    
    Examples:
        >>> print_usage()
    
    Raises:
        此函數不會拋出錯誤
    """
    print("護照辨識 API 測試工具")
    print("=" * 50)
    print("\n單張辨識測試:")
    print("  python test.py <圖片路徑> [BASE_URL]")
    print("  範例: python test.py passport.jpg")
    print("  範例: python test.py passport.jpg http://localhost:8080")
    print("\n批次辨識測試:")
    print("  python test.py --batch <圖片路徑1> <圖片路徑2> ... [--url BASE_URL]")
    print("  範例: python test.py --batch passport1.jpg passport2.jpg")
    print("  範例: python test.py --batch *.jpg --url http://localhost:8080")


def main():
    """主程式
    
    從命令列參數讀取圖片路徑並執行測試。
    支援單張辨識與批次辨識兩種模式。
    
    Examples:
        >>> # 從命令列執行單張辨識
        >>> # python test.py passport.jpg
        >>> # python test.py passport.jpg http://localhost:8080
        >>> 
        >>> # 從命令列執行批次辨識
        >>> # python test.py --batch passport1.jpg passport2.jpg
        >>> # python test.py --batch passport1.jpg passport2.jpg --url http://localhost:8080
    
    Raises:
        此函數不會拋出錯誤，會以適當的結束代碼退出
    """
    import time
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # 解析命令列參數
    args = sys.argv[1:]
    
    # 檢查是否為批次模式
    if args[0] == '--batch':
        # 批次模式
        if len(args) < 2:
            print("錯誤: 批次模式需要至少一張圖片")
            print_usage()
            sys.exit(1)
        
        # 解析圖片路徑與 URL
        image_paths: list[str] = []
        base_url = DEFAULT_BASE_URL
        
        i = 1
        while i < len(args):
            if args[i] == '--url':
                if i + 1 < len(args):
                    base_url = args[i + 1]
                    i += 2
                else:
                    print("錯誤: --url 需要指定 URL")
                    sys.exit(1)
            else:
                image_paths.append(args[i])
                i += 1
        
        if len(image_paths) == 0:
            print("錯誤: 批次模式需要至少一張圖片")
            print_usage()
            sys.exit(1)
        
        try:
            start_time = time.time()
            test_passport_batch_api(image_paths, base_url)
            print(f'\n總耗時：{time.time() - start_time:.2f} 秒')
        except (FileNotFoundError, ValueError) as e:
            print(f"\n測試失敗: {e}")
            sys.exit(1)
        except requests.RequestException as e:
            print(f"\n測試失敗: {e}")
            sys.exit(1)
    else:
        # 單張模式
        image_path = args[0]
        base_url = args[1] if len(args) > 1 else DEFAULT_BASE_URL
        
        try:
            start_time = time.time()
            test_passport_api(image_path, base_url)
            print(f'\n總耗時：{time.time() - start_time:.2f} 秒')
        except (FileNotFoundError, ValueError) as e:
            print(f"\n測試失敗: {e}")
            sys.exit(1)
        except requests.RequestException as e:
            print(f"\n測試失敗: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

