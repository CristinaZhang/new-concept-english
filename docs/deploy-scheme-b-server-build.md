# 部署方案 B：服务器端构建 + K8s CI/CD

> 流程：`git push 到服务器 → hook 触发 build → 构建镜像 → K3s 部署`
> 探索 K8s 原生 CI/CD（Argo CD / Tekton）。

---

## 一、方案概述

```
git push (到 K3s 服务器上的裸仓库)
  ↓
Git post-receive hook 触发
  ↓
Buildah 构建镜像（tag=commit sha）
  ↓
kubectl apply 部署 YAML
```

**优点**：不依赖外部服务，完全自主控制，适合探索 K8s CI/CD。
**缺点**：2C2G 资源有限，构建时会影响服务运行。

---

## 二、方案 B-1：裸仓库 + Git Hook（轻量级）

### 2.1 在 K3s 服务器上创建裸 Git 仓库

```bash
ssh root@47.96.135.190

# 创建裸仓库
mkdir -p /opt/git/nce.git
cd /opt/git/nce.git
git init --bare

# 创建 post-receive hook
cat > hooks/post-receive << 'EOF'
#!/bin/bash
set -e

REPO_DIR="/opt/git/nce"
BUILD_DIR="/tmp/nce-build"
IMAGE_TAG=$(date +%Y%m%d%H%M%S)

echo "=== 代码更新，开始构建 ==="

# 1. 检出代码
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR
git --work-tree=$BUILD_DIR --git-dir=/opt/git/nce.git checkout -f

cd $BUILD_DIR

# 2. 构建后端镜像（用 buildah）
echo "=== 构建后端镜像 ==="
buildah build -t nce-backend:$IMAGE_TAG -f backend/Dockerfile ./backend

# 3. 构建前端镜像
echo "=== 构建前端镜像 ==="
buildah build -t nce-frontend:$IMAGE_TAG -f frontend/Dockerfile ./frontend

# 4. 导入到 containerd
echo "=== 导入到 containerd ==="
buildah push nce-backend:$IMAGE_TAG containerd:
buildah push nce-frontend:$IMAGE_TAG containerd:

# 5. 更新 K8s 部署
echo "=== 部署到 K8s ==="
kubectl set image deployment/nce-backend \
  backend=nce-backend:$IMAGE_TAG -n new-concept --record

kubectl set image deployment/nce-frontend \
  frontend=nce-frontend:$IMAGE_TAG -n new-concept --record

kubectl rollout status deployment/nce-backend -n new-concept --timeout=120s
kubectl rollout status deployment/nce-frontend -n new-concept --timeout=120s

echo "=== 部署完成 ==="
EOF

chmod +x hooks/post-receive
```

### 2.2 本地添加服务器远程仓库

```bash
cd /Users/dadaozei/Documents/ai_work/projects/new-concept-english

# 添加服务器为远程
git remote add k3s root@47.96.135.190:/opt/git/nce.git

# 推送触发构建
git push k3s main
```

### 2.3 安装 Buildah

```bash
ssh root@47.96.135.190

# Ubuntu 22.04 安装 buildah
apt update
apt install -y buildah

# 验证
buildah version
```

> 注意：buildah 可能需要 `unshare` 权限。如果遇到问题，加 `export BUILDAH_ISOLATION=chroot`。

---

## 三、方案 B-2：K8s 原生 CI/CD（探索方向）

### 选项 1：Argo CD（GitOps）

**原理**：Argo CD 监控 Git 仓库中的 K8s YAML，检测到变更自动 sync 到集群。

```
git push (K8s YAML 变更)
  ↓
Argo CD 检测到 Git 变化
  ↓
自动 kubectl apply
```

**安装**：
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 获取初始密码
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 访问 Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**限制**：Argo CD 只管**部署**，不管**构建镜像**。需要配合其他方案做构建。

### 选项 2：Tekton Pipelines（K8s 原生 CI）

**原理**：在 K8s 内跑 CI Pipeline（类似 GitHub Actions，但在集群内）。

```
git push → Tekton Trigger 监听
  ↓
Pipeline: checkout → build → push image → deploy
```

**安装**：
```bash
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
```

**2C2G 警告**：Tekton 本身占用资源较多（~500Mi），不建议在小服务器上跑。

### 选项 3：KubeVela / Flux

类似 Argo CD 的 GitOps 工具，更轻量。

### 推荐路线

对于 2C2G 服务器：

| 阶段 | 方案 | 说明 |
|------|------|------|
| **现在** | GitHub Actions（方案 A） | 构建在外面，不占服务器资源 |
| **后续** | 裸仓库 + Buildah Hook（方案 B-1） | 轻量级，适合单机项目 |
| **探索** | Argo CD | 只负责部署，构建仍在外部 |
| **不推荐** | Tekton 在 2C2G | 资源太重 |

---

## 四、方案 B 的资源影响评估

| 操作 | 内存峰值 | CPU 峰值 | 影响时间 |
|------|---------|---------|---------|
| Buildah 构建 Python 镜像 | ~400Mi | ~150% | 1-2 分钟 |
| Buildah 构建 Node 镜像 | ~800Mi | ~200% | 2-3 分钟 |
| 服务正常运行 | ~200Mi | ~5% | 持续 |
| **构建期间总计** | **~1000Mi** | **~200%** | **3-5 分钟** |

> 2C2G 总内存 1.6G，构建期间可能 OOM。建议：
> 1. 加 swap：`fallocate -l 2G /swapfile && mkswap /swapfile && swapon /swapfile`
> 2. 或限制构建并发：每次只构建一个镜像

---

## 五、方案对比总结

| 维度 | 方案 A: GitHub Actions | 方案 B-1: 服务器 Hook | 方案 B-2: K8s CI/CD |
|------|----------------------|---------------------|-------------------|
| **构建位置** | GitHub Runner | K3s 服务器 | K3s 集群内 |
| **资源占用** | 零（外部） | 服务器 CPU/内存 | 服务器 CPU/内存 |
| **网络依赖** | 需要 GitHub 通 | 无需外部网络 | 需拉基础镜像 |
| **构建速度** | 快（8C 环境） | 慢（2C2G） | 慢（2C2G） |
| **镜像存储** | GHCR | 本地 containerd | 本地 containerd |
| **部署触发** | SSH 到 K3s | Git Hook 自动 | GitOps 自动 |
| **2C2G 适配** | ✅ 最优 | ⚠️ 需 swap | ⚠️ 需 swap |
| **维护成本** | 低 | 低 | 中 |
| **适合场景** | 个人项目 | 内网/离线环境 | 团队/GitOps |

---

## 六、后续探索路线图

```
Phase 1（现在）
  → GitHub Actions 构建 + SSH 部署
  → 验证前端/后端能正常跑在 K3s 上

Phase 2（1-2 周后）
  → 服务器裸仓库 + Buildah Hook
  → 体验完整的本地 CI/CD 流程

Phase 3（1 个月后）
  → Argo CD GitOps（只负责部署）
  → 配合 GitHub Actions（负责构建）
  → 理解 K8s 原生 CI/CD 生态
```
