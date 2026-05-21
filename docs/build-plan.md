# 新概念英语学习网站 — 搭建计划

> **创建日期**: 2026-05-21
> **目标**: 8-9 岁三年级男孩自主学习新概念英语第一册
> **形式**: Web 网页，Vue 3 + FastAPI + SQLite
> **OpenClaw 角色**: co-builder 执行第一版代码生成
> **关联模式**: 复用 family-reading 项目的 FastAPI + SQLModel + SQLite 架构

---

## 整体架构

```
new-concept-english/
├── backend/                    # FastAPI + SQLModel + SQLite
│   ├── app/
│   │   ├── main.py             # FastAPI 入口，挂载静态资源
│   │   ├── config.py           # Pydantic settings
│   │   ├── db/
│   │   │   ├── database.py     # SQLModel 引擎/会话/初始化
│   │   │   └── models.py       # 数据模型
│   │   ├── routers/
│   │   │   ├── lessons.py      # 课文 CRUD + 音频服务
│   │   │   ├── vocabulary.py   # 词汇 CRUD
│   │   │   ├── grammar.py      # 语法点 + 练习
│   │   │   └── progress.py     # 学习进度
│   │   └── services/
│   │       └── resource_downloader.py  # 网盘资源下载
│   ├── scripts/
│   │   └── seed_data.py        # 种子数据导入
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # Vue 3 + Vite
│   ├── src/
│   │   ├── views/
│   │   │   ├── LessonList.vue
│   │   │   ├── LessonDetail.vue
│   │   │   ├── Vocabulary.vue
│   │   │   ├── SpellingPractice.vue
│   │   │   └── Grammar.vue
│   │   ├── components/
│   │   │   ├── AppHeader.vue
│   │   │   ├── BottomNav.vue
│   │   │   ├── AudioPlayer.vue
│   │   │   ├── LessonCard.vue
│   │   │   ├── Flashcard.vue
│   │   │   └── ScoreDisplay.vue
│   │   ├── api/index.js        # Axios 封装
│   │   ├── router/index.js
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
├── resources/                  # 教材/音频/图片
│   ├── seed/                   # 种子 JSON 数据
│   ├── audio/                  # MP3 音频
│   ├── images/                 # 插图
│   └── download.sh             # 网盘下载脚本
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
└── docker-compose.yml
```

---

## 数据模型

| 模型 | 关键字段 |
|------|---------|
| **Lesson** | id, lesson_number(1-144), title, level, text, translation, image_url, audio_url |
| **Vocabulary** | id, lesson_id(FK), word, phonetic, meaning, example_sentence, audio_url |
| **GrammarPoint** | id, lesson_id(FK), name, explanation(中文), examples(JSON) |
| **Exercise** | id, lesson_id(FK), grammar_point_id(FK), type(fill_blank/mc/error_correction), question, answer, options(JSON) |
| **UserProgress** | id, lesson_id(FK), vocabulary_score, grammar_score, completed_at, review_dates(JSON) |

---

## API 设计

