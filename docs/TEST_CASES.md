# 新概念英语学习网站 — 测试用例

> 覆盖范围：正常流程（Happy Path）
> 创建日期：2026-07-09

---

## 一、测试环境

| 项目 | 说明 |
|------|------|
| **后端** | FastAPI + SQLite，端口 8000 |
| **前端** | Vue 3 + Vite，端口 5173（dev）或 80（prod） |
| **数据** | L1-L20 种子数据 |
| **音频** | `/resources/audio/` 目录 |

---

## 二、API 层测试（后端）

### TC-001: 课文列表

| 步骤 | 预期 |
|------|------|
| `GET /v1/lessons` | 返回 200，items 数组，length = 20 |
| `GET /v1/lessons?limit=10&offset=0` | 返回 10 条 |
| `GET /v1/lessons?level=第一册` | 返回 20 条 |

验证脚本：
```bash
# 课文总数
curl -s http://localhost:8000/v1/lessons | python3 -c "import json,sys; d=json.load(sys.stdin); assert len(d['items'])==20, f'Expected 20, got {len(d[\"items\"])}'" && echo "PASS"

# 单课详情
curl -s http://localhost:8000/v1/lessons/1 | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['lesson_number']==1 and d['title']; print(f'PASS: L1 {d[\"title\"]}')"

# 课文文本内容
curl -s http://localhost:8000/v1/lessons/1 | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('text'), 'L1 text is empty'; print('PASS: text not empty')"
```

### TC-002: 词汇查询

| 步骤 | 预期 |
|------|------|
| `GET /v1/lessons/1/vocabulary` | 返回 200，非空数组 |
| `GET /v1/lessons/3/vocabulary` | 返回 200，非空数组 |
| `GET /v1/vocabulary/1` | 返回单词详情，含 word/phonetic/meaning |

### TC-003: 语法点查询

| 步骤 | 预期 |
|------|------|
| `GET /v1/lessons/1/grammar` | 返回 200，非空数组 |
| `GET /v1/lessons/3/grammar` | 返回 200，非空数组 |
| 语法点含 name/explanation/examples | ✅ |

### TC-004: 练习提交

| 步骤 | 预期 |
|------|------|
| `GET /v1/exercises/1` | 返回练习题，含 type/question/answer |
| `POST /v1/exercises/1/submit {"answer": "正确"}` | 返回 {correct: true/false, correct_answer: ...} |
| `POST /v1/exercises/1/submit {"answer": "错误"}` | 返回 {correct: false, correct_answer: ...} |

### TC-005: 学习进度

| 步骤 | 预期 |
|------|------|
| `POST /v1/progress/lessons/1 {"vocabulary_score": 80, "grammar_score": 90}` | 返回 200 |
| `GET /v1/progress/lessons/1` | 返回刚提交的进度 |
| `GET /v1/progress/summary` | 返回 total_lessons, completed_lessons 等 |

---

## 三、前端页面测试

### TC-010: 首页 — 课文列表

| 步骤 | 预期 |
|------|------|
| 打开 `/lessons` | 页面加载，显示 L1-L20 卡片 |
| 每课显示课号 + 标题 + 类型标签（课文/练习） | ✅ |
| 点击任意课文卡片 | 跳转到 `/lessons/{id}` |

### TC-011: 课文详情页

| 步骤 | 预期 |
|------|------|
| 打开 `/lessons/1` | 加载 L1 详情 |
| 显示课号 L1 + 标题 + "课文"标签 | ✅ |
| 英文课文正常显示 | ✅ |
| 中文翻译可切换显示/隐藏 | ✅ |
| 音频播放器正常渲染 | ✅ |
| 生词列表显示，可点击发音 | ✅ |
| 语法点显示讲解和例句 | ✅ |
| 练习题可作答，提交后即时反馈 | ✅ |

### TC-012: 上一课/下一课导航（已修复）

| 步骤 | 预期 |
|------|------|
| 在 L2 页面，点击"上一课" | URL 变为 `/lessons/1`，内容刷新为 L1 |
| 在 L1 页面，点击"下一课" | URL 变为 `/lessons/2`，内容刷新为 L2 |
| 连续点击"下一课"3 次 | 每次内容都正确刷新 |
| 页面自动滚动到顶部 | ✅ |
| 练习答题状态清空 | ✅ |
| 在 L20 页面点击"下一课" | 正常进入（无限制，或提示已到末尾） |
| 在 L1 页面点击"上一课" | 不触发（lesson_number > 1 才显示按钮） |

