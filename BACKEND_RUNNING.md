# ✅ 后端启动成功!

恭喜!你的CyberPrism后端已经成功运行了!

## 当前状态

✅ **后端服务运行中**
- 地址: http://127.0.0.1:5000
- 状态: 正常运行
- 管理员账户: `admin` / `admin123`

## 关于Docker警告

你看到的Docker警告是正常的:
```
警告: 无法连接到Docker daemon
```

**原因**:
- Windows上Docker Desktop可能未启动
- 或者Docker配置需要调整

**影响**:
- ⚠️ 靶场题(Docker类型)暂时无法使用
- ✅ 选择题功能完全正常
- ✅ 所有其他功能正常

**如何修复**(可选):
1. 启动Docker Desktop
2. 确保Docker正在运行: `docker ps`
3. 重启后端服务

**如果不需要靶场题**: 可以忽略此警告,专注于选择题功能。

## 下一步

### 方案1: 测试API(推荐)

打开新终端,测试健康检查:
```bash
curl http://localhost:5000/health
```

应返回:
```json
{"status":"healthy"}
```

### 方案2: 启动前端

打开新终端:
```bash
cd frontend
npm install
npm run dev
```

然后访问 http://localhost:3000

### 方案3: 添加测试题目

使用Python脚本快速添加题目:

创建 `backend/add_test_challenge.py`:
```python
import requests

BASE_URL = "http://localhost:5000/api"

# 登录
login_res = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 添加选择题
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

res = requests.post(f"{BASE_URL}/admin/challenges", headers=headers, json=challenge)
print(f"状态: {res.status_code}")
print(f"响应: {res.json()}")
```

运行:
```bash
pip install requests
python backend/add_test_challenge.py
```

## 项目结构变化

**重要**: 启动文件已从 `app.py` 改为 `run.py`

- ❌ 旧方式: `python app.py`
- ✅ 新方式: `python run.py`

原因: 避免模块导入冲突

## 常用命令

```bash
# 启动后端
cd backend
python run.py

# 测试健康检查
curl http://localhost:5000/health

# 查看数据库(如果安装了sqlite3)
sqlite3 backend/cyberprism.db
sqlite> .tables
sqlite> SELECT * FROM users;
sqlite> .quit

# 重置数据库
rm backend/cyberprism.db
python backend/run.py
```

## 需要帮助?

- 📚 部署文档: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- 🔧 测试指南: [docs/TESTING.md](docs/TESTING.md)
- 📖 API文档: [docs/API.md](docs/API.md)
- 🚀 快速启动: [QUICKSTART.md](QUICKSTART.md)

**一切就绪!开始你的CTF之旅吧!** 🎉
