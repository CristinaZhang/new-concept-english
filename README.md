# 新概念英语学习网站 (New Concept English Learning)

> 面向 8-9 岁孩子的新概念英语第一册自主学习平台

## ✨ 功能

- 📖 **课文浏览** — 中英对照，按"课文+练习"分组展示
- 🎧 **课文音频** — 在线播放
- 📝 **词汇学习** — 闪卡 + 列表，🔊 点击听发音
- ✏️ **拼写练习** — 听发音 → 拼写英文
- 📐 **语法学习** — 中文讲解 + 例句 + 练习
- 📊 **学习进度** — 记录每课完成情况

## 🛠 技术栈

前端 Vue 3 + Vite / 后端 FastAPI + SQLite / 部署 Docker + Nginx

## 🚀 本地运行

```bash
# 后端
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python scripts/seed_data.py
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

## 🐳 Docker

```bash
docker compose up --build -d
```

## 📡 API

`GET /v1/lessons` `GET /v1/lessons/{id}` `GET /v1/lessons/{id}/vocabulary`
`GET /v1/lessons/{id}/grammar` `POST /v1/exercises/{id}/submit`
`GET /v1/progress/summary`

## 📝 数据

L1-L20 课文/词汇/语法/练习，奇数课=课文，偶数课=练习

## 📦 资源

音频来自 [wychl/nce](https://github.com/wychl/nce)
