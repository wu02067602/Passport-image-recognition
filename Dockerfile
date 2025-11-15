# 使用 Python 官方映像作為基礎映像
FROM python:3.14-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY app.py .
COPY src/ ./src/

# 暴露端口
EXPOSE 5000

# 啟動應用程式
CMD ["python", "app.py"]