全部 `/v1` 前缀，无鉴权（单用户）。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/v1/lessons?level=第一册&limit=20&offset=0` | 课文列表（分页） |
| GET | `/v1/lessons/{id}` | 课文详情 |
| GET | `/v1/lessons/{id}/vocabulary` | 课文词汇 |
| GET | `/v1/vocabulary/{id}` | 单词详情 |
| GET | `/v1/lessons/{id}/grammar` | 课文语法点 |
| GET | `/v1/grammar/{id}` | 语法点详情 |
| POST | `/v1/exercises/{id}/submit` | 提交练习答案，返回对错 |
| GET | `/v1/progress` | 全部进度 |
| POST | `/v1/progress/lessons/{id}` | 更新进度 |
| GET | `/v1/progress/summary` | 进度汇总 |

静态资源：`/resources/audio/*.mp3`、`/resources/images/*.jpg`

---

## 页面流程

```
[首页/课文列表] ──点击──> [课文详情] ──tab──> [词汇卡片] ──tab──> [语法练习]
                               │                    │                    │
                         音频播放+变速          拼写练习            提交答案+打分
```

---

## OpenClaw 执行提示词

> 以下提示词逐条发送给 OpenClaw，按顺序执行。

### Prompt 1: 初始化项目结构

```
在 /Users/dadaozei/Documents/ai_work/projects/new-concept-english/ 创建项目。

目录结构：
backend/app/{main.py, config.py, db/{database.py, models.py}, routers/{lessons.py, vocabulary.py, grammar.py, progress.py}}
backend/scripts/seed_data.py
backend/requirements.txt
backend/.env.example
frontend/ (Vue 3 + Vite)
resources/{seed/, audio/, images/, download.sh}

后端参考 /Users/dadaozei/Documents/ai_work/projects/family-reading/backend/ 的模式：
- config.py 用 pydantic-settings
- database.py 用 SQLModel 引擎/会话
- main.py 用 create_app 模式 + StaticFiles 挂载 /resources
- 区别：不需要 auth 中间件，不需要微信登录

前端用 Vue 3 + Vite + vue-router + axios。
配置 Vite dev proxy: /v1 -> http://localhost:8000
```

### Prompt 2: 创建数据模型

```
在 backend/app/db/models.py 创建 SQLModel 模型：

Lesson: id, lesson_number(int, unique, 1-144), title, level(str="第一册"), text, translation, image_url, audio_url
Vocabulary: id, lesson_id(int, FK->Lesson), word, phonetic, meaning, example_sentence, audio_url
GrammarPoint: id, lesson_id(int, FK), name, explanation, examples_json(str)
Exercise: id, lesson_id(int, FK), grammar_point_id(int, FK), type(str enum), question, answer, options_json(str, nullable)
UserProgress: id, lesson_id(int, FK), vocabulary_score(float), grammar_score(float), completed_at(datetime, nullable), review_dates_json(str, nullable), created_at, updated_at

参考 family-reading 的 NowMixin 模式处理时间戳。所有 FK 用 SQLModel relationship 模式。
database.py 包含 get_session 依赖和 init_db 函数。
```

### Prompt 3: 创建 API 路由

```
在 backend/app/routers/ 创建四个路由，全部 /v1 前缀：

lessons.py:
- GET /v1/lessons?level=第一册&limit=20&offset=0 -> 分页列表
- GET /v1/lessons/{lesson_id} -> 详情
- Pydantic response models: LessonListItem, LessonDetail

vocabulary.py:
- GET /v1/lessons/{lesson_id}/vocabulary -> 列表
- GET /v1/vocabulary/{vocab_id} -> 详情
- VocabItem response model

grammar.py:
- GET /v1/lessons/{lesson_id}/grammar -> 列表
- GET /v1/grammar/{grammar_id} -> 详情
- POST /v1/exercises/{exercise_id}/submit -> 提交答案，返回 correct/correct_answer/explanation
- GrammarPoint, Exercise, ExerciseSubmitRequest, ExerciseResult models

progress.py:
- GET /v1/progress -> 全部进度
- GET /v1/progress/lessons/{lesson_id} -> 单课进度
- POST /v1/progress/lessons/{lesson_id} -> upsert 进度
- GET /v1/progress/summary -> 汇总（total_lessons, completed_lessons, overall_progress）

所有路由无鉴权，用 get_session 获取数据库会话。
```

### Prompt 4: 种子数据

```
创建 backend/scripts/seed_data.py，从 JSON 文件读取并写入数据库。
创建 resources/seed/ 目录，包含以下文件：

lessons.json: 新概念英语第一册第 1-20 课，每课含 lesson_number, title, text(英文课文), translation(中文翻译), image_url, audio_url
vocabulary.json: 每课 5-8 个单词，含 word, phonetic, meaning, example_sentence
grammar.json: 每课 1-2 个语法点，含 name, explanation(中文), examples(JSON数组)
exercises.json: 每课 2-3 道练习题，含 lesson_id, type(fill_blank/multiple_choice/error_correction), question, answer, options

seed_data.py 运行方式：python scripts/seed_data.py --db sqlite:///data/app.db --seed-dir ../resources/seed
```

### Prompt 5: 前端页面

```
实现以下 Vue 3 页面：

1. LessonList.vue (首页 /):
   - 从 GET /v1/lessons 获取课文列表
   - 彩色卡片网格，显示课号+标题+完成徽章
   - 大字体，适合 8 岁儿童

2. LessonDetail.vue (/lesson/:id):
   - 从 GET /v1/lessons/:id 获取课文详情
   - 英文课文展示，中文翻译可切换显示/隐藏
   - AudioPlayer 组件：播放/暂停 + 变速(0.5x/0.75x/1x)
   - Tab 导航：课文 / 词汇 / 语法

3. Vocabulary.vue (/lesson/:id/vocab):
   - 从 GET /v1/lessons/:id/vocabulary 获取词汇
   - Flashcard 卡片：正面英文+音标，背面中文+例句
   - 点击翻转动画，播放发音按钮

4. SpellingPractice.vue (/lesson/:id/vocab/spelling):
   - 听音频 → 输入单词 → 即时反馈对错
   - 正确=绿色+星星动画，错误=显示正确拼写
   - 完成后 POST 进度到 /v1/progress/lessons/:id

5. Grammar.vue (/lesson/:id/grammar):
   - 从 GET /v1/lessons/:id/grammar 获取语法点
   - 中文解释 + 例句
   - 三种练习组件：填空题 / 四选一 / 改错
   - POST /v1/exercises/:id/submit 提交答案
   - ScoreDisplay 显示得分

AppHeader.vue: 返回按钮 + 课文标题 + 进度环
BottomNav.vue: 底部固定 Tab 栏
AudioPlayer.vue: 复用 HTML5 audio，支持 playbackRate
```

### Prompt 6: Docker 部署

```
创建部署文件：

Dockerfile.backend:
- 基础镜像 python:3.12-slim
- 复制 requirements.txt, pip install
- 复制 app/ 目录
- 创建 data/ 目录
- 挂载 /resources 静态目录
- 启动命令: uvicorn app.main:app --host 0.0.0.0 --port 8000

Dockerfile.frontend:
- 多阶段构建: node:20-alpine 构建 -> nginx:alpine 运行
- nginx 配置: proxy /v1/ -> http://backend:8000/v1/

docker-compose.yml:
- backend: 构建 Dockerfile.backend, ports 8000:8000, volumes data/ 和 resources/
- frontend: 构建 Dockerfile.frontend, ports 80:80, depends_on backend

nginx.conf: 前端静态文件服务 + 反向代理到后端
```

### Prompt 7: 网盘资源下载脚本

```
创建 resources/download.sh 脚本：

功能：从网盘链接下载新概念英语第一册的音频(MP3)和图片(JPG)到 resources/audio/ 和 resources/images/

实现方式：
1. 用户需要手动设置网盘链接为变量 SOURCE_URL
2. 使用 curl/wget 下载
3. 如果是百度网盘，提供手动下载指引
4. 如果是直链，自动批量下载

脚本执行后：
- resources/audio/ 包含 L001.mp3 - L144.mp3
- resources/images/ 包含 lesson_001.jpg - lesson_144.jpg
- resources/seed/ 中的 JSON 引用这些文件路径
```

---

## 验证方式

1. **后端**：`cd backend && uvicorn app.main:app --reload`，浏览器访问 `http://localhost:8000/docs` 确认 API 正常
2. **前端**：`cd frontend && npm run dev`，浏览器访问 `http://localhost:5173` 确认页面渲染
3. **种子数据**：`python scripts/seed_data.py`，确认 20 课数据写入数据库
4. **完整流程**：首页 → 选课文 → 听音频 → 学词汇 → 做语法 → 进度保存

---

## 执行顺序

1. Prompt 1 → 项目结构
2. Prompt 2 → 数据模型
3. Prompt 3 → API 路由
4. Prompt 4 → 种子数据
5. Prompt 5 → 前端页面
6. Prompt 6 → Docker 部署
7. Prompt 7 → 资源下载

每个 Prompt 执行后验证，再进入下一个。
