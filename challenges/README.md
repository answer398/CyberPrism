# CyberPrism CTF 出题与测试指南
## 📝 出题规范与注意事项

### 必须遵守的规则

#### 1. docker-compose.yml 配置规范 ⚠️

**这是最关键的文件！**

**标准模板（推荐）**:

```yaml
version: '3.8'

services:
  web:                          # 服务名（可自定义）
    build:
      context: .                # 构建上下文
    image: cyberprism/<题目名字>  # 镜像名称
    container_name: cyberprism-<题目名字>-${USER_ID:-default}  # 容器名称
    ports:
      - "80"                    # ⚠️ 只写容器内端口，不写宿主机端口!
    environment:
      - FLAG=${FLAG}            # ⚠️ FLAG注入点（必需！）
    volumes:                    # 可选：挂载源代码
      - ./src:/var/www/html
```

**命名规范**:

| 类型 | 格式 | 示例 |
|------|------|------|
| **镜像名** | `cyberprism/<题目名字>` | `cyberprism/web-sql-injection` |
| **容器名** | `cyberprism-<题目名字>-${USER_ID}` | `cyberprism-web-sql-injection-123` |

**重要说明**:
- ❌ 不需要添加 `:latest` 或其他tag标签
- ❌ 不需要在名字中包含难度等级
- ✅ 使用描述性的题目名称(如 `web-sql-injection`)

**完整示例**:

```yaml
# web-sql-injection/docker-compose.yml
version: '3.8'

services:
  web:
    build:
      context: .
    image: cyberprism/web-sql-injection
    container_name: cyberprism-web-sql-injection-${USER_ID:-default}
    ports:
      - "80"
    environment:
      - FLAG=${FLAG}
    volumes:
      - ./src:/var/www/html
```

**关键要点**:

| 配置项 | 说明 | 正确示例 | 错误示例 |
|--------|------|---------|---------|
| **ports** | 只写容器端口 | `- "80"` ✅ | `- "8080:80"` ❌ |
| **environment** | 必须包含FLAG变量 | `- FLAG=${FLAG}` ✅ | 没有这一行 ❌ |
| **image** | 使用规范的镜像名 | `cyberprism/web-sql-injection` ✅ | `cyberprism/web-easy:latest` ❌ |

**为什么不能写宿主机端口？**

系统会自动随机分配30000-40000之间的端口。如果你写了固定端口(如`8080:80`)，会导致：
- ❌ 多个用户同时启动时端口冲突
- ❌ 覆盖系统的随机端口分配机制
- ❌ 容器启动失败

#### 2. Dockerfile 规范

**必须包含的元素**:

```dockerfile
FROM <基础镜像>                    # 使用具体版本，不用latest

# 安装依赖
RUN <安装命令>

# 复制文件
COPY ./src /path/to/app

# 设置权限（重要！）
RUN chown -R <用户>:<组> /path/to/app

# 暴露端口（必须与docker-compose.yml一致）
EXPOSE <端口号>

# 启动命令（如果需要）
CMD ["<启动命令>"]
```

**web-easy示例**:

```dockerfile
FROM php:8.1-apache

# 安装MySQL扩展
RUN docker-php-ext-install mysqli pdo pdo_mysql

# 复制文件
COPY ./src /var/www/html/

# 设置权限
RUN chown -R www-data:www-data /var/www/html

# 暴露端口
EXPOSE 80
```

#### 3. Flag读取规范

**✅ 推荐方式**:

```php
// PHP - 从环境变量读取，提供默认值
<?php echo getenv('FLAG') ?: 'FLAG{default}'; ?>
```

**❌ 错误方式**:

```php
// 硬编码FLAG（会导致所有用户看到相同的FLAG）
<?php echo "FLAG{sql_injection_is_easy}"; ?>

// 可能无法读取的方式
<?php echo $_ENV['FLAG']; ?>
```

#### 4. Flag格式规范

**标准格式**: `FLAG{<内容>}`

**内容要求**:
- 小写字母、数字、下划线
- 与题目内容相关
- 长度建议: 20-50字符

**示例**:

| 示例 | 是否合规 | 说明 |
|------|---------|------|
| `FLAG{sql_injection_is_easy}` | ✅ | 标准格式 |
| `FLAG{xxe_attack_2024}` | ✅ | 包含技术名称 |
| `FLAG{c0mm4nd_1nj3ct10n}` | ✅ | 使用数字替代字母 |
| `flag{test}` | ❌ | 开头必须大写 |
| `FLAG{测试}` | ❌ | 不使用中文 |
| `FLAG{Test Case}` | ❌ | 不使用空格 |

