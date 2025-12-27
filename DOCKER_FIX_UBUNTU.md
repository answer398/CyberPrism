# Ubuntu 20.04 Docker 连接问题修复指南

## 问题描述
错误信息：`Error while fetching server API version: Not supported URL scheme http+docker`

这个错误通常由以下原因引起：
1. Docker服务未启动
2. Docker socket权限问题
3. 用户不在docker组
4. Docker Python SDK版本问题

---

## 修复步骤

### 1. 检查Docker服务状态

```bash
# 检查Docker服务是否运行
sudo systemctl status docker

# 如果未运行，启动Docker服务
sudo systemctl start docker

# 设置Docker开机自启
sudo systemctl enable docker
```

### 2. 检查Docker Socket权限

```bash
# 检查socket文件是否存在
ls -la /var/run/docker.sock

# 输出应该类似于：
# srw-rw---- 1 root docker 0 Dec 27 10:00 /var/run/docker.sock
```

### 3. 将当前用户添加到docker组（推荐）

```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新加载用户组（或重新登录）
newgrp docker

# 验证用户已在docker组
groups
```

### 4. 修复Socket权限（如果第3步不生效）

```bash
# 临时修改权限（重启后失效）
sudo chmod 666 /var/run/docker.sock

# 永久修改（推荐方式是添加到docker组）
sudo chmod 660 /var/run/docker.sock
sudo chown root:docker /var/run/docker.sock
```

### 5. 验证Docker连接

```bash
# 测试Docker命令
docker ps

# 测试Python连接
cd backend
source venv/bin/activate  # 如果使用虚拟环境
python3 -c "import docker; client = docker.from_env(); print(client.ping())"

# 应该输出：True
```

### 6. 如果仍然失败，检查Docker Python SDK

```bash
# 重新安装docker包
pip uninstall docker docker-py docker-compose
pip install docker==7.0.0

# 验证版本
pip show docker
```

### 7. 检查环境变量

```bash
# 查看DOCKER_HOST环境变量
echo $DOCKER_HOST

# 如果设置了错误的值，取消设置
unset DOCKER_HOST

# 或在~/.bashrc中永久移除
```

---

## 运行后端服务

```bash
cd backend

# 激活虚拟环境（如果使用）
source venv/bin/activate

# 启动后端
python3 run.py
```

---

## 常见问题

### Q1: 执行 `docker ps` 提示权限被拒绝
**A**: 需要添加用户到docker组，然后重新登录或执行 `newgrp docker`

### Q2: `from_env()` 仍然失败
**A**: 检查是否设置了错误的 `DOCKER_HOST` 环境变量

### Q3: 在虚拟环境中无法连接
**A**: 确保在虚拟环境中安装了docker包：`pip install docker==7.0.0`

### Q4: 使用root运行仍然失败
**A**: 检查Docker服务是否启动：`sudo systemctl start docker`

---

## 验证修复

运行以下Python脚本测试连接：

```bash
cd backend
python3 << 'EOF'
import docker
import platform

print(f"系统: {platform.system()}")

try:
    # 方法1: from_env()
    client = docker.from_env()
    client.ping()
    print("✓ docker.from_env() 连接成功")
except Exception as e:
    print(f"✗ docker.from_env() 失败: {e}")

    try:
        # 方法2: Unix socket
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        client.ping()
        print("✓ Unix socket 连接成功")
    except Exception as e2:
        print(f"✗ Unix socket 失败: {e2}")

# 显示Docker版本
try:
    info = client.version()
    print(f"\nDocker版本: {info['Version']}")
    print(f"API版本: {info['ApiVersion']}")
except:
    pass
EOF
```

输出应该显示：`✓ docker.from_env() 连接成功` 或 `✓ Unix socket 连接成功`

---

## 快速修复（一键脚本）

```bash
#!/bin/bash
# 快速修复Docker连接问题

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER

# 修复socket权限
sudo chmod 660 /var/run/docker.sock
sudo chown root:docker /var/run/docker.sock

echo "修复完成！请执行以下命令之一："
echo "1. 重新登录当前用户"
echo "2. 或执行: newgrp docker"
echo "3. 然后重启后端服务"
```

保存为 `fix_docker.sh`，执行：
```bash
chmod +x fix_docker.sh
./fix_docker.sh
```
