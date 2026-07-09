# CI/CD 构建与部署流程

> 最后更新：2026-07-09
> 架构：GitHub Actions → GHCR → K3s（47.96.135.190）

---

## 一、流程概览

```
git push → GitHub Actions
    │
    ├─ job 1: test-backend
    │      ├─ pip install + seed data
    │      ├─ 启动 FastAPI
    │      └─ 6 个 API 测试（课文/词汇/语法/练习/进度）
    │
    ├─ job 2: test-frontend
    │      ├─ npm install
    │      └─ npm run build（验证构建成功）
    │
    └─ job 3: build-and-deploy（前两步通过才执行）
           ├─ build backend image → push to GHCR
           ├─ build frontend image → push to GHCR
           └─ SSH to K3s → kubectl apply → rollout
```

**关键设计**：测试失败 → 不 build → 不部署。

---

## 二、Workflow 文件

`.github/workflows/deploy.yml`

### 触发条件

| 触发方式 | 说明 |
|---------|------|
| `push` to `master` | 代码推送自动触发 |
| `workflow_dispatch` | 手动触发（GitHub Actions 页面） |

###  Secrets 依赖

| Secret | 用途 | 设置位置 |
|--------|------|---------|
| `GITHUB_TOKEN` | 推送镜像到 GHCR（自动提供） | 无需设置 |
| `GHCR_PAT` | K3s 拉取私有镜像 | Settings → Secrets → Actions |
| `SSH_PRIVATE_KEY` | SSH 到 K3s 执行 kubectl | Settings → Secrets → Actions |

---

## 三、各 Job 详解

### Job 1: test-backend

| 步骤 | 说明 |
|------|------|
| 安装依赖 | `pip install -r requirements.txt` |
| Seed 数据 | `python scripts/seed_data.py` |
| 启动服务 | `uvicorn app.main:app --port 8000 &` |
| 等待就绪 | 轮询 `/docs` 直到服务启动 |
| 运行测试 | 6 个 API 测试，任一失败即终止 |

**测试用例**：

| # | 测试 | 验证 |
|---|------|------|
| TC-001 | 课文列表 | 返回 20 课 |
| TC-002 | 单课详情 | L1 标题非空 |
| TC-003 | 词汇查询 | L1 词汇 > 0 |
| TC-004 | 语法查询 | L1 语法点 > 0 |
| TC-005 | 练习提交 | 返回 correct 字段 |
| TC-006 | 进度查询 | 返回 total_lessons |

### Job 2: test-frontend

| 步骤 | 说明 |
|------|------|
| Node.js 20 | actions/setup-node@v4 |
| 安装依赖 | `npm install` |
| 构建 | `npm run build` |
| 验证 | 检查 `dist/index.html` 存在 |

### Job 3: build-and-deploy

**依赖**：`needs: [test-backend, test-frontend]`

| 步骤 | 说明 |
|------|------|
| Docker Buildx | 设置构建器 |
| GHCR 登录 | 用 `GITHUB_TOKEN` |
| Build 后端 | 镜像名：`ghcr.io/cristinazhang/nce-backend:<commit-sha>` |
| Build 前端 | 镜像名：`ghcr.io/cristinazhang/nce-frontend:<commit-sha>` |
| SSH 部署 | appleboy/ssh-action 执行 kubectl |

**部署脚本**（在 K3s 上执行）：
```bash
# 1. 创建 namespace（如不存在）
kubectl create namespace new-concept --dry-run=client -o yaml | kubectl apply -f -

# 2. 更新 ImagePullSecret（解决 PAT 过期问题）
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=CristinaZhang \
  --docker-password="${{ secrets.GHCR_PAT }}" \
  -n new-concept --dry-run=client -o yaml | kubectl apply -f -

# 3. 应用 Backend Deployment
kubectl apply -f - <<EOF
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
      imagePullSecrets:
      - name: ghcr-secret
      containers:
      - name: backend
        image: ghcr.io/cristinazhang/nce-backend:<commit-sha>
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
EOF

# 4. 应用 Frontend Deployment（同上）

# 5. 应用 PVC

# 6. 等待滚动更新
kubectl rollout status deployment/nce-backend -n new-concept --timeout=120s
kubectl rollout status deployment/nce-frontend -n new-concept --timeout=120s
```