#### 5. 目录结构规范

```
challenges/
├── <分类>-<难度>/              # 如: web-easy
│   ├── Dockerfile              # 容器构建文件（必需）
│   ├── docker-compose.yml      # 容器配置文件（必需）
│   ├── src/                    # 题目源代码（必需）
│   │   ├── index.php
│   │   └── ...
│   └── writeup.md              # 解题思路（可选）
└── README.md                   # 本文档
```

---

## ✅ 测试检查清单

### 出题前必检项目

在提交题目到平台之前，请确认以下所有项目：

#### 📁 文件结构检查

- [ ] `Dockerfile` 存在且可构建
- [ ] `docker-compose.yml` 存在且格式正确
- [ ] `src/` 目录包含所有源代码
- [ ] 没有包含敏感信息（密码、密钥等）

#### 🔧 docker-compose.yml 检查

- [ ] 端口配置只写容器端口（如`"80"`）
- [ ] 包含 `FLAG=${FLAG}` 环境变量
- [ ] 如果有多个服务，确保服务名唯一
- [ ] 没有暴露不必要的端口

#### 🐳 Dockerfile 检查

- [ ] 基础镜像版本明确（不用`latest`）
- [ ] 文件权限设置正确
- [ ] `EXPOSE` 的端口与docker-compose.yml一致
- [ ] 构建时间合理（< 5分钟）

#### 🎯 题目功能检查

- [ ] 本地构建成功: `docker-compose build`
- [ ] 本地启动成功: `docker-compose up`
- [ ] FLAG正确注入: `docker-compose exec <service> env | grep FLAG`
- [ ] 可以通过浏览器访问题目
- [ ] 可以通过预期方法获取FLAG

#### 🏁 Flag检查

- [ ] Flag格式: `FLAG{<内容>}`
- [ ] Flag唯一（不与其他题目重复）
- [ ] Flag在代码中通过`getenv('FLAG')`读取
- [ ] Flag不硬编码在代码中
- [ ] Flag长度适中（建议20-50字符）

#### 🔒 安全检查

- [ ] 题目不包含真实漏洞（仅教学用途）
- [ ] 不会对宿主机造成危害
- [ ] 容器内没有提权漏洞
- [ ] 日志不泄露敏感信息

---

## 🧪 本地测试流程

### 1. 构建镜像

```bash
cd challenges/web-easy
docker-compose build
```

### 2. 启动容器（手动注入FLAG）

```bash
# 方式1: 使用环境变量
FLAG=FLAG{test_flag_123} docker-compose up

# 方式2: 创建.env文件
echo "FLAG=FLAG{test_flag_123}" > .env
docker-compose up
```

### 3. 验证FLAG注入

```bash
# 进入容器
docker-compose exec web bash

# 查看环境变量
env | grep FLAG

# 应显示: FLAG=FLAG{test_flag_123}
```

### 4. 访问题目

```bash
# 查看映射端口
docker-compose ps

# 访问题目
curl http://localhost:<端口>
# 或浏览器打开 http://localhost:<端口>
```

### 5. 解题验证

通过预期的解题方法获取FLAG，确认显示的是你设置的FLAG。

### 6. 清理环境

```bash
docker-compose down
docker-compose down -v  # 同时删除数据卷
```

---
## 🐛 常见问题与解决

### Q1: 容器启动失败，提示"Docker配置文件不存在"

**原因**: `docker_compose_file` 路径错误

**解决**:
1. 确认路径是相对于项目根目录
2. 使用正斜杠 `/`（不是反斜杠 `\`）
3. 确认文件确实存在

```bash
# 检查文件
ls -la challenges/web-easy/docker-compose.yml
```

### Q2: 端口冲突，提示"端口已被使用"

**原因**: docker-compose.yml中指定了固定的宿主机端口

**解决**:

```yaml
# ❌ 错误写法
ports:
  - "8080:80"

# ✅ 正确写法
ports:
  - "80"
```

### Q3: FLAG显示为默认值，不是数据库中的FLAG

**原因**: 环境变量注入失败

**检查**:
1. docker-compose.yml中是否包含 `FLAG=${FLAG}`
2. 题目代码中是否正确读取环境变量

```php
// ✅ 正确
<?php echo getenv('FLAG'); ?>

