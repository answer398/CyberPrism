# CyberPrism 项目总结

## 项目概述

**项目名称**: CyberPrism - CTF能力评估平台

**项目目标**: 通过CTF题目和选择题反映个人渗透测试(PT)能力,并生成可视化的技能矩阵图。

**开发周期**: 单次实现

**技术栈**:
- 前端: Vue 3 + Element Plus + ECharts + Vue Router + Vite
- 后端: Flask + SQLite + Flask-JWT-Extended + Docker SDK
- 容器化: Docker + Docker Compose
- 数据库: SQLite

---

## 已实现功能

### ✅ 核心功能

#### 1. 用户系统
- [x] 用户注册(用户名、邮箱、姓名、常用ID)
- [x] 用户登录(JWT认证,24小时有效期)
- [x] 个人信息管理
- [x] 双权限系统(管理员/普通用户)
- [x] 技能标签自动解锁机制

#### 2. 题目系统
- [x] 选择题管理(CRUD)
- [x] 靶场题管理(CRUD)
- [x] 题目分类和难度标记
- [x] 答案提交和验证
- [x] 技能标签关联

#### 3. Docker容器管理
- [x] 用户手动启动容器
- [x] 动态端口映射(30000-40000)
- [x] FLAG环境变量注入
- [x] 60分钟自动过期
- [x] 延时容器(10-60分钟)
- [x] 手动停止容器
- [x] 管理员容器管理
- [x] 过期容器清理

#### 4. 能力评估系统
- [x] MITRE ATT&CK技能标签体系
- [x] 自动解锁技能标签
- [x] ECharts热力图可视化
- [x] 技能矩阵展示
- [x] 个人能力统计

#### 5. 管理员后台
- [x] 用户管理(查看、修改、删除)
- [x] 题目管理(添加、编辑、删除)
- [x] 容器管理(查看、强制停止)
- [x] 平台统计信息
- [x] 批量清理过期容器

#### 6. 靶场样本
- [x] Web-Easy: SQL注入(简单)
- [x] Web-Medium: 本地文件包含(中等)
- [x] Web-Hard: 命令注入(困难)

---

## 技术亮点

### 1. 后端架构
- **模块化设计**: models/routes/utils/docker_challenges分离
- **JWT认证**: 无状态认证,支持跨域
- **装饰器权限控制**: admin_required装饰器实现管理员权限
- **ORM映射**: Flask-SQLAlchemy简化数据库操作
- **Docker SDK集成**: Python docker库管理容器生命周期

### 2. 前端架构
- **Vue 3 Composition API**: 更好的逻辑复用
- **Element Plus**: 完整的UI组件库
- **ECharts集成**: 能力矩阵热力图可视化
- **Vue Router**: 路由守卫实现权限控制
- **Axios封装**: 统一的API请求拦截器

### 3. 容器化方案
- **动态端口映射**: 随机分配30000-40000端口
- **环境变量注入**: FLAG通过环境变量传入容器
- **自动资源回收**: 60分钟超时自动清理
- **容器隔离**: 每个用户独立容器环境

### 4. 安全设计
- **密码哈希**: bcrypt加密存储
- **JWT令牌**: 防止CSRF攻击
- **权限分离**: 管理员和普通用户权限隔离
- **容器沙箱**: Docker隔离靶场环境
- **输入验证**: 后端参数验证

---

## 数据库设计

### 表结构

**users** - 用户表
- id, username, email, password_hash
- display_name, common_id, is_admin
- created_at, updated_at

**challenges** - 题目表
- id, title, description, category, type
- difficulty, points
- question, options, correct_answer (选择题)
- flag, docker_compose_file, container_port (靶场题)
- skill_tags (JSON), is_active

**submissions** - 提交记录表
- id, user_id, challenge_id
- submitted_answer, is_correct
- submitted_at

**user_skill_tags** - 用户技能标签表
- id, user_id, category
- skill_name, skill_code
- unlocked_at

**container_instances** - 容器实例表
- id, user_id, challenge_id
- container_id, container_name, host_port
- status, created_at, expires_at

---

## API设计

### 认证API
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- GET /api/auth/me - 获取当前用户
- PUT /api/auth/me - 更新用户信息

### 题目API
- GET /api/challenges - 获取题目列表
- GET /api/challenges/:id - 获取题目详情
- POST /api/challenges/:id/submit - 提交答案

### 容器API
- POST /api/containers/start/:id - 启动容器
- POST /api/containers/:id/stop - 停止容器
- POST /api/containers/:id/extend - 延长容器
- GET /api/containers/my - 我的容器列表

### 管理员API
- GET /api/admin/users - 用户管理
- POST /api/admin/challenges - 题目管理
- GET /api/admin/containers - 容器管理
- GET /api/admin/stats - 平台统计

---

## 文件结构

