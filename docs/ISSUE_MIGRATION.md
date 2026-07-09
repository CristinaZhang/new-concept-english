# GitHub Issues 迁移指南

> 将 docs/ISSUES.md 中的条目迁移到 GitHub Issues

---

## 批量创建 Issues 脚本

```bash
#!/bin/bash
# 用法: ./scripts/create-issues.sh OWNER/REPO
# 需要安装 GitHub CLI: brew install gh
# 需要先登录: gh auth login

REPO=${1:-"CristinaZhang/new-concept-english"}

echo "📋 在 $REPO 创建 Issues..."

# Issue #3: GHCR PAT 过期
gh issue create --repo "$REPO" \
  --title "🔴 GHCR PAT 过期，无法部署新镜像" \
  --label "bug,deployment" \
  --body "## 问题描述
K3s 集群拉取新镜像时返回 \`403 Forbidden\`，旧的 ImagePullSecret 中的 PAT 已过期。

## 影响
- 代码已 push 到 master（commit \`20eba50\`）
- 构建了新镜像但无法部署
- 网站仍运行旧版本（无 prev/next fix）

## 修复步骤
1. 去 GitHub → Settings → Developer settings → Personal access tokens
2. 确认或重新生成 PAT（需要 \`read:packages\` 权限）
3. 更新 K3s secret:
   \`\`\`bash
   kubectl create secret docker-registry ghcr-secret \\
     --docker-server=ghcr.io \\
     --docker-username=CristinaZhang \\
     --docker-password=<新PAT> \\
     -n new-concept \\
     --dry-run=client -o yaml | kubectl apply -f -
   \`\`\`
4. 触发重新部署"

# Issue #4: 偶数课数据为空
gh issue create --repo "$REPO" \
  --title "🟡 偶数课（练习课）词汇/语法/练习数据为空" \
  --label "bug,data" \
  --body "## 问题描述
偶数课（如 L2/L4）返回空数据：
- \`/v1/lessons/4/vocabulary\` → \`[]\`
- \`/v1/lessons/4/grammar\` → \`[]\`
- \`/v1/exercises/4\` → \`[]\`

## 原因
种子数据只填充了奇数课的词汇/语法，偶数课只有基本信息。

## 影响
偶数课页面显示为空，无学习内容。"

# 功能需求: 扩课
gh issue create --repo "$REPO" \
  --title "📚 扩课 L20 → L40+" \
  --label "enhancement,data" \
  --body "## 需求
目前只有 L1-L20（20课），需要扩展到 L40 或更多。

## 工作内容
1. 准备课文数据（英文 + 中文翻译）
2. 准备词汇数据（每课 5-8 词）
3. 准备语法点（每课 1-2 个）
4. 准备练习题（每课 2-3 题）
5. 准备音频资源
6. 更新 seed 脚本

## 数据来源
- 音频: github.com/wychl/nce
- 课文/词汇: 需要从教材录入"

# 功能需求: 错题本
gh issue create --repo "$REPO" \
  --title "📝 错题本功能" \
  --label "enhancement" \
  --body "## 需求
记录孩子做错的题目，方便复习。

## 功能设计
- 每道错题记录：题目、正确答案、用户答案、所属课程
- 错题本页面：按课程分类浏览
- 重做功能：可以重新做错题
- 清除功能：掌握的题可以移除"

# 功能需求: 打卡
gh issue create --repo "$REPO" \
  --title "🔥 连续学习打卡" \
  --label "enhancement" \
  --body "## 需求
激励孩子坚持学习，显示连续学习天数。

## 功能设计
- 每天完成至少 1 课即算打卡
- 显示连续天数 🔥3 / 🔥7 / 🔥30
- 里程碑奖励动画"

echo "✅ Issues 创建完成"
```

---

## GitHub Issues 使用方式

### 查看 Issues
- 浏览器：`https://github.com/CristinaZhang/new-concept-english/issues`
- CLI：`gh issue list`

### 创建 Issue
```bash
# 使用模板（交互式）
gh issue create

# 直接创建
gh issue create --title "标题" --body "内容" --label "bug"
```

### 更新状态
```bash
# 关闭
gh issue close 1 --reason completed

# 重新打开
gh issue reopen 1

# 添加标签
gh issue edit 1 --add-label "enhancement"
```

### 评论
```bash
gh issue comment 1 --body "已修复，待部署"
```

---

## Issue 标签约定

| 标签 | 用途 |
|------|------|
| `bug` | 功能缺陷 |
| `enhancement` | 新功能/改进 |
| `deployment` | 部署/运维相关 |
| `data` | 数据相关（课文/词汇/音频） |
| `frontend` | 前端问题 |
| `backend` | 后端问题 |
| `good first issue` | 适合入门的简单任务 |
| `wontfix` | 不打算修复 |