// ❌ 可能失败
<?php echo $_ENV['FLAG']; ?>
```

**调试**:

```bash
# 进入容器查看环境变量
docker exec -it <container_id> env | grep FLAG
```

### Q4: 提交正确的FLAG但验证失败

**原因**: 字符串匹配问题（大小写敏感）

**检查**:
1. FLAG格式是否正确（必须是`FLAG{...}`，不能是`flag{...}`）
2. 是否有多余的空格或换行符
3. 数据库中的FLAG是否与题目中的一致

### Q5: 容器无法访问，浏览器显示连接超时

**原因**: 防火墙阻止了30000-40000端口

**解决**:

```bash
# CentOS/RHEL
firewall-cmd --zone=public --add-port=30000-40000/tcp --permanent
firewall-cmd --reload

# Ubuntu/Debian
ufw allow 30000:40000/tcp
ufw reload
```

### Q6: 如何查看和管理Docker镜像

**查看所有CyberPrism镜像**:

```bash
# 查看所有cyberprism镜像
docker images | grep cyberprism

# 或使用filter
docker images --filter=reference='cyberprism/*'
```

**按分类查看镜像**:

```bash
# 查看所有web类题目镜像
docker images | grep "cyberprism/web"

# 查看特定难度的镜像
docker images | grep "cyberprism/web-easy"
```

**按标签查看镜像**:

```bash
# 查看特定漏洞类型
docker images cyberprism/web-easy:sql-injection
docker images cyberprism/web-medium:file-inclusion
docker images cyberprism/web-hard:command-injection
```

**清理未使用的镜像**:

```bash
# 删除悬空镜像（dangling images）
docker image prune

# 删除所有未使用的镜像
docker image prune -a

# 删除特定题目的镜像
docker rmi cyberprism/web-easy:latest
docker rmi cyberprism/web-easy:sql-injection
```

**批量删除CyberPrism镜像**:

```bash
# 删除所有cyberprism镜像
docker rmi $(docker images -q 'cyberprism/*')

# 强制删除
docker rmi -f $(docker images -q 'cyberprism/*')
```

---

## 📦 镜像命名规范详解

### 镜像命名结构

```
cyberprism/<题目名字>
    │         │
    │         └─ 题目的唯一名称（小写、连字符分隔）
    └─ 项目名称（固定前缀）
```

### 命名最佳实践

**✅ 推荐的命名方式**:

1. **描述性强**: 名称应该反映题目的主要漏洞或技术点
   - ✅ `cyberprism/web-sql-injection`
   - ✅ `cyberprism/xxe-attack`
   - ✅ `cyberprism/jwt-crack`

2. **使用连字符**: 多个单词用连字符分隔
   - ✅ `cyberprism/file-inclusion`
   - ❌ `cyberprism/fileinclusion`
   - ❌ `cyberprism/file_inclusion`

3. **全部小写**: 所有字母使用小写
   - ✅ `cyberprism/web-xss`
   - ❌ `cyberprism/Web-XSS`

4. **简洁明了**: 避免过长的名称
   - ✅ `cyberprism/csrf-bypass`
   - ❌ `cyberprism/cross-site-request-forgery-protection-bypass`

**❌ 避免的命名方式**:

1. **不要添加难度标识**
   - ❌ `cyberprism/web-easy`
   - ❌ `cyberprism/sql-injection-hard`
   - ✅ `cyberprism/web-sql-injection`

2. **不要添加版本号或标签**
   - ❌ `cyberprism/web-xss:v1.0`
   - ❌ `cyberprism/web-xss:latest`
   - ✅ `cyberprism/web-xss`

### 常见题目类型命名参考

**Web安全**:
- `cyberprism/web-sql-injection` - SQL注入
- `cyberprism/web-xss` - 跨站脚本
- `cyberprism/file-inclusion` - 文件包含
- `cyberprism/command-injection` - 命令注入
- `cyberprism/file-upload` - 文件上传

**二进制安全**:
- `cyberprism/stack-overflow` - 栈溢出
- `cyberprism/heap-overflow` - 堆溢出
- `cyberprism/format-string` - 格式化字符串

**密码学**:
- `cyberprism/rsa-attack` - RSA攻击
- `cyberprism/hash-collision` - 哈希碰撞

### 完整示例

```yaml
# web-sql-injection/docker-compose.yml
services:
  web:
    build:
      context: .
    image: cyberprism/web-sql-injection
    container_name: cyberprism-web-sql-injection-${USER_ID:-default}

# file-inclusion/docker-compose.yml
services:
  web:
    build:
      context: .
    image: cyberprism/file-inclusion
    container_name: cyberprism-file-inclusion-${USER_ID:-default}

