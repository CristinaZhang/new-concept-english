# 多用户功能

> 创建日期：2026-07-09
> 目的：支持多人共享学习网站，每人独立学习进度

---

## 使用方式

### 分享链接给不同用户

```
小明: http://47.96.135.190:32627/?user=abc123
小红: http://47.96.135.190:32627/?user=def456
小华: http://47.96.135.190:32627/?user=ghi789
```

### 用户首次访问
1. 打开链接 → `user` 参数存入 localStorage
2. 页面顶部显示当前用户名
3. 所有练习进度按 user_id 独立记录

### 后续访问
- 直接访问 `http://47.96.135.190:32627/`（无参数）→ 自动使用上次身份
- 点击头部用户徽章 → 切换用户

### 创建新用户
1. 点击头部用户徽章
2. 在"新用户"输入框中输入 ID（如 `kid006`）
3. 点击"创建"
4. 分享带 `?user=kid006` 的链接

---

## 默认用户

种子数据预设了 5 个用户：

| user_id | 名字 |
|---------|------|
| kid001 | 小明 |
| kid002 | 小红 |
| kid003 | 小华 |
| kid004 | 小强 |
| kid005 | 小丽 |

---

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/v1/users` | 获取所有用户列表 |
| POST | `/v1/users` | 创建新用户 `{"user_id": "abc123", "name": "测试"}` |
| GET | `/v1/progress?user_id=abc123` | 获取指定用户进度 |
| GET | `/v1/progress/summary?user_id=abc123` | 获取指定用户进度汇总 |
| POST | `/v1/progress/lessons/{id}?user_id=abc123` | 更新指定用户进度 |

---

## 技术实现

- **前端**：`frontend/src/utils/user.js` — URL 参数 + localStorage 身份管理
- **后端**：`backend/app/db/models.py` — `User` + `UserProgress.user_id`
- **数据库**：SQLite，`user_progress` 表增加 `user_id` 字段，`(user_id, lesson_id)` 联合唯一
