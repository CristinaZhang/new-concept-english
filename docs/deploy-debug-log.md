# K3s 部署实战：从 0 到网站上线的完整记录

> 日期：2026-06-03
> 环境：阿里云 ECS 2C2G / Ubuntu 22.04 / K3s v1.35.5+k3s1
> 项目：新概念英语学习网站（FastAPI + Vue 3）

---

## 一、目标

将 `new-concept-english` 项目（FastAPI 后端 + Vue 3 前端）部署到 K3s 集群，通过 ECS 公网 IP 访问。

### 为什么选 GitHub Actions 方案

| 考虑 | 原因 |
|------|------|
| 本地无 Docker | Mac 上没装，装 Docker Desktop 太重 |
| 服务器无法构建 | Docker Hub 被墙，ctr 只有运行没有构建 |
| 零维护 | push → 自动构建 → 自动部署 |
| 适合探索 CI/CD | 这是 K8s CI/CD 的第一步实践 |

---

## 二、完整操作步骤

### Step 1：创建 GitHub 仓库

```bash
# 本地已有代码，remote 指向错误的用户
git remote -v
# origin  https://github.com/dadaozei/new-concept-english.git  ← 错了

# 改为用户名为 CristinaZhang
git remote set-url origin git@github.com:CristinaZhang/new-concept-english.git
```

然后在 GitHub 网页上创建仓库 `CristinaZhang/new-concept-english`（不勾选 README）。

### Step 2：统一 Git 身份

本地 commit 的 email 是 `dadaozei@gmail.com` 和 `dadaozei@Biuiu.local`，需要统一改为 `qiaoooo123@163.com`，否则 GitHub 上 commit 不会关联到账号。

```bash
# 1. 改本地配置
git config --global user.email "qiaoooo123@163.com"
git config user.name "CristinaZhang"

# 2. rewrite 所有历史
git filter-branch --env-filter '
OLD_EMAIL1="dadaozei@gmail.com"
OLD_EMAIL2="dadaozei@Biuiu.local"
CORRECT_NAME="CristinaZhang"
CORRECT_EMAIL="qiaoooo123@163.com"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL1" ] || [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL2" ]; then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL1" ] || [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL2" ]; then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags

# 3. 清理旧引用
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now

# 4. force push
git push --force origin master
```

**踩坑**：后台任务 (`run_in_background: true`) 里 SSH agent 无法弹出认证提示，force push 会静默失败。需要前台执行。

### Step 3：调整 Dockerfile

**问题**：后端 Dockerfile 的构建上下文是 `./backend/`，但需要访问项目根目录的 `resources/`（音频/图片）。

**解决**：把后端 Dockerfile 的构建上下文改为项目根目录，同时调整 COPY 路径。

**修改前** `backend/Dockerfile`：
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY scripts/ ./scripts/
```

**修改后**（构建上下文改为 `.` 项目根目录）：
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY resources/ ./resources/    # ← 新增：打包音频/图片
RUN mkdir -p data
EXPOSE 8000
CMD ["sh", "-c", "python scripts/seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

对应地，GitHub Actions 里后端的 `context` 从 `./backend` 改为 `.`：

```yaml
- name: Build and push backend
  uses: docker/build-push-action@v6
  with:
    context: .                    # ← 项目根目录
    file: ./backend/Dockerfile    # ← 指定 Dockerfile 位置
```

### Step 4：调整前端 nginx.conf

**问题**：Docker Compose 环境下 `proxy_pass http://backend:8000` 用 Docker 网络名，K8s 里不生效。

**修改前**：
```nginx
location /v1/ {
    proxy_pass http://backend:8000;
}
```

**修改后**（用 K8s Service DNS）：
```nginx
location /v1/ {
    proxy_pass http://nce-backend.new-concept.svc.cluster.local:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Step 5：创建 .dockerignore

**踩坑 1**：第一次写的 `.dockerignore` 排除了 `frontend/` 和 `resources/`，导致构建时找不到这些目录。

```
# ❌ 错误写法
frontend/    ← 前端构建需要这个！
resources/   ← 后端需要这个！
```

**踩坑 2**：正确的写法是只排除不需要的：

```dockerignore
# Python build artifacts
.venv/
__pycache__/
*.pyc

# Local env files
.env
local.env

# Docs / configs (not needed in Docker)
docs/
k8s/
.github/