# command-injection/docker-compose.yml
services:
  web:
    build:
      context: .
    image: cyberprism/command-injection
    container_name: cyberprism-command-injection-${USER_ID:-default}
```

### 镜像管理

**查看所有CyberPrism镜像**:
```bash
docker images --filter=reference='cyberprism/*'
```

**删除单个镜像**:
```bash
docker rmi cyberprism/web-sql-injection
```

**删除所有CyberPrism镜像**:
```bash
docker images --filter=reference='cyberprism/*' -q | xargs docker rmi
```

---

## 📚 题目模板

### Web题目模板（PHP）

**Dockerfile**:

```dockerfile
FROM php:8.1-apache

# 安装依赖
RUN docker-php-ext-install mysqli pdo pdo_mysql

# 复制源码
COPY ./src /var/www/html/

# 设置权限
RUN chown -R www-data:www-data /var/www/html

# 暴露端口
EXPOSE 80
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
    image: cyberprism/<题目名字>
    container_name: cyberprism-<题目名字>-${USER_ID:-default}
    ports:
      - "80"
    environment:
      - FLAG=${FLAG}
```

**src/index.php**:

```php
<!DOCTYPE html>
<html>
<head>
    <title>CTF Challenge</title>
</head>
<body>
    <h1>Welcome to CTF Challenge</h1>

    <?php
    // 你的题目逻辑

    // 最终显示FLAG
    if ($满足条件) {
        echo "<p>FLAG: " . getenv('FLAG') . "</p>";
    }
    ?>
</body>
</html>
```

### Python Flask题目模板

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY ./src .

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
    image: cyberprism/<题目名字>
    container_name: cyberprism-<题目名字>-${USER_ID:-default}
    ports:
      - "5000"
    environment:
      - FLAG=${FLAG}
```

**src/app.py**:

```python
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    flag = os.getenv('FLAG', 'FLAG{default}')
    return render_template('index.html', flag=flag)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🛠️ 镜像管理工具

为了方便镜像的管理和维护，我们提供了专用的管理脚本。

### Linux/Mac 用户

使用 Bash 脚本：

```bash
# 赋予执行权限
chmod +x scripts/manage-images.sh

# 查看所有镜像
./scripts/manage-images.sh list

# 查看Web类题目镜像
./scripts/manage-images.sh list-web

# 查看简单难度镜像
./scripts/manage-images.sh list-easy

# 查看镜像详细信息
./scripts/manage-images.sh info cyberprism/web-easy:latest

# 构建单个题目
./scripts/manage-images.sh build challenges/web-easy

# 构建所有题目
./scripts/manage-images.sh build-all

# 显示统计信息
./scripts/manage-images.sh stats

# 清理悬空镜像
./scripts/manage-images.sh clean-dangling

# 查看帮助
./scripts/manage-images.sh help
```

### Windows 用户

使用 PowerShell 脚本：

```powershell
# 查看所有镜像
.\scripts\manage-images.ps1 list

# 查看Web类题目镜像
.\scripts\manage-images.ps1 list-web

# 查看镜像详细信息
.\scripts\manage-images.ps1 info cyberprism/web-easy:latest

# 构建单个题目
.\scripts\manage-images.ps1 build challenges\web-easy

# 构建所有题目
.\scripts\manage-images.ps1 build-all

# 显示统计信息
.\scripts\manage-images.ps1 stats

# 清理悬空镜像
.\scripts\manage-images.ps1 clean-dangling

# 查看帮助
.\scripts\manage-images.ps1 help
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `list` | 列出所有CyberPrism镜像 |
| `list-web` | 列出Web类题目镜像 |
| `list-easy` | 列出简单难度镜像 |
| `info <镜像名>` | 显示镜像详细信息 |
| `build <目录>` | 构建指定题目镜像 |
| `build-all` | 构建所有题目镜像 |
| `stats` | 显示镜像统计信息 |
| `clean-dangling` | 清理悬空镜像 |
| `clean-unused` | 清理未使用镜像 |
| `clean-all` | 删除所有CyberPrism镜像 |

---

## 📞 技术支持

### 核心代码位置

- 容器管理器: `backend/app/docker_challenges/manager.py`
- 容器路由: `backend/app/routes/containers.py`
- 题目路由: `backend/app/routes/challenges.py`
- 数据模型: `backend/app/models/__init__.py`

### 获取帮助

- 查看系统日志: `docker logs <container_id>`
- 检查数据库: `mysql -u root -p cyberprism`
- 调试容器: `docker exec -it <container_id> bash`

---

**最后更新**: 2024-12-27
**版本**: v2.0