```
CyberPrism/
├── backend/
│   ├── app/
│   │   ├── models/__init__.py          (5个模型类)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 (认证路由)
│   │   │   ├── challenges.py           (题目路由)
│   │   │   ├── containers.py           (容器路由)
│   │   │   ├── users.py                (用户路由)
│   │   │   └── admin.py                (管理员路由)
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 (密码哈希)
│   │   │   └── decorators.py           (权限装饰器)
│   │   └── docker_challenges/
│   │       ├── __init__.py
│   │       └── manager.py              (Docker管理器)
│   ├── app.py                          (应用入口)
│   ├── requirements.txt                (依赖清单)
│   └── .env.example                    (环境变量模板)
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── request.js              (Axios封装)
│   │   │   ├── user.js                 (用户API)
│   │   │   ├── challenge.js            (题目API)
│   │   │   ├── container.js            (容器API)
│   │   │   └── admin.js                (管理员API)
│   │   ├── views/
│   │   │   ├── Login.vue               (登录页)
│   │   │   ├── Register.vue            (注册页)
│   │   │   ├── Dashboard.vue           (仪表盘)
│   │   │   ├── Profile.vue             (个人资料+能力矩阵)
│   │   │   ├── Challenges.vue          (题目列表)
│   │   │   ├── Containers.vue          (容器管理)
│   │   │   ├── Leaderboard.vue         (排行榜)
│   │   │   └── admin/                  (管理员页面)
│   │   ├── router/index.js             (路由配置)
│   │   ├── App.vue
│   │   └── main.js
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
├── challenges/
│   ├── web-easy/                       (SQL注入靶场)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── src/
│   ├── web-medium/                     (LFI靶场)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── src/
│   ├── web-hard/                       (命令注入靶场)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── src/
│   └── README.md                       (靶场说明)
├── docs/
│   ├── DEPLOYMENT.md                   (部署文档)
│   ├── API.md                          (API文档)
│   └── TESTING.md                      (测试指南)
└── README.md                           (项目说明)
```

**统计**:
- 后端Python文件: 12个
- 前端Vue组件: 15个
- 靶场题目: 3个
- 文档文件: 5个

---

## 技能标签体系

基于MITRE ATT&CK框架设计,包含4大类,13个技能:

1. **信息收集与侦察**
   - 信息收集 (T1071)
   - 网络扫描 (T1046)
   - 子域枚举 (T1071)
   - 网络拓扑分析 (T1027)

2. **漏洞利用与攻击**
   - 利用公共漏洞 (T1203)
   - 提权与横向移动 (T1075)
   - 社会工程学攻击 (T1071)
   - 恶意软件 (T1053)

3. **后渗透**
   - 横向移动 (T1021)
   - 后门植入 (T1012)
   - 权限提升 (T1088)

4. **防御规避与反侦察**
   - 文件/日志清理 (T1070)
   - 命令与控制 (T1071)

---

## 部署建议

### 开发环境
- Python 3.9+
- Node.js 16+
- Docker Desktop(Windows) / Docker(Linux)
- SQLite Browser(可选,查看数据库)

### 生产环境
- 使用Gunicorn部署Flask
- 使用Nginx作为反向代理
- 配置HTTPS证书
- 定期备份SQLite数据库
- 设置容器资源限制
- 使用PostgreSQL替代SQLite(可选)

---

## 已知限制

1. **前端UI**: 部分管理员页面为简化实现,可扩展完善
2. **选择题管理**: 需通过API添加,无可视化编辑界面
3. **动态FLAG**: 当前为静态FLAG,未实现动态FLAG生成
4. **容器资源限制**: 未设置CPU和内存限制
5. **日志系统**: 缺少系统操作日志
6. **邮件通知**: 未实现邮件通知功能

---

## 扩展方向

### 短期扩展
- [ ] 完善管理员UI界面
- [ ] 在线选择题编辑器
- [ ] 动态FLAG生成系统
- [ ] 容器资源限制配置
- [ ] 系统操作日志

### 中期扩展
- [ ] 更多题目类型(Binary, Crypto, Misc)
- [ ] 团队协作模式
- [ ] 能力报告PDF导出
- [ ] 用户间PK系统
- [ ] 邮件通知系统

### 长期扩展
- [ ] AI辅助出题
- [ ] 自适应难度调整
- [ ] 大数据能力分析
- [ ] 移动端APP
- [ ] 多语言支持

---

## 测试checklist

- [x] 用户注册和登录
- [x] 题目列表获取
- [x] 选择题答案提交
- [x] 技能标签解锁
- [x] 能力矩阵显示
- [x] 容器启动(需Docker)
- [x] 容器延时和停止
- [x] 管理员权限验证
- [x] JWT令牌过期处理
- [ ] 完整集成测试(需手动执行)

---

## 参考资料

- CTFd: https://github.com/CTFd/CTFd
- MITRE ATT&CK: https://attack.mitre.org/
- Flask文档: https://flask.palletsprojects.com/
- Vue 3文档: https://vuejs.org/
- ECharts文档: https://echarts.apache.org/
- Docker SDK: https://docker-py.readthedocs.io/

---

## 总结

CyberPrism项目成功实现了:
1. ✅ 完整的用户认证和权限系统
2. ✅ 选择题和Docker靶场题双轨制
3. ✅ 自动化的技能标签解锁
4. ✅ ECharts可视化能力矩阵
5. ✅ Docker容器动态管理
6. ✅ 管理员后台控制面板
7. ✅ 3个难度递进的靶场样本
8. ✅ 完整的部署和测试文档

项目架构清晰,模块分离,易于扩展。可作为CTF平台的基础框架,继续添加更多题目和功能。

**项目状态**: ✅ MVP完成,可部署使用

---

*文档生成时间: 2024*
