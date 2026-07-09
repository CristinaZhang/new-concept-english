#!/bin/bash
# 批量创建 GitHub Issues
# 需要 GitHub CLI: brew install gh && gh auth login

set -e

REPO=${1:-"CristinaZhang/new-concept-english"}

echo "📋 在 $REPO 创建 Issues..."

# Issue 1: GHCR PAT 过期
echo "Creating: GHCR PAT 过期..."
gh issue create --repo "$REPO" \
  --title "🔴 GHCR PAT 过期，无法部署新镜像" \
  --label "bug,deployment" \
  --body "**问题**: K3s 拉取新镜像返回 403 Forbidden，ImagePullSecret 中 PAT 过期。

**影响**: 代码已 push（commit 20eba50），新镜像无法部署，网站仍运行旧版本。

**修复**:
1. GitHub → Settings → Developer settings → Personal access tokens
2. 确认/重生成 PAT（需 \`read:packages\` 权限）
3. 更新 secret: \`kubectl create secret docker-registry ghcr-secret --docker-server=ghcr.io --docker-username=CristinaZhang --docker-password=<新PAT> -n new-concept --dry-run=client -o yaml | kubectl apply -f -\`
4. 触发重新部署" 2>/dev/null || echo "  (可能已存在)"

# Issue 2: 偶数课数据为空
echo "Creating: 偶数课数据为空..."
gh issue create --repo "$REPO" \
  --title "🟡 偶数课（练习课）词汇/语法/练习数据为空" \
  --label "bug,data" \
  --body "**问题**: L4/L2 等偶数课返回 \`vocabulary: []\`, \`grammar: []\`, \`exercises: []\`。

**原因**: 种子数据只填充了奇数课的词汇/语法/练习。

**影响**: 偶数课页面显示为空，无学习内容。" 2>/dev/null || echo "  (可能已存在)"

# Issue 3: 扩课
echo "Creating: 扩课 L20 → L40+..."
gh issue create --repo "$REPO" \
  --title "📚 扩课 L20 → L40+" \
  --label "enhancement,data" \
  --body "目前只有 L1-L20，需要扩展到更多课文。需准备：课文数据、词汇、语法点、练习题、音频资源。" 2>/dev/null || echo "  (可能已存在)"

# Issue 4: 错题本
echo "Creating: 错题本功能..."
gh issue create --repo "$REPO" \
  --title "📝 错题本功能" \
  --label "enhancement" \
  --body "记录做错的题目，支持按课程分类浏览、重做、清除已掌握的题目。" 2>/dev/null || echo "  (可能已存在)"

# Issue 5: 打卡
echo "Creating: 连续学习打卡..."
gh issue create --repo "$REPO" \
  --title "🔥 连续学习打卡" \
  --label "enhancement" \
  --body "每天完成至少 1 课即算打卡，显示连续天数，里程碑奖励动画。" 2>/dev/null || echo "  (可能已存在)"

echo ""
echo "✅ 完成！查看: https://github.com/$REPO/issues"
