# CyberPrism CTF 出题与测试指南

## 📋 目录
- [靶场题目列表](#靶场题目列表)
- [系统核心机制确认](#系统核心机制确认)
- [出题规范与注意事项](#出题规范与注意事项)
- [测试检查清单](#测试检查清单)
- [部署说明](#部署说明)

---

## 🎯 靶场题目列表

本目录包含三个不同难度的Web安全挑战题目,供CyberPrism平台使用。

### 1. Web-Easy: SQL注入 (简单)
**目录**: `web-easy/`
**漏洞类型**: SQL Injection
**技能标签**: 信息收集 / 利用公共漏洞

**描述**:
一个存在SQL注入漏洞的简单登录系统。用户需要绕过登录验证,以管理员身份登录并获取FLAG。

**解题思路**:
- 在用户名字段输入: `admin' OR '1'='1`
- 密码字段随意输入
- 系统会执行有漏洞的SQL查询并返回管理员用户
- 登录成功后查看FLAG

**配置**:
- 容器端口: 80
- FLAG注入方式: 环境变量
- docker-compose路径: `challenges/web-easy/docker-compose.yml`

**建议FLAG**: `FLAG{sql_1nj3ct10n_1s_34sy}`

---

### 2. Web-Medium: 文件包含漏洞 (中等)
**目录**: `web-medium/`
**漏洞类型**: Local File Inclusion (LFI)
**技能标签**: 网络扫描 / 利用公共漏洞

**描述**:
一个简易博客系统,通过URL参数加载页面内容,存在本地文件包含漏洞。

**解题思路**:
- 分析URL参数: `?page=home`
- 尝试路径穿越: `?page=../../../../flag`
- 读取系统文件: `?page=../../../../flag.txt`
- 获取FLAG内容

**配置**:
- 容器端口: 80
- FLAG位置: /flag.txt
- docker-compose路径: `challenges/web-medium/docker-compose.yml`

**建议FLAG**: `FLAG{l0c4l_f1l3_1nclus10n_vuln3r4b1l1ty}`

---

### 3. Web-Hard: 命令注入 (困难)
**目录**: `web-hard/`
**漏洞类型**: Command Injection
**技能标签**: 利用公共漏洞 / 命令与控制

**描述**:
一个网络诊断工具,允许用户ping任意主机。虽然有基本的字符过滤,但可以绕过执行系统命令。

**解题思路**:
- 系统过滤了常见的命令注入字符: `;`, `&&`, `||`, `|`, `` ` ``, `$`, `(`, `)`
- 使用换行符绕过: `%0a` (URL编码的\n)
- Payload示例: `8.8.8.8%0acat /flag.txt`
- 或使用: `8.8.8.8%0als -la /`

**配置**:
- 容器端口: 5000
- FLAG位置: /flag.txt (权限400)
- docker-compose路径: `challenges/web-hard/docker-compose.yml`

**建议FLAG**: `FLAG{c0mm4nd_1nj3ct10n_m4st3r}`

---

## ✅ 系统核心机制确认

### 1. 端口映射是否随机？

**答案：是的，完全随机分配！**

**机制说明** (`backend/app/docker_challenges/manager.py:37-42`):

```python
# 生成随机端口(30000-40000)
host_port = random.randint(30000, 40000)

# 检查端口是否已被使用（防止冲突）
while ContainerInstance.query.filter_by(host_port=host_port, status='running').first():
    host_port = random.randint(30000, 40000)
```

**端口分配特性**:
- **端口范围**: 30000-40000（共10000个可用端口）
- **分配方式**: 随机生成 + 数据库碰撞检测
- **冲突处理**: while循环重试直到找到未被使用的端口
- **并发安全**: 通过查询数据库中`status='running'`的记录防止冲突

**容器启动时的端口映射**:

```python
container = self.client.containers.run(
    image=image_name,
    ports={f"{challenge.container_port}/tcp": host_port},
    # challenge.container_port = 80 (从docker-compose.yml读取)
    # host_port = 35267 (系统随机分配)
)
```

**示例**:
- 容器内: `http://localhost:80`
- 宿主机: `http://服务器IP:35267` (每次启动都不同)

---

### 2. Flag验证机制

**答案：精确字符串匹配（大小写敏感）**

**验证逻辑** (`backend/app/routes/challenges.py:94-97`):

```python
# Docker靶场Flag验证
if challenge.type == 'docker':
    is_correct = submitted_answer == challenge.flag  # 精确匹配!
```

**验证流程**:

```
用户提交 FLAG{sql_injection_is_easy}
    ↓
POST /api/challenges/123/submit
    ↓
检查是否已正确解答过（防止重复得分）
    ↓
字符串比较: submitted_answer == challenge.flag
    ↓
    ├─ 匹配成功
    │   ├─ 创建 Submission(is_correct=True)
    │   ├─ 解锁技能标签 (skill_tags)
    │   ├─ 增加用户积分 (points)
    │   └─ 返回 {is_correct: true, points: 100}
    │
    └─ 匹配失败
        ├─ 创建 Submission(is_correct=False)
        └─ 返回 {is_correct: false, points: 0}
```

**Flag注入机制** (`backend/app/docker_challenges/manager.py:61-66`):

```python
# 获取docker-compose.yml中的环境变量配置
env_vars = service_config.get('environment', {})

# 注入真实FLAG
if isinstance(env_vars, list):
    env_vars.append(f"FLAG={challenge.flag}")
else:
    env_vars['FLAG'] = challenge.flag
```

**在题目代码中读取FLAG**:

```php
// PHP示例（推荐）
<?php echo getenv('FLAG') ?: 'FLAG{default}'; ?>

// 或
<?php echo getenv('FLAG'); ?>
```

```python
# Python示例
import os
flag = os.getenv('FLAG', 'FLAG{default}')
```

---

### 3. 镜像自动构建机制

**答案：支持自动构建，无需手动预先构建！**

**工作流程** (`backend/app/docker_challenges/manager.py:58-95`):

```python
# 1. 确定镜像名称
image_name = service_config.get('image')  # 如: cyberprism/web-easy:latest

# 2. 检查镜像是否存在
try:
    self.client.images.get(image_name)
    print(f"镜像 {image_name} 已存在，直接使用")
except docker.errors.ImageNotFound:
    # 3. 镜像不存在，自动构建
    print(f"镜像 {image_name} 不存在，开始构建...")
    self.client.images.build(
        path=build_path,
        tag=image_name,
        rm=True
    )
```

**自动构建特性**:
- **智能检测**: 自动检查镜像是否存在
- **按需构建**: 首次启动时自动构建
- **镜像复用**: 构建一次，后续直接使用
- **命名规范**: 使用docker-compose.yml中定义的镜像名

**启动时间对比**:

| 场景 | 耗时 | 说明 |
|------|------|------|
| **首次启动** | 2-5分钟 | 需要拉取基础镜像 + 构建题目镜像 |
| **后续启动** | 5-10秒 | 镜像已存在，直接启动容器 |

**推荐做法**:

✅ **开发/测试环境**: 使用自动构建，方便快速测试

✅ **生产/比赛环境**: 预先构建所有镜像，确保启动速度
```bash
# 使用管理脚本批量构建
./scripts/manage-images.sh build-all

# 或手动构建
cd challenges/web-easy && docker-compose build
cd challenges/web-medium && docker-compose build
cd challenges/web-hard && docker-compose build
```

**详细说明**: 参见 [AUTO-BUILD-GUIDE.md](AUTO-BUILD-GUIDE.md)

---

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

## 🚀 部署说明

### 添加题目到数据库

管理员需要通过后台添加题目到数据库：

#### 题目1: SQL注入（简单）

```json
{
  "title": "简单登录系统",
  "description": "一个存在SQL注入漏洞的登录系统,尝试以管理员身份登录获取FLAG。",
  "category": "漏洞利用与攻击",
  "type": "docker",
  "difficulty": "easy",
  "points": 100,
  "flag": "FLAG{sql_1nj3ct10n_1s_34sy}",
  "docker_compose_file": "challenges/web-easy/docker-compose.yml",
  "container_port": 80,
  "skill_tags": {
    "信息收集与侦察": "信息收集",
    "漏洞利用与攻击": "利用公共漏洞"
  }
}
```

#### 题目2: 文件包含漏洞（中等）

```json
{
  "title": "简易博客系统",
  "description": "一个存在本地文件包含漏洞的博客系统,读取系统敏感文件获取FLAG。",
  "category": "漏洞利用与攻击",
  "type": "docker",
  "difficulty": "medium",
  "points": 200,
  "flag": "FLAG{l0c4l_f1l3_1nclus10n_vuln3r4b1l1ty}",
  "docker_compose_file": "challenges/web-medium/docker-compose.yml",
  "container_port": 80,
  "skill_tags": {
    "信息收集与侦察": "网络扫描",
    "漏洞利用与攻击": "利用公共漏洞"
  }
}
```

#### 题目3: 命令注入（困难）

```json
{
  "title": "网络诊断工具",
  "description": "一个带有基本过滤的网络诊断工具,绕过限制执行系统命令获取FLAG。",
  "category": "漏洞利用与攻击",
  "type": "docker",
  "difficulty": "hard",
  "points": 300,
  "flag": "FLAG{c0mm4nd_1nj3ct10n_m4st3r}",
  "docker_compose_file": "challenges/web-hard/docker-compose.yml",
  "container_port": 5000,
  "skill_tags": {
    "漏洞利用与攻击": "利用公共漏洞",
    "防御规避与反侦察": "命令与控制"
  }
}
```

**⚠️ 重要提示**:
- `docker_compose_file` 必须是相对于项目根目录的路径
- 使用正斜杠 `/`（不是反斜杠 `\`）
- Linux示例: `challenges/web-easy/docker-compose.yml`
- Windows也使用: `challenges/web-easy/docker-compose.yml`（不是 `challenges\web-easy\docker-compose.yml`）

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
