# 新概念英语学习网站 (New Concept English Learning)

> 面向 8-9 岁孩子的新概念英语第一册自主学习平台

## 技术栈

- **后端**: FastAPI + SQLModel + SQLite
- **前端**: Vue 3 + Vite + vue-router + axios
- **部署**: Docker (docker-compose.yml 待添加)

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 初始化数据库 + 导入种子数据
python scripts/seed_data.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档: http://localhost:8000/docs

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (自动代理 /v1 到后端)
npm run dev
```

访问: http://localhost:5173

## 项目结构

```
new-concept-english/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 入口 + StaticFiles 挂载
│   │   ├── config.py       # pydantic-settings 配置
│   │   ├── db/
│   │   │   ├── database.py # SQLModel 引擎/会话
│   │   │   └── models.py   # 数据模型
│   │   └── routers/        # API 路由
│   │       ├── lessons.py
│   │       ├── vocabulary.py
│   │       ├── grammar.py
│   │       └── progress.py
│   └── scripts/seed_data.py
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── views/          # 页面组件
│       ├── components/     # 通用组件
│       └── api/index.js    # Axios 封装
└── resources/              # 音频/图片资源
```

## API 设计

| 方法   | 路径                                  | 说明         |
| ------ | ------------------------------------- | ------------ |
| GET    | `/v1/lessons`                         | 课文列表     |
| GET    | `/v1/lessons/{id}`                    | 课文详情     |
| GET    | `/v1/lessons/{id}/vocabulary`         | 课文词汇     |
| GET    | `/v1/vocabulary/{id}`                 | 单词详情     |
| GET    | `/v1/lessons/{id}/grammar`            | 课文语法     |
| GET    | `/v1/grammar/{id}`                    | 语法点详情   |
| POST   | `/v1/exercises/{id}/submit`           | 提交练习     |
| GET    | `/v1/progress`                        | 全部进度     |
| POST   | `/v1/progress/lessons/{id}`           | 更新进度     |
| GET    | `/v1/progress/summary`                | 进度汇总     |

## 种子数据

当前 `seed_data.py` 包含 Lesson 1-10 的示例数据：
- 10 篇课文（含原文和翻译）
- Lesson 1 的 7 个生词
- Lesson 1 的 1 个语法点 + 3 道练习

后续可逐步扩充至完整 144 课。
