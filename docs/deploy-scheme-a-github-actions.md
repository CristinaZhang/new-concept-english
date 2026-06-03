# 部署方案 A：GitHub Actions 自动构建

> 流程：`git push → GitHub Actions 构建镜像 → 推 GHCR → K3s 拉取 → kubectl apply`
> 无需在本地或服务器装任何构建工具。

---

## 一、前置准备

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建仓库（网页操作，勾选 README）
# 然后本地关联
cd /Users/dadaozei/Documents/ai_work/projects/new-concept-english
git init
git remote add origin https://github.com/dadaozei/new-concept-english.git
git add .
git commit -m "initial commit"
git branch -M main
git push -u origin main
```

### 2. 创建 GitHub Personal Access Token（用于推送 GHCR）

```
GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
→ Generate new token
→ 勾选: write:packages, read:packages
→ 生成后保存 Token（只显示一次）
```

### 3. 在 GitHub 仓库设置 Secrets

```
仓库 → Settings → Secrets and variables → Actions → New repository secret
```

需要添加 3 个 Secret：

| Secret 名 | 值 | 说明 |
|----------|-----|------|
| `GHCR_USERNAME` | 你的 GitHub 用户名 | 推送镜像的用户名 |
| `GHCR_TOKEN` | 上一步生成的 Token | 推送镜像的密码 |
| `SSH_PRIVATE_KEY` | 你的 SSH 私钥 | 用于 SSH 到 K3s 执行部署 |

> SSH 私钥获取：`cat ~/.ssh/id_ed25519`

---

## 二、Dockerfile 检查

### backend/Dockerfile（已有，需微调）

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/

RUN mkdir -p data

EXPOSE 8000

CMD ["sh", "-c", "python scripts/seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

> ⚠️ 当前镜像里不包含 resources（音频/图片），需要在构建时复制或通过 volume 挂载。
> 见下方方案选择。

### frontend/Dockerfile（已有，无需改动）

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## 三、GitHub Actions 工作流

创建 `.github/workflows/deploy.yml`：

```yaml
name: Build & Deploy to K3s

on:
  push:
    branches: [main]
  workflow_dispatch:  # 允许手动触发

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository_owner }}

jobs:
  # ── 构建并推送后端镜像 ──
  build-backend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.GHCR_USERNAME }}
          password: ${{ secrets.GHCR_TOKEN }}

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/nce-backend:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/nce-backend:latest

  # ── 构建并推送前端镜像 ──
  build-frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.GHCR_USERNAME }}
          password: ${{ secrets.GHCR_TOKEN }}

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/nce-frontend:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/nce-frontend:latest

  # ── 部署到 K3s ──
  deploy:
    needs: [build-backend, build-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to K3s
        uses: appleboy/ssh-action@v1
        with:
          host: 47.96.135.190
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            # 拉取新镜像
            export GHCR_TOKEN="${{ secrets.GHCR_TOKEN }}"
            echo $GHCR_TOKEN | k3s ctr images login \
              --username "${{ secrets.GHCR_USERNAME }}" \
              --password-stdin ghcr.io

            # 如果镜像是公开的，可以跳过 login 直接拉
            kubectl set image deployment/nce-backend \
              backend=ghcr.io/${{ env.IMAGE_PREFIX }}/nce-backend:${{ github.sha }} \
              -n new-concept --record

            kubectl set image deployment/nce-frontend \
              frontend=ghcr.io/${{ env.IMAGE_PREFIX }}/nce-frontend:${{ github.sha }} \
              -n new-concept --record

            # 等待滚动更新完成
            kubectl rollout status deployment/nce-backend -n new-concept --timeout=120s
            kubectl rollout status deployment/nce-frontend -n new-concept --timeout=120s
```

---

## 四、K8s 部署 YAML

创建 `k8s/` 目录：

### k8s/namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: new-concept
```

### k8s/backend.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nce-backend
  namespace: new-concept
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nce-backend
  template:
    metadata:
      labels:
        app: nce-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/dadaozei/nce-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: sqlite:///./data/nce.db
        - name: CORS_ORIGINS
          value: "http://47.96.135.190"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "250m"
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: nce-backend-data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nce-backend-data
  namespace: new-concept
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
  storageClassName: local-path
---
apiVersion: v1
kind: Service
metadata:
  name: nce-backend
  namespace: new-concept
spec:
  selector:
    app: nce-backend
  ports:
  - port: 8000
    targetPort: 8000
```

### k8s/frontend.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nce-frontend
  namespace: new-concept
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nce-frontend
  template:
    metadata:
      labels:
        app: nce-frontend
    spec:
      containers:
      - name: frontend
        image: ghcr.io/dadaozei/nce-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: nce-frontend
  namespace: new-concept
spec:
  type: LoadBalancer   # K3s 的 ServiceLB 自动处理
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: nce-frontend
```

### k8s/apply-all.sh

```bash
#!/bin/bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

---

## 五、首次部署步骤清单

- [ ] GitHub 创建仓库，推送代码
- [ ] 创建 Personal Access Token（write:packages）
- [ ] 添加仓库 Secrets（GHCR_USERNAME / GHCR_TOKEN / SSH_PRIVATE_KEY）
- [ ] 创建 `.github/workflows/deploy.yml`
- [ ] 创建 `k8s/` 目录及 3 个 YAML
- [ ] 首次部署：SSH 到 K3s 执行 `kubectl apply -f k8s/`
- [ ] push 代码触发 Actions，验证自动构建和部署
- [ ] 浏览器访问 `http://47.96.135.190` 确认

---

## 六、注意事项

### 1. 音频/图片资源

当前后端 Dockerfile 没有打包 `resources/` 目录（音频和图片）。有两个方案：

**方案 A：Dockerfile 打包资源（推荐）**

修改 `backend/Dockerfile`：
```dockerfile
COPY resources/ /app/resources/
```

**方案 B：用 PVC 挂载**

把资源放到 PVC，通过 volumeMount 挂载。适合资源经常更新的场景。

### 2. GHCR 镜像拉取

如果镜像设为 `public`，K3s 可以直接拉，不需要 ImagePullSecret。
如果设为 `private`，需要在 K3s 中配置：

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=$GHCR_USERNAME \
  --docker-password=$GHCR_TOKEN \
  -n new-concept
```

然后在 Deployment 中引用：
```yaml
imagePullSecrets:
- name: ghcr-secret
```

### 3. 资源限制

2C2G 服务器：
- backend: 128Mi-256Mi
- frontend: 64Mi-128Mi
- coredns: ~16Mi
- 总计约 500Mi，剩余内存够用