# Dev scripts
resources/download_audio_*.py
```

### Step 6：创建 GitHub Actions 工作流

创建 `.github/workflows/deploy.yml`。经历了多次迭代：

**v1（失败）**：没有 `docker/setup-buildx-action`，build 步骤直接失败。

**v2（失败）**：用了错误的镜像名（`IMAGE_PREFIX: CristinaZhang` 大写，GHCR 要求全小写）。

**v3（失败）**：`.dockerignore` 排除了 `frontend/` 和 `resources/`。

**v4（失败）**：GHCR 镜像是私有的，K3s 没有认证无法拉取。

**v5（成功）**：
- 加了 `docker/setup-buildx-action`
- `IMAGE_PREFIX` 改为小写 `cristinazhang`
- 修正 `.dockerignore`
- 加了 `imagePullSecrets` 和自动创建 Secret

最终版本的关键部分：
```yaml
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: ./backend/Dockerfile
          push: true
          tags: ghcr.io/cristinazhang/nce-backend:${{ github.sha }}
      - uses: docker/build-push-action@v6
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: ghcr.io/cristinazhang/nce-frontend:${{ github.sha }}
      - uses: appleboy/ssh-action@v1
        with:
          host: 47.96.135.190
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            # 创建 ImagePullSecret
            kubectl create secret docker-registry ghcr-secret \
              --docker-server=ghcr.io \
              --docker-username=CristinaZhang \
              --docker-password="${{ secrets.GHCR_PAT }}" \
              -n new-concept --dry-run=client -o yaml | kubectl apply -f -
            # 部署 backend + frontend
            kubectl apply -f - <<EOF
            apiVersion: apps/v1
            kind: Deployment
            ...
            EOF
```

### Step 7：配置 GitHub Secrets

仓库 → Settings → Secrets and variables → Actions：

| Secret | 值 | 作用 |
|--------|-----|------|
| `SSH_PRIVATE_KEY` | `cat ~/.ssh/id_ed25519` | GitHub Actions SSH 到 K3s 服务器 |
| `GHCR_PAT` | GitHub Personal Access Token（read:packages） | K3s 拉取 GHCR 私有镜像 |

### Step 8：首次部署

```bash
# 手动创建 namespace 和 deployment（因为 workflow 的 kubectl set image 需要已有 deployment）
ssh root@47.96.135.190
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

然后 push 代码触发 workflow，后续每次 push 自动部署。

---

## 三、遇到的问题与 Debug

### 问题 1：Git 身份不对，commit 不关联 GitHub 账号

**症状**：GitHub 上 commit 显示为 `dadaozei@gmail.com`，不关联 CristinaZhang 账号。

**原因**：本地 `git config user.email` 是旧邮箱。

**解决**：用 `git filter-branch --env-filter` rewrite 所有 commit 的 author/committer email，然后 force push。

### 问题 2：force push 在后台任务中失败

**症状**：`run_in_background: true` 的 force push 没反应，退出码 128。

**原因**：后台模式下 SSH agent 无法弹出认证提示，git 的 SSH 交互被阻塞。

**解决**：前台执行 `git push --force`。

### 问题 3：Docker build 失败（无错误信息）

**症状**：GitHub Actions 的 build 步骤直接失败，但看不到具体错误。

**原因**：`docker/build-push-action` 需要先 `docker/setup-buildx-action`。没有 setup buildx 时 action 会静默失败。

**解决**：在每个 build job 前加 `docker/setup-buildx-action@v3`。

### 问题 4：GHCR 镜像名大写

**症状**：build 失败。

**原因**：GHCR 要求镜像名全小写。`IMAGE_PREFIX: CristinaZhang` 导致 URL 无效。

**解决**：`IMAGE_PREFIX: cristinazhang`（全小写）。

### 问题 5：.dockerignore 排除了需要的目录

**症状**：build 时找不到 `frontend/` 或 `resources/`。

**原因**：`.dockerignore` 里写了 `frontend/` 和 `resources/`，Docker 构建时忽略这些目录。

**解决**：只排除不需要的（.venv/__pycache__/docs/k8s/.github/等）。

### 问题 6：GHCR 私有镜像拉取失败（ImagePullBackOff）

**症状**：Pod 状态 `ImagePullBackOff`，events 显示 `failed to resolve reference "ghcr.io/...": not found`。

**原因**：GHCR 默认创建的包是**私有的**，K3s 没有认证无法拉取。401 被容器运行时转为 404（安全考虑，不暴露资源是否存在）。

**解决**：创建 ImagePullSecret：
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=CristinaZhang \
  --docker-password=<PAT> \
  -n new-concept
