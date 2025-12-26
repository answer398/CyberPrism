# CyberPrism - CTF能力评估平台

CyberPrism是一个基于CTF题目和选择题的个人渗透测试能力评估平台。通过完成不同类型的安全挑战,用户可以解锁技能标签,平台会生成可视化的能力矩阵图,全面展示用户的PT能力。

## 核心功能

### 1. 用户系统
- 用户注册和登录(JWT认证)
- 个人信息管理(姓名、常用ID、邮箱)
- 双权限系统(管理员/普通用户)
- 技能标签自动解锁机制

### 2. 题目系统
- **选择题**: 测试理论知识
- **靶场题**: Docker容器化的实战环境
  - SQL注入
  - 文件包含漏洞
  - 命令注入
  - 更多类型(可扩展)

### 3. 容器管理
- 用户手动启动容器
- 60分钟自动过期
- 支持延时和手动停止
- 管理员可管理所有用户容器

### 4. 能力评估
- 基于MITRE ATT&CK技能标签体系
- ECharts可视化能力矩阵
- 技能分类:
  - 信息收集与侦察
  - 漏洞利用与攻击
  - 后渗透
  - 防御规避与反侦察

### 5. 管理后台
- 用户管理(查看、修改、删除)
- 题目管理(添加、编辑、删除)
- 容器管理(查看、停止)
- 平台统计信息

## 技术栈

- **前端**: Vue 3 + Element Plus + ECharts + Vue Router
- **后端**: Flask + SQLite + Flask-JWT-Extended
- **容器化**: Docker + Docker Compose
- **数据库**: SQLite

## 快速开始

### 前置要求
- Python 3.9+
- Node.js 16+
- Docker 20.10+
- Docker Compose 2.0+

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端将运行在 `http://localhost:5000`

默认管理员: `admin` / `admin123`

### 2. 启动前端
```bash
cd frontend
npm install
npm run dev
```

前端将运行在 `http://localhost:3000`

### 3. 访问平台
打开浏览器访问: `http://localhost:3000`

## 项目结构

```
CyberPrism/
├── backend/                 # Flask后端
│   ├── app/
│   │   ├── models/         # 数据库模型
│   │   ├── routes/         # API路由
│   │   ├── utils/          # 工具函数
│   │   └── docker_challenges/  # 容器管理
│   ├── app.py             # 应用入口
│   └── requirements.txt
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── api/           # API封装
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   └── main.js
│   ├── vite.config.js
│   └── package.json
├── challenges/             # 靶场题目
│   ├── web-easy/          # SQL注入(简单)
│   ├── web-medium/        # 文件包含(中等)
│   ├── web-hard/          # 命令注入(困难)
│   └── README.md          # 靶场说明
├── docs/                  # 文档
│   ├── DEPLOYMENT.md      # 部署文档
│   └── API.md             # API文档
└── README.md
```

## 文档

- [部署文档](docs/DEPLOYMENT.md) - 详细的部署步骤和配置说明
- [API文档](docs/API.md) - 完整的API接口文档
- [靶场说明](challenges/README.md) - 靶场题目详解和解题思路

## 技能标签体系

平台采用基于MITRE ATT&CK框架的技能标签体系:

```json
{
  "信息收集与侦察": {
    "信息收集": "T1071",
    "网络扫描": "T1046",
    "子域枚举": "T1071",
    "网络拓扑分析": "T1027"
  },
  "漏洞利用与攻击": {
    "利用公共漏洞": "T1203",
    "提权与横向移动": "T1075",
    "社会工程学攻击": "T1071",
    "恶意软件": "T1053"
  },
  "后渗透": {
    "横向移动": "T1021",
    "后门植入": "T1012",
    "权限提升": "T1088"
  },
  "防御规避与反侦察": {
    "权限提升": "T1088",
    "文件/日志清理": "T1070",
    "命令与控制": "T1071"
  }
}
```

用户通过解答题目自动解锁相应技能标签。

## 特色功能

### 能力矩阵可视化
使用ECharts热力图展示用户的技能掌握情况:
- 绿色方块: 已解锁技能
- 灰色方块: 未解锁技能
- 直观展示PT能力全貌

### Docker容器隔离
每个用户的靶场环境完全隔离:
- 独立的Docker容器
- 动态端口映射(30000-40000)
- 环境变量注入FLAG
- 自动资源回收

### 双权限系统
- **普通用户**: 注册、做题、查看个人数据
- **管理员**: 完整的平台管理权限

## 开发参考

### 添加新靶场题

1. 在`challenges/`下创建新目录
2. 编写Dockerfile和docker-compose.yml
3. 通过管理员API添加题目信息
4. 配置技能标签映射

详见[靶场说明](challenges/README.md)

### 添加新技能标签

1. 修改后端`app/routes/challenges.py`中的`SKILL_CODES`字典
2. 更新题目的`skill_tags`字段
3. 前端自动适配新标签

## 安全说明

本平台用于教育目的,包含的漏洞环境仅供学习使用:
- 所有靶场环境均运行在Docker容器中
- 不要将靶场直接暴露到公网
- 定期清理过期容器
- 生产部署时修改默认密码

## 已知限制

1. **前端页面**: 部分页面为简化实现,可根据需求扩展
2. **选择题**: 需要手动通过API添加
3. **Windows Docker**: 路径处理可能需要额外配置

## 后续扩展

- [ ] 添加更多靶场题目类型
- [ ] 实现选择题在线编辑界面
- [ ] 增加用户间的PK功能
- [ ] 导出能力报告PDF
- [ ] 团队协作模式
- [ ] 更详细的解题过程记录

## 致谢

本项目参考了开源CTF平台CTFd的设计理念。

## 许可证

MIT License

---

**开始你的PT能力评估之旅吧!** 🚀
