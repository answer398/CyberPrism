# 🚀 CyberPrism 快速启动指南

5分钟启动你的CTF能力评估平台!

## 📋 前置检查

```bash
# 检查Python版本(需要3.9+)
python --version

# 检查Node.js版本(需要16+)
node --version

# 检查Docker(可选,用于靶场)
docker --version
```

## 🎯 快速启动

### 步骤1: 启动后端(2分钟)

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

✅ 看到"✓ 默认管理员账户已创建"表示成功!

后端地址: `http://localhost:5000`
默认管理员: `admin` / `admin123`

### 步骤2: 启动前端(3分钟)

打开新终端:

```bash
# 进入前端目录
cd frontend

# 安装依赖(首次需要几分钟)
npm install

# 启动开发服务器
npm run dev
```

✅ 看到"Local: http://localhost:3000"表示成功!

前端地址: `http://localhost:3000`

## 🎮 开始使用

### 方案A: 注册新用户(推荐)

1. 浏览器访问 `http://localhost:3000`
2. 点击"还没有账号?立即注册"
3. 填写注册信息
4. 自动登录进入平台

### 方案B: 使用管理员账户

1. 浏览器访问 `http://localhost:3000/login`
2. 输入 `admin` / `admin123`
3. 登录后进入管理后台

## 📝 添加第一道题目

### 方法1: 使用curl(快速)

```bash
# 先获取管理员token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*"' \
  | cut -d'"' -f4)

# 添加选择题
curl -X POST http://localhost:5000/api/admin/challenges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SQL注入基础",
    "description": "测试SQL注入基础知识",
    "category": "信息收集与侦察",
    "type": "choice",
    "difficulty": "easy",
    "points": 50,
    "question": "以下哪个是SQL注入的常见payload?",
    "options": {
      "A": "SELECT * FROM users",
      "B": "admin OR 1=1",
      "C": "DROP TABLE users",
      "D": "UPDATE users SET"
    },
    "correct_answer": "B",
    "skill_tags": {
      "信息收集与侦察": "信息收集"
    }
  }'
```

### 方法2: 使用Python脚本

创建`add_challenge.py`:

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 登录获取token
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 添加题目
challenge = {
    "title": "SQL注入基础",
    "description": "测试SQL注入基础知识",
    "category": "信息收集与侦察",
    "type": "choice",
    "difficulty": "easy",
    "points": 50,
    "question": "以下哪个是SQL注入的常见payload?",
    "options": {
        "A": "SELECT * FROM users",
        "B": "admin' OR '1'='1",
        "C": "DROP TABLE users",
        "D": "UPDATE users SET"
    },
    "correct_answer": "B",
    "skill_tags": {
        "信息收集与侦察": "信息收集"
    }
}

response = requests.post(
    f"{BASE_URL}/admin/challenges",
    headers=headers,
    json=challenge
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
```

运行:
```bash
pip install requests
python add_challenge.py
```

## 🐳 启动靶场题(可选)

如果安装了Docker,可以测试靶场:

```bash
# 测试SQL注入靶场
cd challenges/web-easy
docker-compose up -d

# 查看端口
docker-compose ps

# 浏览器访问 http://localhost:<端口>
```

解题方法:
- 用户名: `admin' OR '1'='1`
- 密码: 随意
- 成功后看到FLAG

停止容器:
```bash
docker-compose down
```

## ✅ 验证安装

访问 `http://localhost:3000`:
- [ ] 能看到登录页面
- [ ] 能成功注册/登录
- [ ] 能看到Dashboard
- [ ] 能进入"题目挑战"页面
- [ ] 能看到刚添加的题目
- [ ] 提交答案后能解锁技能
- [ ] "个人资料"页面能看到能力矩阵图

## 🔧 常见问题

### Q1: 后端启动报错"Address already in use"
**A**: 5000端口被占用,修改`backend/app.py`最后一行端口号

### Q2: 前端启动报错"Cannot find module"
**A**: 删除`node_modules`和`package-lock.json`,重新`npm install`

### Q3: 前端页面空白
**A**:
1. 检查后端是否运行: 访问`http://localhost:5000/health`
2. 打开浏览器控制台查看错误
3. 检查vite.config.js的proxy配置

### Q4: 能力矩阵不显示
**A**:
1. 先做一道题解锁技能
2. 刷新页面
3. 检查浏览器控制台是否有错误

## 📚 下一步

1. 阅读[部署文档](docs/DEPLOYMENT.md)了解详细配置
2. 查看[API文档](docs/API.md)了解接口细节
3. 阅读[靶场说明](challenges/README.md)学习出题方法
4. 查看[测试指南](docs/TESTING.md)进行完整测试

## 🎉 完成!

现在你可以:
- ✨ 开始做题并解锁技能
- 📊 查看你的能力矩阵
- 🏆 和其他用户PK排行榜
- 🎯 管理平台(管理员)

**祝使用愉快!** 🚀

---

遇到问题?检查[项目总结](docs/PROJECT_SUMMARY.md)