```
然后在 Deployment 中引用：
```yaml
imagePullSecrets:
- name: ghcr-secret
```

### 问题 7：kubectl set image 需要已有 deployment

**症状**：deploy 步骤的 `kubectl set image` 报错，因为 deployment 还不存在。

**解决**：首次手动 `kubectl apply` 创建 deployment，后续 workflow 用 `kubectl apply`（会自动 update 现有资源）。

---

## 四、当前状态

### 已完成 ✅

| 项目 | 状态 |
|------|------|
| GitHub 仓库创建 | ✅ |
| Git 身份统一 | ✅ |
| GitHub Actions workflow | ✅ 构建成功 |
| GHCR 镜像推送 | ✅ backend + frontend 都成功 |
| GitHub Secrets 配置 | ✅ SSH_PRIVATE_KEY + GHCR_PAT |
| ImagePullSecret 创建 | ✅ |
| K8s Deployment 创建 | ✅ |
| 前端 Pod 运行 | ✅ 1/1 Running |
| 前端页面可访问 | ✅ 通过 NodePort 32627 |

### 进行中 ⏳

| 项目 | 状态 | 阻塞原因 |
|------|------|---------|
| 公网 IP:80 直接访问 | ❌ | LoadBalancer EXTERNAL-IP pending，需要确认阿里云安全组 80 端口 |
| 公网 NodePort 32627 访问 | ❌ | 阿里云安全组需放行 32627 端口 |

### 已解决 ✅

| 项目 | 状态 |
|------|------|
| 后端 Pod 启动 | ✅ 1/1 Running，镜像拉取完成（约 15 分钟） |
| 前端 Pod 启动 | ✅ 1/1 Running |
| 前端 HTML 返回 | ✅ HTTP 200 |
| 后端 API | ✅ `/v1/lessons` 返回 20 课数据 |
| 后端 Health | ✅ `/health` 返回 `{"status":"ok"}` |
| Nginx 反向代理 | ✅ `/v1/` → backend 正常 |
| 内部 DNS | ✅ `nce-backend.new-concept.svc.cluster.local` 解析正常 |
| 旧 ReplicaSets 清理 | ✅ 已清理 6 个旧 RS |

---

## 五、当前 K8s 资源

```
Namespace: new-concept

Deployments:
  nce-backend   image: ghcr.io/cristinazhang/nce-backend:<sha>
  nce-frontend  image: ghcr.io/cristinazhang/nce-frontend:<sha>

Services:
  nce-backend   ClusterIP   10.43.143.217:8000
  nce-frontend  LoadBalancer  10.43.123.204:80 → NodePort 32627

PVC:
  nce-backend-data  1Gi (local-path)

Secret:
  ghcr-secret  (GHCR 认证)
```

### 访问方式

| 方式 | 地址 | 状态 |
|------|------|------|
| NodePort | `http://47.96.135.190:32627` | ✅ 前端已可访问 |
| 公网 IP:80 | `http://47.96.135.190` | ❌ 安全组需放行 |
| ClusterIP（节点内） | `http://10.43.123.204` | ✅ 可访问 |

---

## 七、部署成功状态（2026-06-03 更新）

### 服务全部正常

| 端点 | 结果 |
|------|------|
| `http://localhost:32627` | ✅ 返回前端 HTML |
| `http://localhost:32627/v1/lessons` | ✅ 返回 20 课 JSON 数据 |
| `http://localhost:32627/health` | ✅ 返回 SPA 页面（nginx try_files 兜底） |

### 内部验证

| 测试 | 结果 |
|------|------|
| 前端 Pod 内 `wget /v1/lessons` | ✅ 20 课数据 |
| 后端 Health `/health` | ✅ `{"status":"ok"}` |
| 内部 DNS `nce-backend.new-concept.svc.cluster.local:8000` | ✅ 解析正常 |
| Nginx 反向代理 `/v1/` → backend | ✅ 正常工作 |

### 待完成

1. **阿里云安全组放行 32627 端口** → 公网通过 NodePort 访问
2. **阿里云安全组放行 80 端口** → 公网直接访问（需确认 ServiceLB 行为）
3. **后续 push 自动部署** → GitHub Actions 已配置，push 即触发

---

## 六、后续待解决（历史）

1. ~~后端 Pod 是否正常启动~~ — ✅ 已解决
2. ~~阿里云安全组放行 80 端口~~ — 待确认
3. ~~排查前端页面是否正常加载~~ — ✅ 已解决
4. ~~后端 API 联调~~ — ✅ 已解决
5. GHCR 镜像设为 Public — 可选，省去 ImagePullSecret
6. ~~清理旧的失败 Pod~~ — ✅ 已清理 6 个旧 ReplicaSets
