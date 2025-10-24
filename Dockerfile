FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
  RUN apt-get update && apt-get install -y --no-install-recommends \
      && rm -rf /var/lib/apt/lists/*
#
#     # 复制依赖文件并安装
      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt
#
#     # 复制应用代码
      COPY app.py .
#
#     # 设置环境变量
      ENV VERSION=1.0.0
      ENV ENVIRONMENT=production
      ENV BUILD_TIME=unknown
      ENV FLASK_ENV=production
#
#     # 暴露端口
      EXPOSE 5000
#
#     # 运行应用
      CMD ["python", "app.py"]
