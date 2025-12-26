FROM python:3.9-slim

WORKDIR /app

# 安装系统工具
RUN apt-get update && apt-get install -y \
    ping \
    iputils-ping \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制应用文件
COPY ./src /app

# 安装Python依赖
RUN pip install flask

# 创建flag文件
RUN echo "Placeholder for FLAG" > /flag.txt && chmod 400 /flag.txt

EXPOSE 5000

# 运行应用前写入FLAG
CMD sh -c 'echo "$FLAG" > /flag.txt && python app.py'