---

## 四、Docker 镜像

| 镜像 | Dockerfile | 基础镜像 | 端口 |
|------|-----------|---------|------|
| nce-backend | `backend/Dockerfile` | python:3.12-slim | 8000 |
| nce-frontend | `frontend/Dockerfile` | node:20-alpine → nginx:alpine | 80 |

### 镜像命名

```
ghcr.io/cristinazhang/nce-backend:<commit-sha>
ghcr.io/cristinazhang/nce-frontend:<commit-sha>
```

每次部署用 commit SHA 做 tag，保证唯一性和可追溯性。

---

## 五、K8s 清单文件（独立维护）

`k8s/` 目录是部署 YAML 的唯一来源，deploy.yml 通过 `sed` 替换镜像 tag 后 apply。

| 文件 | 内容 |
|------|------|
| `k8s/namespace.yaml` | namespace 定义 |
| `k8s/backend.yaml` | Backend Deployment + PVC + Service |
| `k8s/frontend.yaml` | Frontend Deployment + Service |

### 镜像占位符

YAML 文件中用占位符代替具体版本：
```yaml
# k8s/backend.yaml
image: __BACKEND_IMAGE__

# k8s/frontend.yaml  
image: __FRONTEND_IMAGE__
```

deploy.yml 在 apply 前用 `sed` 替换：
```bash
sed "s|__BACKEND_IMAGE__|$BACKEND_IMG|g; s|__FRONTEND_IMAGE__|$FRONTEND_IMG|g" k8s/backend.yaml | kubectl apply -f -
```

> ⚠️ 修改 K8s 配置只需改 `k8s/` 下的 YAML，**不需要**改 `deploy.yml`。

---

## 六、K3s 部署状态

| 资源 | 名称 | 类型 | 说明 |
|------|------|------|------|
| Namespace | new-concept | - | 隔离部署 |
| Deployment | nce-backend | 1 replica | 后端 API |
| Deployment | nce-frontend | 1 replica | 前端 Nginx |
| Service | nce-backend | ClusterIP | 仅集群内访问 |
| Service | nce-frontend | LoadBalancer | NodePort 32627 |
| PVC | nce-backend-data | 1Gi | 数据库持久化 |
| Secret | ghcr-secret | docker-registry | GHCR 拉取凭证 |

**外部访问**：`http://47.96.135.190:32627`

---

## 六、日常操作

### 触发部署

```bash
# 方式 1: push 代码
git add . && git commit -m "fix: ..." && git push origin master

# 方式 2: 手动触发（GitHub Actions 页面）
# https://github.com/CristinaZhang/new-concept-english/actions
```

### 检查状态

```bash
# 查看部署
ssh root@47.96.135.190 'kubectl get all -n new-concept'

# 查看日志
ssh root@47.96.135.190 'kubectl logs -n new-concept nce-backend-xxx'

# 回滚到上一版本
ssh root@47.96.135.190 'kubectl rollout undo deployment/nce-frontend -n new-concept'
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| ImagePullBackOff 403 | GHCR PAT 过期 | 重生成 PAT → 更新 ghcr-secret → 重新部署 |
| 部署成功但前端 404 | Nginx 配置问题 | 检查 `frontend/nginx.conf` |
| 后端 500 | 数据库/代码错误 | `kubectl logs` 查看后端日志 |
| 音频 404 | resources 未挂载 | 确认 Dockerfile COPY resources 或 volume 挂载 |

---

## 七、架构待改进

| 项目 | 当前状态 | 目标 |
|------|---------|------|
| 前端测试 | 仅 build 验证 | 加入 Vue 组件单元测试 |
| 后端测试 | Shell 脚本 API 测试 | 迁移到 pytest |
| 音频资源 | 404（未解决） | Dockerfile 打包或 volume 挂载 |
| 域名访问 | IP:端口 | Ingress + 域名 |
| HTTPS | 无 | Let's Encrypt 证书 |
| 监控 | 无 | 健康检查 + 告警 |