### TC-013: 练习作答

| 步骤 | 预期 |
|------|------|
| 选择题点击选项 | 绿色=正确，红色=错误并显示正确答案 |
| 填空题输入正确答案 | ✅ 正确 |
| 填空题输入错误答案 | ❌ 显示正确答案 |
| 全部题目完成后 | 自动保存进度 |
| 已答题不能重复作答 | ✅ 按钮 disabled |

---

## 四、部署验证

### TC-020: 服务健康

| 步骤 | 预期 |
|------|------|
| `curl http://<server>:32627` | 返回 200，HTML 正常 |
| `curl http://<server>:32627/v1/lessons` | 返回 200，20 课数据 |
| `kubectl get pods -n new-concept` | backend 1/1 Running, frontend 1/1 Running |
| 前端构建无报错 | `npm run build` 成功 |

### TC-021: 音频资源

| 步骤 | 预期 |
|------|------|
| `curl -I http://<server>:32627/resources/audio/001\&002.Excuse\ Me.mp3` | 返回 200 或正确文件大小 |

---

## 五、快速验证脚本

```bash
#!/bin/bash
# 快速验证后端 API 正常
# 用法: ./scripts/quick-test.sh http://47.96.135.190:32627

BASE_URL=${1:-http://localhost:8000}
PASS=0
FAIL=0

echo "🧪 快速验证测试..."

# TC-001: 课文列表
echo -n "TC-001 课文列表... "
COUNT=$(curl -s "$BASE_URL/v1/lessons" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['items']))")
if [ "$COUNT" = "20" ]; then echo "✅ PASS (20 lessons)"; PASS=$((PASS+1)); else echo "❌ FAIL (got $COUNT)"; FAIL=$((FAIL+1)); fi

# TC-002: 单课详情
echo -n "TC-002 L1详情... "
TITLE=$(curl -s "$BASE_URL/v1/lessons/1" | python3 -c "import json,sys; print(json.load(sys.stdin)['title'])")
if [ -n "$TITLE" ]; then echo "✅ PASS ($TITLE)"; PASS=$((PASS+1)); else echo "❌ FAIL"; FAIL=$((FAIL+1)); fi

# TC-003: 词汇
echo -n "TC-003 L1词汇... "
VCOUNT=$(curl -s "$BASE_URL/v1/lessons/1/vocabulary" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$VCOUNT" -gt 0 ] 2>/dev/null; then echo "✅ PASS ($VCOUNT words)"; PASS=$((PASS+1)); else echo "❌ FAIL"; FAIL=$((FAIL+1)); fi

# TC-004: 语法
echo -n "TC-004 L1语法... "
GCOUNT=$(curl -s "$BASE_URL/v1/lessons/1/grammar" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$GCOUNT" -gt 0 ] 2>/dev/null; then echo "✅ PASS ($GCOUNT points)"; PASS=$((PASS+1)); else echo "❌ FAIL"; FAIL=$((FAIL+1)); fi

# TC-005: 练习提交
echo -n "TC-005 练习提交... "
RESULT=$(curl -s -X POST "$BASE_URL/v1/exercises/1/submit" -H "Content-Type: application/json" -d '{"answer":"test"}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('correct', 'missing'))")
if [ "$RESULT" = "True" ] || [ "$RESULT" = "False" ]; then echo "✅ PASS"; PASS=$((PASS+1)); else echo "❌ FAIL (got: $RESULT)"; FAIL=$((FAIL+1)); fi

# TC-006: 进度
echo -n "TC-006 进度... "
curl -s "$BASE_URL/v1/progress/summary" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'total_lessons' in d" && echo "✅ PASS" && PASS=$((PASS+1)) || { echo "❌ FAIL"; FAIL=$((FAIL+1)); }

echo ""
echo "结果: $PASS/$((PASS+FAIL)) 通过, $FAIL 失败"
```

---

## 六、未来扩展：异常场景

| 场景 | 预期行为 |
|------|---------|
| 不存在的课号 `/v1/lessons/999` | 404 + 友好提示 |
| 音频文件不存在 | 播放器显示"暂无音频" |
| 网络断开时提交答案 | 提示"网络异常，请重试" |
| 快速连续点击上一课/下一课 | 不卡死，正确加载 |
| 并发提交同一道题 | 不重复计分 |
| 数据库损坏 | 降级显示，不崩溃 |
