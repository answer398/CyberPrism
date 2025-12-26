# CyberPrism 部署和使用文档

## 目录
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [初始化数据](#初始化数据)
- [使用指南](#使用指南)
- [管理员操作](#管理员操作)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求
- CPU: 2核心及以上
- 内存: 4GB及以上
- 磁盘: 20GB及以上

### 软件要求
- Python 3.9+
- Node.js 16+
- Docker 20.10+
- Docker Compose 2.0+

---

## 快速开始

### 1. 克隆项目(如果从Git获取)
```bash
# 如果是新创建的项目,跳过此步
cd CyberPrism
```

### 2. 后端部署

#### 2.1 安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 2.2 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件,修改以下配置:
# - SECRET_KEY: Flask密钥(建议生成随机字符串)
# - JWT_SECRET_KEY: JWT密钥(建议生成随机字符串)
```

生成随机密钥(Python):
```python
import secrets
print(secrets.token_hex(32))
```

#### 2.3 初始化数据库
```bash
# 在backend目录下执行
python app.py
```

首次运行会自动:
- 创建SQLite数据库
- 创建所有数据表
- 创建默认管理员账户: `admin` / `admin123`

**重要**: 部署到生产环境后请立即修改管理员密码!

#### 2.4 启动后端服务
```bash
# 开发环境
python app.py

# 生产环境(推荐使用gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

后端API将运行在: `http://localhost:5000`

### 3. 前端部署

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 配置API地址
编辑 [vite.config.js](frontend/vite.config.js),确保proxy配置指向正确的后端地址:
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // 修改为实际后端地址
      changeOrigin: true
    }
  }
}
```

#### 3.3 启动前端
```bash
# 开发环境
npm run dev

# 生产环境构建
npm run build
# 构建产物在 dist/ 目录,可部署到Nginx等Web服务器
```

前端将运行在: `http://localhost:3000`

---

## 初始化数据

### 1. 登录管理员账户
- 访问前端: `http://localhost:3000`
- 使用默认管理员登录: `admin` / `admin123`

### 2. 添加靶场题目

管理员登录后,通过API添加题目。示例使用curl:

#### 添加SQL注入题目:
```bash
curl -X POST http://localhost:5000/api/admin/challenges \
  -H "Authorization: Bearer <你的JWT令牌>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "简单登录系统",
    "description": "一个存在SQL注入漏洞的登录系统,尝试以管理员身份登录获取FLAG。",
    "category": "漏洞利用与攻击",
    "type": "docker",
    "difficulty": "easy",
    "points": 100,
    "flag": "FLAG{sql_1nj3ct10n_1s_34sy}",
    "docker_compose_file": "D:\\Codes\\CyberPrism\\challenges\\web-easy\\docker-compose.yml",
    "container_port": 80,
    "skill_tags": {
      "信息收集与侦察": "信息收集",
      "漏洞利用与攻击": "利用公共漏洞"
    }
  }'
```

**注意**:
- 将 `<你的JWT令牌>` 替换为实际登录后获取的token
- `docker_compose_file` 路径需要使用绝对路径
- Windows系统路径使用双反斜杠 `\\`

#### 添加选择题示例:
```bash
curl -X POST http://localhost:5000/api/admin/challenges \
  -H "Authorization: Bearer <你的JWT令牌>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SQL注入基础知识",
    "description": "测试SQL注入的基础知识",
    "category": "信息收集与侦察",
    "type": "choice",
    "difficulty": "easy",
    "points": 50,
    "question": "以下哪个SQL注入Payload可以绕过登录验证?",
    "options": {
      "A": "admin AND 1=1",
      "B": "admin OR 1=1",
      "C": "admin XOR 1=1",
      "D": "admin NOT 1=1"
    },
    "correct_answer": "B",
    "skill_tags": {
      "信息收集与侦察": "信息收集"
    }
  }'
```

### 3. 测试靶场环境

在添加靶场题目前,建议先测试Docker环境:

```bash
# 测试web-easy
cd challenges/web-easy
docker-compose up -d
# 访问 http://localhost:<随机端口> 测试
docker-compose down

# 测试其他靶场...
```

---

## 使用指南

### 普通用户流程

#### 1. 注册账号
- 访问 `http://localhost:3000/register`
- 填写用户名、邮箱、姓名、密码等信息
- 点击注册

#### 2. 登录系统
- 访问 `http://localhost:3000/login`
- 输入用户名和密码登录

#### 3. 挑战题目

**选择题**:
- 进入"题目挑战"页面
- 筛选或查看题目列表
- 点击题目查看详情
- 选择答案并提交
- 答对后自动解锁相应技能标签

**靶场题**:
- 进入"题目挑战"页面
- 选择Docker类型的题目
- 点击"启动容器"
- 等待容器启动完成(约10-30秒)
- 获取访问地址(格式: `http://服务器IP:端口`)
- 在浏览器中访问靶场
- 解题后获取FLAG
- 提交FLAG到平台
- 完成后可以手动停止容器或等待60分钟自动过期

