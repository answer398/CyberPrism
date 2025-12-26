# CyberPrism API文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **认证方式**: JWT Bearer Token
- **Content-Type**: `application/json`

## 认证相关

### 用户注册
```
POST /auth/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "display_name": "string",
  "common_id": "string (可选)"
}
```

**响应**:
```json
{
  "message": "注册成功",
  "access_token": "jwt_token_string",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "display_name": "用户一",
    "common_id": "user1",
    "is_admin": false
  }
}
```

### 用户登录
```
POST /auth/login
```

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**: 同注册

### 获取当前用户信息
```
GET /auth/me
Headers: Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "display_name": "用户一",
  "is_admin": false,
  "skill_tags": [...]
}
```

## 题目相关

### 获取题目列表
```
GET /challenges?type=docker&category=漏洞利用&difficulty=easy
Headers: Authorization: Bearer <token>
```

**查询参数**:
- `type`: choice | docker (可选)
- `category`: 题目分类 (可选)
- `difficulty`: easy | medium | hard (可选)

**响应**:
```json
[
  {
    "id": 1,
    "title": "简单登录系统",
    "description": "SQL注入漏洞",
    "category": "漏洞利用与攻击",
    "type": "docker",
    "difficulty": "easy",
    "points": 100,
    "solved": false,
    "container_port": 80
  }
]
```

### 提交答案
```
POST /challenges/<id>/submit
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "answer": "FLAG{...}" // 或选择题答案 "A", "B" etc
}
```

**响应**:
```json
{
  "is_correct": true,
  "message": "恭喜!答案正确!",
  "points": 100
}
```

## 容器相关

### 启动容器
```
POST /containers/start/<challenge_id>
Headers: Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "容器启动成功",
  "container": {
    "id": 1,
    "challenge_id": 1,
    "container_id": "docker_container_id",
    "host_port": 35678,
    "status": "running",
    "expires_at": "2024-01-01T12:00:00"
  }
}
```

### 停止容器
```
POST /containers/<instance_id>/stop
Headers: Authorization: Bearer <token>
```

### 延长容器时间
```
POST /containers/<instance_id>/extend
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "minutes": 30
}
```

## 管理员API

### 获取所有用户
```
GET /admin/users
Headers: Authorization: Bearer <admin_token>
```

### 添加题目
```
POST /admin/challenges
Headers: Authorization: Bearer <admin_token>
```

**请求体**:
```json
{
  "title": "题目标题",
  "description": "题目描述",
  "category": "分类",
  "type": "docker",
  "difficulty": "easy",
  "points": 100,
  "flag": "FLAG{...}",
  "docker_compose_file": "绝对路径",
  "container_port": 80,
  "skill_tags": {
    "分类名": "技能名"
  }
}
```

### 获取平台统计
```
GET /admin/stats
Headers: Authorization: Bearer <admin_token>
```

**响应**:
```json
{
  "total_users": 10,
  "total_challenges": 5,
  "total_submissions": 50,
  "correct_submissions": 30,
  "running_containers": 3,
  "success_rate": 60.0
}
```

## 错误码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证或token过期
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器错误
