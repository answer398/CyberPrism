# CyberPrism 快速测试指南

## 测试后端

### 1. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python app.py
```

看到以下输出表示成功:
```
✓ 默认管理员账户已创建 (admin/admin123)
 * Running on http://0.0.0.0:5000
```

### 2. 测试健康检查
```bash
curl http://localhost:5000/health
```

应返回:
```json
{"status":"healthy"}
```

### 3. 测试用户注册
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "display_name": "测试用户",
    "common_id": "test001"
  }'
```

应返回包含`access_token`的JSON。

### 4. 测试管理员登录
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

记录返回的`access_token`,后续测试需要使用。

### 5. 添加测试题目
将`<TOKEN>`替换为上一步获取的token:

```bash
curl -X POST http://localhost:5000/api/admin/challenges \
  -H "Authorization: Bearer <TOKEN>" \
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

### 6. 获取题目列表
```bash
curl http://localhost:5000/api/challenges/ \
  -H "Authorization: Bearer <TOKEN>"
```

### 7. 提交答案测试
假设题目ID为1:

```bash
curl -X POST http://localhost:5000/api/challenges/1/submit \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"answer": "B"}'
```

应返回:
```json
{
  "is_correct": true,
  "message": "恭喜!答案正确!",
  "points": 50
}
```

### 8. 查看用户资料(验证技能解锁)
```bash
curl http://localhost:5000/api/users/profile \
  -H "Authorization: Bearer <TOKEN>"
```

应该能看到解锁的技能标签。

## 测试前端

### 1. 安装依赖并启动
```bash
cd frontend
npm install
npm run dev
```

### 2. 浏览器访问
打开 `http://localhost:3000`

### 3. 测试流程
1. 注册新用户
2. 登录
3. 查看Dashboard
4. 进入题目挑战
5. 提交答案
6. 查看个人资料(应该能看到能力矩阵图)

## 测试靶场环境

### 前提: 确保Docker已安装并运行

### 1. 测试SQL注入靶场
```bash
cd challenges/web-easy
docker-compose up -d
```

查看容器状态:
```bash
docker-compose ps
```

访问靶场(端口可能不同):
```
http://localhost:<端口>
```

解题:
- 用户名输入: `admin' OR '1'='1`
- 密码随意
- 成功后应显示FLAG

停止容器:
```bash
docker-compose down
```

### 2. 测试文件包含靶场
```bash
cd challenges/web-medium
docker-compose up -d
```

访问并尝试:
```
http://localhost:<端口>/?page=../../../../flag
```

### 3. 测试命令注入靶场
```bash
cd challenges/web-hard
docker-compose up -d
```

在Ping输入框中尝试:
```
8.8.8.8%0acat /flag.txt
```

## 完整集成测试

使用Python脚本测试完整流程:

```python
import requests
import time

BASE_URL = "http://localhost:5000/api"

# 1. 注册用户
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "integration_test",
    "email": "integration@test.com",
    "password": "test123",
    "display_name": "集成测试用户"
})
print(f"注册: {response.status_code}")
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. 获取题目列表
response = requests.get(f"{BASE_URL}/challenges/", headers=headers)
print(f"获取题目: {response.status_code}, 题目数: {len(response.json())}")

# 3. 提交答案(假设题目ID为1)
if len(response.json()) > 0:
    challenge_id = response.json()[0]["id"]
    response = requests.post(
        f"{BASE_URL}/challenges/{challenge_id}/submit",
        headers=headers,
        json={"answer": "B"}
    )
    print(f"提交答案: {response.status_code}, 结果: {response.json()}")

# 4. 查看个人资料
response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
print(f"个人资料: {response.status_code}")
profile = response.json()
print(f"已解锁技能: {len(profile.get('skills_matrix', {}))}")

print("\n✓ 集成测试完成!")
```

保存为`test_integration.py`并运行:
```bash
cd backend
pip install requests
python test_integration.py
```

## 常见测试问题

### 1. 后端启动失败
- 检查Python版本: `python --version` (需要3.9+)
- 检查依赖安装: `pip list`
- 查看错误日志

### 2. 前端无法连接后端
- 确认后端运行在5000端口
- 检查vite.config.js的proxy配置
- 查看浏览器控制台Network标签

### 3. Docker容器无法启动
- 检查Docker服务: `docker ps`
- 查看Docker日志: `docker-compose logs`
- Windows用户检查WSL2配置

### 4. 数据库错误
- 删除旧数据库: `rm backend/cyberprism.db`
- 重新初始化: `python backend/app.py`

## 性能测试

使用ab(Apache Bench)测试API性能:

```bash
# 测试登录接口
ab -n 100 -c 10 -p login.json -T application/json http://localhost:5000/api/auth/login
```

其中login.json内容:
```json
{"username":"admin","password":"admin123"}
```

## 成功标志

如果以下测试全部通过,说明系统运行正常:
- ✓ 后端健康检查返回200
- ✓ 用户注册/登录成功
- ✓ 题目列表可正常获取
- ✓ 答案提交后技能解锁
- ✓ 前端能正常访问和显示数据
- ✓ 能力矩阵图正确渲染
- ✓ Docker靶场能成功启动和访问

**祝测试顺利!**
