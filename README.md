# 录音管理系统

一个用于查询和管理 Verba (VFC) 平台通话录音的 Web 应用。

## 功能特性

- **用户认证** - 安全的登录系统，支持角色权限控制
- **管理员面板** - 管理用户账户（仅管理员）
- **录音查询** - 按时间范围和参与者姓名搜索录音
- **下载播放** - 下载录音或直接在浏览器中播放
- **录音转录** - 支持 ASR 自动转录和 LLM 说话人分离

## 技术栈

- **前端**: Vue.js 3 + Vite
- **后端**: Python FastAPI
- **数据库**: SQLite

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.12+
- ffmpeg（用于音频转录）

### 安装

1. **后端安装**

```bash
cd backend
pip install -r requirements.txt
```

2. **前端安装**

```bash
cd frontend
npm install
```

### 运行应用

1. **启动后端**（在一个终端中）

```bash
cd backend
python main.py
```

API 服务将在 `http://localhost:8000` 可用

2. **启动前端**（在另一个终端中）

```bash
cd frontend
npm run dev
```

应用将在 `http://localhost:3000` 可用

### 默认登录凭证

- **用户名**: `admin`
- **密码**: `admin123`

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/login | 用户登录 |
| POST | /api/logout | 用户登出 |
| GET | /api/me | 获取当前用户 |
| GET | /api/users | 用户列表（仅管理员）|
| POST | /api/users | 创建用户（仅管理员）|
| DELETE | /api/users/{id} | 删除用户（仅管理员）|
| POST | /api/query | 查询本地录音 |
| POST | /api/query/vfc | 查询 VFC 录音 |
| POST | /api/import | 导入录音到本地 |
| GET | /api/download/{ccrd_id} | 下载录音 |
| POST | /api/recordings/{ccrd_id}/transcribe | 转录音频 |
| DELETE | /api/recordings/{ccrd_id} | 删除录音 |

## Verba 集成

系统与 Verba (VFC) Capture 平台集成，用于：
- Verba API 身份验证
- 按时间范围和参与者搜索通话录音
- 下载 MP3 格式的录音文件

## 项目结构

```
recording-management/
├── frontend/               # Vue.js 3 前端
│   ├── src/
│   │   ├── components/    # 可复用组件
│   │   ├── views/        # 页面组件
│   │   ├── composables/  # Vue 组合式函数
│   │   ├── router/       # 路由配置
│   │   ├── assets/       # 静态资源
│   │   ├── main.js       # 应用入口
│   │   └── style.css     # 全局样式
│   └── package.json
├── backend/                # Python FastAPI 后端
│   ├── main.py           # 主应用
│   ├── recordings/       # 下载的录音文件
│   └── recording_management.db  # SQLite 数据库
└── README.md
```
