# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

# Windows下设置UTF-8输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 50)
print("CyberPrism 快速测试脚本")
print("=" * 50)

BASE_URL = "http://localhost:5000/api"

# 1. 测试健康检查
print("\n[1/5] 测试健康检查...")
try:
    res = requests.get("http://localhost:5000/health")
    if res.status_code == 200:
        print("✓ 健康检查通过")
    else:
        print(f"✗ 健康检查失败: {res.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ 无法连接到后端: {e}")
    print("请确保后端正在运行: python backend/run.py")
    exit(1)

# 2. 测试管理员登录
print("\n[2/5] 测试管理员登录...")
try:
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if res.status_code == 200:
        token = res.json()["access_token"]
        print("✓ 管理员登录成功")
        print(f"  Token: {token[:20]}...")
    else:
        print(f"✗ 登录失败: {res.text}")
        exit(1)
except Exception as e:
    print(f"✗ 登录出错: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 3. 添加测试题目
print("\n[3/5] 添加测试选择题...")
challenge = {
    "title": "SQL注入基础知识",
    "description": "测试对SQL注入的基础理解",
    "category": "信息收集与侦察",
    "type": "choice",
    "difficulty": "easy",
    "points": 50,
    "question": "以下哪个是最常见的SQL注入payload?",
    "options": {
        "A": "SELECT * FROM users",
        "B": "admin' OR '1'='1",
        "C": "DROP TABLE users",
        "D": "UPDATE users SET password"
    },
    "correct_answer": "B",
    "skill_tags": {
        "信息收集与侦察": "信息收集"
    }
}

try:
    res = requests.post(f"{BASE_URL}/admin/challenges", headers=headers, json=challenge)
    if res.status_code == 201:
        challenge_id = res.json()["challenge"]["id"]
        print(f"✓ 题目添加成功 (ID: {challenge_id})")
    else:
        print(f"✗ 题目添加失败: {res.text}")
except Exception as e:
    print(f"✗ 添加题目出错: {e}")

# 4. 注册测试用户
print("\n[4/5] 注册测试用户...")
try:
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "testuser",
        "email": "test@cyberprism.com",
        "password": "test123",
        "display_name": "测试用户",
        "common_id": "test001"
    })
    if res.status_code == 201:
        user_token = res.json()["access_token"]
        print("✓ 用户注册成功")
    else:
        # 可能已存在
        print("  用户可能已存在,尝试登录...")
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "testuser",
            "password": "test123"
        })
        user_token = res.json()["access_token"]
        print("✓ 用户登录成功")
except Exception as e:
    print(f"✗ 用户注册/登录出错: {e}")
    user_token = None

# 5. 提交答案测试
if user_token and 'challenge_id' in locals():
    print("\n[5/5] 测试提交答案...")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    try:
        res = requests.post(
            f"{BASE_URL}/challenges/{challenge_id}/submit",
            headers=user_headers,
            json={"answer": "B"}
        )
        if res.status_code == 200:
            result = res.json()
            if result["is_correct"]:
                print(f"✓ 答案正确! 获得{result['points']}分")
            else:
                print("✗ 答案错误")
        else:
            print(f"  提交状态: {res.status_code}")
    except Exception as e:
        print(f"✗ 提交答案出错: {e}")
else:
    print("\n[5/5] 跳过答案提交测试")
    user_headers = None

# 6. 查看用户资料
if user_token and user_headers:
    print("\n[6/6] 查看用户技能解锁...")
    try:
        res = requests.get(f"{BASE_URL}/users/profile", headers=user_headers)
        if res.status_code == 200:
            profile = res.json()
            skills_count = sum(len(skills) for skills in profile.get("skills_matrix", {}).values())
            print(f"✓ 已解锁技能数: {skills_count}")
            if skills_count > 0:
                print("  已解锁技能:")
                for category, skills in profile.get("skills_matrix", {}).items():
                    for skill in skills:
                        print(f"    - {category}: {skill['skill_name']}")
    except Exception as e:
        print(f"✗ 获取用户资料出错: {e}")

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
print("\n下一步:")
print("1. 启动前端: cd frontend && npm install && npm run dev")
print("2. 访问: http://localhost:3000")
print("3. 使用 testuser/test123 登录")
print("4. 查看个人资料页面的能力矩阵图")
print("\n管理员账户: admin/admin123")
