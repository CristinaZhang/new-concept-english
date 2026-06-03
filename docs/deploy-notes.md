# K3s 部署笔记

> 环境：阿里云 ECS 2C2G / Ubuntu 22.04 / K3s v1.35.5+k3s1
> 安装时禁用了 Traefik：`--disable=traefik`
> 
> **部署方案**：
> - 方案 A：[GitHub Actions 自动构建](deploy-scheme-a-github-actions.md) ← 推荐先用这个
> - 方案 B：[服务器端构建 + K8s CI/CD](deploy-scheme-b-server-build.md) ← 后续探索

---

## 服务暴露方案：ServiceLB (LoadBalancer)

### 为什么不用 Traefik

K3s 安装时 `--disable=traefik`，且当前场景是**单 ECS 公网 IP + 单 FastAPI 服务**，不需要 Ingress Controller。

K3s 自带 **ServiceLB**（klipper-lb），通过 iptables 把节点端口流量转发到 Pod，无需额外安装组件。

### 方案对比

| 方案 | 访问方式 | 优点 | 缺点 |
|------|---------|------|------|
| **LoadBalancer**（推荐） | `http://<公网IP>:80` | K3s 自带，端口干净 | 单服务占 80 端口 |
| NodePort | `http://<公网IP>:30080` | 简单 | 端口号不友好，需开安全组 |
| Traefik + Ingress | `http://<公网IP>/api` | 多服务按路径路由 | 需安装额外组件 |
| HostNetwork | `http://<公网IP>:8000` | 零配置 | 端口冲突风险 |

### 部署配置

**FastAPI Service（LoadBalancer）**：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-svc
  namespace: new-concept
spec:
  type: LoadBalancer
  ports:
  - port: 80          # 外部访问端口
    targetPort: 8000  # Pod 内 FastAPI 端口
    protocol: TCP
  selector:
    app: fastapi
```

**FastAPI Deployment（参考）**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi
  namespace: new-concept
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: new-concept-english-backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "250m"
```

### 访问

```bash
# 部署后直接访问 ECS 公网 IP
curl http://<ECS公网IP>/docs

# 查看 Service 状态
kubectl get svc fastapi-svc -n new-concept
# 会看到 EXTERNAL-IP 显示为节点 IP（即本机 IP）
```

### 阿里云安全组

需要放行对应的端口：

- **LoadBalancer 方案**：放行 TCP 80（源 IP 可设为 0.0.0.0/0）
- **NodePort 方案**：放行 TCP 30000-32767

---

## 后续扩展：什么时候需要装 Traefik

| 场景 | 是否需要 Traefik |
|------|----------------|
| 单服务 + ECS 公网 IP 直连 | ❌ ServiceLB 够用 |
| 域名绑定 + HTTPS | ✅ 需要 Ingress Controller |
| 多服务按路径路由（/api, /docs, /admin） | ✅ Traefik 中间件方便 |
| 2C2G 资源紧张 | ❌ 省一个 Pod 资源 |

**装回 Traefik 的命令**：

```bash
# Helm 安装
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik -n kube-system

# 或重新安装 K3s（去掉 --disable=traefik）
curl -sfL https://get.k3s.io | INSTALL_K3S_MIRROR=cn sh -s -
```

---

## 排障

### Service 没有 EXTERNAL-IP

```bash
kubectl describe svc fastapi-svc -n new-concept
# 看 Events 有没有报错
```

### Pod 不通

```bash
# 检查 Pod 状态
kubectl get pods -n new-concept

# 看 Pod 日志
kubectl logs -n new-concept -l app=fastapi

# 从 Pod 内测试
kubectl exec -n new-concept -l app=fastapi -- curl localhost:8000/docs
```

### 安全组确认

```bash
# 在 ECS 上确认端口监听
ss -tlnp | grep :80
```
