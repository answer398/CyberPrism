# 靶场题目说明

本目录包含三个不同难度的Web安全挑战题目,供CyberPrism平台使用。

## 题目列表

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

## 部署说明

### 添加题目到数据库

管理员需要通过API添加这些题目到数据库:

```json
// 题目1: SQL注入
{
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
}

// 题目2: LFI
{
  "title": "简易博客系统",
  "description": "一个存在本地文件包含漏洞的博客系统,读取系统敏感文件获取FLAG。",
  "category": "漏洞利用与攻击",
  "type": "docker",
  "difficulty": "medium",
  "points": 200,
  "flag": "FLAG{l0c4l_f1l3_1nclus10n_vuln3r4b1l1ty}",
  "docker_compose_file": "D:\\Codes\\CyberPrism\\challenges\\web-medium\\docker-compose.yml",
  "container_port": 80,
  "skill_tags": {
    "信息收集与侦察": "网络扫描",
    "漏洞利用与攻击": "利用公共漏洞"
  }
}

// 题目3: 命令注入
{
  "title": "网络诊断工具",
  "description": "一个带有基本过滤的网络诊断工具,绕过限制执行系统命令获取FLAG。",
  "category": "漏洞利用与攻击",
  "type": "docker",
  "difficulty": "hard",
  "points": 300,
  "flag": "FLAG{c0mm4nd_1nj3ct10n_m4st3r}",
  "docker_compose_file": "D:\\Codes\\CyberPrism\\challenges\\web-hard\\docker-compose.yml",
  "container_port": 5000,
  "skill_tags": {
    "漏洞利用与攻击": "利用公共漏洞",
    "防御规避与反侦察": "命令与控制"
  }
}
```

### 测试题目

在部署前,建议先本地测试每个题目:

```bash
# 测试web-easy
cd challenges/web-easy
docker-compose up -d
# 访问 http://localhost:<端口>

# 测试web-medium
cd challenges/web-medium
docker-compose up -d

# 测试web-hard
cd challenges/web-hard
docker-compose up -d

# 清理
docker-compose down
```

## 注意事项

1. 所有FLAG都通过环境变量注入,确保平台正确设置`FLAG`环境变量
2. 容器端口会动态映射到宿主机的30000-40000范围
3. 容器默认60分钟后自动过期
4. 管理员可以随时停止任何用户的容器