#### 4. 查看能力矩阵
- 进入"个人资料"页面
- 查看技能矩阵热力图
- 绿色方块表示已解锁的技能
- 查看已解锁技能列表

#### 5. 管理容器
- 进入"我的容器"页面
- 查看当前运行的容器
- 可以延长容器时间(每次10-60分钟)
- 可以手动停止不需要的容器

#### 6. 查看排行榜
- 进入"排行榜"页面
- 查看所有用户的解题排名
- 排名依据正确解答数量

---

## 管理员操作

### 1. 用户管理
- 查看所有用户列表
- 查看用户详细信息和技能矩阵
- 修改用户信息(姓名、邮箱、权限等)
- 重置用户密码
- 删除用户(不能删除管理员)

### 2. 题目管理
- 添加新题目(选择题或靶场题)
- 编辑题目信息
- 激活/禁用题目
- 删除题目
- 查看题目解答统计

### 3. 容器管理
- 查看所有用户的运行中容器
- 查看容器归属用户
- 强制停止任何容器
- 批量清理过期容器

### 4. 平台统计
- 查看总用户数
- 查看总题目数
- 查看总提交数和正确率
- 查看运行中容器数量

---

## Docker配置注意事项

### Windows系统Docker配置

如果你使用Windows系统,需要确保:

1. **安装Docker Desktop**
   - 下载并安装Docker Desktop for Windows
   - 启用WSL 2后端

2. **配置Docker权限**
   - 确保Docker daemon正在运行
   - 在backend目录下创建`.env`文件时,`DOCKER_HOST`可能需要调整:
     ```
     # Windows上通常使用
     DOCKER_HOST=npipe:////./pipe/docker_engine

     # 或者使用默认值(让docker-py自动检测)
     # DOCKER_HOST=
     ```

3. **路径处理**
   - Windows路径在docker-compose.yml中需要转换
   - Python代码会自动处理,但配置文件中的路径要用绝对路径

### Linux系统Docker配置

1. **安装Docker**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose

   # 启动Docker服务
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **配置用户权限**
   ```bash
   # 将当前用户添加到docker组
   sudo usermod -aG docker $USER

   # 重新登录或执行
   newgrp docker
   ```

3. **配置.env**
   ```
   DOCKER_HOST=unix:///var/run/docker.sock
   ```

---

## 数据库备份

### 备份SQLite数据库
```bash
# 在backend目录下
cp cyberprism.db cyberprism.db.backup_$(date +%Y%m%d)
```

### 恢复数据库
```bash
cp cyberprism.db.backup_20231201 cyberprism.db
```

---

## 常见问题

### 1. 后端启动报错 "No module named 'flask'"
**解决**: 确保已安装所有依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. Docker容器启动失败
**可能原因**:
- Docker daemon未运行
- docker-compose文件路径错误
- 端口已被占用

**解决**:
- 检查Docker服务状态: `docker ps`
- 检查docker_compose_file路径是否为绝对路径
- 查看错误日志

### 3. 前端无法连接后端API
**解决**:
- 检查后端是否在运行: `http://localhost:5000/health`
- 检查vite.config.js中的proxy配置
- 检查浏览器控制台的CORS错误

### 4. JWT token过期
**解决**: 重新登录获取新token,token有效期为24小时

### 5. 靶场容器无法访问
**可能原因**:
- 容器启动失败
- 端口映射错误
- 防火墙阻止

**解决**:
- 使用`docker ps`查看容器状态
- 检查防火墙规则
- 查看容器日志: `docker logs <container_id>`

### 6. 能力矩阵不显示
**解决**:
- 检查浏览器控制台是否有错误
- 确保已安装ECharts: `npm install echarts`
- 检查技能标签数据是否正确

---

## 安全建议

1. **修改默认管理员密码**: 首次部署后立即修改
2. **使用HTTPS**: 生产环境建议配置SSL证书
3. **定期备份数据库**: 避免数据丢失
4. **限制Docker资源**: 防止容器占用过多资源
5. **设置容器超时**: 已实现60分钟自动过期
6. **审核用户提交**: 监控异常提交行为

---

## 技术支持

如有问题,请检查:
1. 后端日志
2. 前端浏览器控制台
3. Docker容器日志
4. 数据库完整性

项目结构:
```
CyberPrism/
├── backend/          # Flask后端
│   ├── app/
│   │   ├── models/   # 数据库模型
│   │   ├── routes/   # API路由
│   │   ├── utils/    # 工具函数
│   │   └── docker_challenges/  # Docker管理
│   ├── app.py        # 应用入口
│   └── requirements.txt
├── frontend/         # Vue前端
│   ├── src/
│   │   ├── api/      # API封装
│   │   ├── views/    # 页面组件
│   │   └── router/   # 路由配置
│   └── package.json
├── challenges/       # 靶场题目
│   ├── web-easy/     # SQL注入
│   ├── web-medium/   # 文件包含
│   └── web-hard/     # 命令注入
└── docs/            # 文档
```

---

**祝你使用愉快!**
