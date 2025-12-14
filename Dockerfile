# 使用 Python 官方映像作為基礎映像
FROM asia-east1-docker.pkg.dev/cola-cloud/chainguard-images/python:latest-dev

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
EXPOSE 8080

# 設定啟動命令 - 使用 bash 來執行 Python
ENTRYPOINT ["/bin/bash", "-c", "python3 app.py"]
