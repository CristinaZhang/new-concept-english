# 监控方案 A：Grafana Cloud

> 架构：服务器跑 Grafana Alloy（~50MB） → 指标/日志推送到 Grafana Cloud 免费版
> 适合：2C2G 小服务器，数据存云端，手机/网页随时看

---

## 一、注册 Grafana Cloud

1. 访问 [grafana.com](https://grafana.com/) → **Get started for free**
2. 选择 Free 计划（无需信用卡）
3. 登录后进入 [Grafana Cloud Portal](https://grafana.com/orgs/your-org)

### 免费额度

| 项目 | 额度 | 说明 |
|------|------|------|
| 指标 | 10k 活跃系列 | 够用，一个 Pod 约 50-200 系列 |
| 日志 | 50GB/月 | 2 个服务的日志远远够用 |
| Traces | 50GB/月 | 暂不需要 |
| Alerting | 5 个通知渠道 | 邮件/钉钉/企业微信等 |
| Dashboard | 不限 | 网页/手机随时查看 |

### 获取凭证

1. 进入 Cloud Portal → **Stacks** → 你的 stack
2. 点击 **Details** → **Prometheus** → 记下：
   - **Remote Write URL**：`https://prometheus-prod-xx-prod-us-east-0.grafana.net/api/prom/push`
   - **Username**：你的 instance ID（数字）
3. 点击 **Security** → **API Keys** → **Create API Key**
   - 权限选：`MetricsPublisher` + `LogsWriter`
   - 保存生成的 Key（只显示一次）
4. 同样记下 **Loki URL**：`https://logs-prod-us-central1.grafana.net/loki/api/v1/push`

---

## 二、Alloy 配置

### Alloy ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alloy-config
  namespace: new-concept
data:
  config.alloy: |
    // ── 系统指标采集 ──
    discovery.kubernetes "nodes" {
      role = "node"
    }

    discovery.kubernetes "pods" {
      role = "pod"
      namespaces {
        names = ["new-concept"]
      }
    }

    // ── 系统指标（通过 node_exporter） ──
    prometheus.exporter.unix "local" {}

    prometheus.scrape "unix" {
      targets    = prometheus.exporter.unix.local.targets
      forward_to = [prometheus.remote_write.grafana.receiver]
    }

    // ── 后端应用指标 ──
    prometheus.scrape "nce_backend" {
      targets = [
        {"__address__" = "nce-backend:8000", "instance" = "nce-backend"},
      ]
      forward_to = [prometheus.remote_write.grafana.receiver]
    }

    // ── 前端指标 ──
    prometheus.scrape "nce_frontend" {
      targets = [
        {"__address__" = "nce-frontend:80", "instance" = "nce-frontend"},
      ]
      forward_to = [prometheus.remote_write.grafana.receiver]
    }

    // ── 推送指标到 Grafana Cloud ──
    prometheus.remote_write "grafana" {
      endpoint {
        url      = "https://prometheus-prod-xx-prod-us-east-0.grafana.net/api/prom/push"
        basic_auth {
          username = "<instance-id>"
          password = "<api-key>"
        }
      }
    }

    // ── 日志采集 ──
    local.file_match "varlog" {
      path_targets = [{
        __address__  = "localhost",
        __path__     = "/var/log/pods/*/*/*.log",
        service_name = "k3s",
      }]
    }

    loki.source.file "varlog" {
      targets    = local.file_match.varlog.targets
      forward_to = [loki.write.grafana.receiver]
    }

    // ── 推送日志到 Grafana Cloud ──
    loki.write "grafana" {
      endpoint {
        url = "https://logs-prod-us-central1.grafana.net/loki/api/v1/push"
        basic_auth {
          username = "<instance-id>"
          password = "<api-key>"
        }
      }
    }
```

---

## 三、K8s 部署 YAML

### Alloy DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: grafana-alloy
  namespace: new-concept
  labels:
    app: grafana-alloy
spec:
  selector:
    matchLabels:
      app: grafana-alloy
  template:
    metadata:
      labels:
        app: grafana-alloy
    spec:
      serviceAccountName: alloy
      containers:
      - name: alloy
        image: grafana/alloy:latest
        args:
        - "run"
        - "/etc/alloy/config.alloy"
        - "--server.http.listen-addr=0.0.0.0:12345"
        - "--storage.path=/tmp/alloy"
        ports:
        - containerPort: 12345
          name: http
        volumeMounts:
        - name: config
          mountPath: /etc/alloy
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: pods
          mountPath: /var/log/pods
          readOnly: true
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "100m"
      volumes:
      - name: config
        configMap:
          name: alloy-config
      - name: varlog
        hostPath:
          path: /var/log
      - name: pods
        hostPath:
          path: /var/log/pods
```

### RBAC（让 Alloy 能发现 K8s Pod）

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: alloy
  namespace: new-concept
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: alloy
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/proxy", "services", "endpoints", "pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["discovery.k8s.io"]
  resources: ["endpointslices"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: alloy
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: alloy
subjects:
- kind: ServiceAccount
  name: alloy
  namespace: new-concept
```

---

## 四、后端应用添加 /metrics 端点

在 FastAPI 中暴露 Prometheus 指标（只需 5 行代码）：

```python
# backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 添加这行（挂载后）
Instrumentator().instrument(app).expose(app)
```

需要加依赖：
```
# backend/requirements.txt
prometheus-fastapi-instrumentator>=6.1.0
```

### 暴露的指标

| 指标 | 说明 |
|------|------|
| `http_requests_total` | 请求总数（按 method/path/status 分） |
| `http_request_duration_seconds` | 请求延迟分布 |
| `http_request_size_bytes` | 请求大小 |
| `http_response_size_bytes` | 响应大小 |

---

## 五、部署步骤

1. **注册 Grafana Cloud**，拿到 URL + API Key
2. **修改 Alloy ConfigMap**，填入你的凭证
3. **更新后端代码**，添加 `prometheus-fastapi-instrumentator`
4. **部署**：
   ```bash
   kubectl apply -f k8s/alloy-rbac.yaml
   kubectl apply -f k8s/alloy-configmap.yaml
   kubectl apply -f k8s/alloy-daemonset.yaml
   ```
5. **验证**：
   ```bash
   kubectl logs -n new-concept -l app=grafana-alloy
   ```

---

## 六、Dashboard 配置

登录 Grafana Cloud 网页，导入现成 Dashboard：

| Dashboard | ID | 说明 |
|-----------|-----|------|
| Node Exporter | 1860 | 系统指标（CPU/内存/磁盘/网络） |
| Kubernetes Cluster | 6417 | K8s 集群概览 |
| FastAPI | 17711 | FastAPI 应用指标 |

导入方式：Grafana 网页 → **Dashboards** → **Import** → 输入 ID → 选择 Prometheus 数据源。

---

## 七、告警配置

Grafana Cloud → **Alerting** → **Contact points** → 添加通知渠道。

### 推荐告警规则

| 规则 | 条件 | 严重度 |
|------|------|--------|
| Pod 异常重启 | `kube_pod_container_status_restarts_total > 3` | 警告 |
| 内存使用过高 | `container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9` | 严重 |
| 后端请求错误率高 | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1` | 严重 |
| 磁盘空间不足 | `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1` | 警告 |
| 后端无响应 | `probe_success{job="nce-backend"} == 0` | 严重 |

---

## 八、总资源占用

| 组件 | 内存 | CPU |
|------|------|-----|
| Grafana Alloy | ~50MB | ~0.05核 |
| **额外占用** | **~50MB** | **~0.05核** |

服务器总内存 1608MB，占用后约 824MB，剩余约 784MB，仍然充裕。
