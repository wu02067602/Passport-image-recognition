"""護照批次辨識主程式

此程式可以批次處理指定目錄下的所有護照圖片，
並將辨識結果輸出為 CSV 檔案。
"""

import csv
import argparse
from pathlib import Path
from typing import Union, Any
from datetime import datetime

from src import PassportController


class PassportBatchProcessor:
    """護照批次處理器類別
    
    負責掃描目錄下的圖片檔案，批次進行護照辨識，
    並將結果輸出為 CSV 檔案。
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """初始化批次處理器
        
        Args:
            model_name (str): 使用的模型名稱，預設為 'gemini-2.5-flash'
        
        Examples:
            >>> processor = PassportBatchProcessor()
            >>> isinstance(processor, PassportBatchProcessor)
            True
        
        Raises:
            ValueError: 當模型名稱為空時
            RuntimeError: 當 gcloud 認證失敗時
        """
        self.controller = PassportController(model_name=model_name)
        self.supported_formats = self.controller.get_supported_formats()
    
    def scan_directory(self, directory_path: Union[str, Path]) -> list[Path]:
        """掃描目錄下所有支援的圖片檔案
        
        Args:
            directory_path (Union[str, Path]): 要掃描的目錄路徑
        
        Returns:
            list[Path]: 所有支援格式的圖片檔案路徑列表
        
        Examples:
            >>> processor = PassportBatchProcessor()
            >>> files = processor.scan_directory("./images")
            >>> isinstance(files, list)
            True
        
        Raises:
            FileNotFoundError: 當目錄不存在時
            ValueError: 當路徑不是目錄時
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"目錄不存在: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"路徑不是目錄: {directory_path}")
        
        image_files = []
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        
        return sorted(image_files)
    
    def process_single_image(self, image_path: Path) -> dict[str, Any]:
        """處理單一圖片檔案
        
        Args:
            image_path (Path): 圖片檔案路徑
        
        Returns:
            dict[str, Any]: 包含檔案資訊和辨識結果的字典
        
        Examples:
            >>> processor = PassportBatchProcessor()
            >>> result = processor.process_single_image(Path("passport.jpg"))
            >>> isinstance(result, dict)
            True
            >>> '檔案名稱' in result
            True
        
        Raises:
            FileNotFoundError: 當圖片檔案不存在時
            ValueError: 當圖片格式不支援或無法開啟時
            RuntimeError: 當 API 呼叫失敗時
        """
        result = {
            "檔案名稱": image_path.name,
            "檔案路徑": str(image_path.absolute()),
            "辨識狀態": "成功",
            "錯誤訊息": ""
        }
        
        try:
            passport_data = self.controller.recognize_passport(image_path)
            
            # 提取所有欄位資料
            result["中文名稱"] = passport_data.get("中文名稱", "")
            result["英文名稱"] = passport_data.get("英文名稱", "")
            
            # 處理國籍資料（可能是字典）
            nationality = passport_data.get("國籍", {})
            if isinstance(nationality, dict):
                result["國籍名稱"] = nationality.get("name", "")
                result["國籍代碼"] = nationality.get("code", "")
            else:
                result["國籍名稱"] = str(nationality) if nationality else ""
                result["國籍代碼"] = ""
            
            result["護照號碼"] = passport_data.get("護照號碼", "")
            result["性別"] = passport_data.get("性別", "")
            result["出生年月日"] = passport_data.get("出生年月日", "")
            result["護照效期"] = passport_data.get("護照效期", "")
            
        except FileNotFoundError as e:
            result["辨識狀態"] = "失敗"
            result["錯誤訊息"] = f"檔案不存在: {str(e)}"
        except ValueError as e:
            result["辨識狀態"] = "失敗"
            result["錯誤訊息"] = f"圖片格式錯誤: {str(e)}"
        except RuntimeError as e:
            result["辨識狀態"] = "失敗"
            result["錯誤訊息"] = f"API 呼叫失敗: {str(e)}"
        
        return result
    
    def process_directory(
        self,
        directory_path: Union[str, Path],
        output_csv: Union[str, Path]
    ) -> None:
        """批次處理目錄下的所有圖片並輸出 CSV
        
        Args:
            directory_path (Union[str, Path]): 要處理的目錄路徑
            output_csv (Union[str, Path]): 輸出 CSV 檔案路徑
        
        Examples:
            >>> processor = PassportBatchProcessor()
            >>> processor.process_directory("./images", "./results.csv")
        
        Raises:
            FileNotFoundError: 當目錄不存在時
            ValueError: 當路徑不是目錄時
            IOError: 當無法寫入 CSV 檔案時
        """
        print(f"開始掃描目錄: {directory_path}")
        image_files = self.scan_directory(directory_path)
        
        if not image_files:
            print(f"警告: 目錄中沒有找到支援的圖片檔案")
            return
        
        print(f"找到 {len(image_files)} 個圖片檔案")
        
        # CSV 欄位定義
        fieldnames = [
            "檔案名稱",
            "檔案路徑",
            "辨識狀態",
            "錯誤訊息",
            "中文名稱",
            "英文名稱",
            "國籍名稱",
            "國籍代碼",
            "護照號碼",
            "性別",
            "出生年月日",
            "護照效期"
        ]
        
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for idx, image_path in enumerate(image_files, 1):
                    print(f"處理 [{idx}/{len(image_files)}]: {image_path.name}")
                    
                    result = self.process_single_image(image_path)
                    writer.writerow(result)
                    
                    if result["辨識狀態"] == "成功":
                        print(f"  ✓ 成功")
                    else:
                        print(f"  ✗ 失敗: {result['錯誤訊息']}")
            
            print(f"\n處理完成！結果已儲存至: {output_csv}")
        
        except IOError as e:
            raise IOError(f"無法寫入 CSV 檔案: {output_csv}") from e


def main():
    """主程式入口
    
    使用前請先執行以下指令進行 gcloud 認證：
    $ gcloud auth application-default login
    
    Examples:
        >>> # 處理指定目錄下的所有護照圖片
        >>> # python main.py --input ./passports --output ./results.csv
    
    Raises:
        此函數不會拋出錯誤，所有錯誤都會被捕捉並顯示
    """
    parser = argparse.ArgumentParser(
        description="護照批次辨識工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python main.py --input ./passports --output results.csv
  python main.py -i ./passports -o results.csv --model gemini-1.5-pro

注意事項:
  - 使用前請先執行 gcloud auth application-default login 進行認證
  - 支援的圖片格式: JPG, JPEG, PNG
  - 會遞迴掃描目錄下的所有子目錄
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='輸入目錄路徑（包含護照圖片）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='輸出 CSV 檔案路徑'
    )
    
    parser.add_argument(
        '-m', '--model',
        type=str,
        default='gemini-2.5-flash',
        help='使用的模型名稱（預設: gemini-2.5-flash）'
    )
    
    args = parser.parse_args()
    
    try:
        # 建立批次處理器
        processor = PassportBatchProcessor(model_name=args.model)
        
        # 執行批次處理
        processor.process_directory(args.input, args.output)
        
    except FileNotFoundError as e:
        print(f"錯誤: {e}")
        exit(1)
    except ValueError as e:
        print(f"錯誤: {e}")
        exit(1)
    except RuntimeError as e:
        print(f"錯誤: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n使用者中斷執行")
        exit(130)


if __name__ == "__main__":
    main()
