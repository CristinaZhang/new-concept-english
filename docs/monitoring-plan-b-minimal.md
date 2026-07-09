# 监控方案 B：极简自建

> 架构：node_exporter + 后端 /metrics → 本地 Mac Prometheus 抓取 → Grafana 展示
> 资源占用：node_exporter ~10MB，后端 /metrics ~0MB
> 局限：Mac 关机 = 数据丢失

---

## 一、部署 node_exporter

```bash
# 部署到 K3s
kubectl apply -f k8s/node-exporter.yaml

# 验证
kubectl get pods -n new-concept -l app=node-exporter
```

验证 node_exporter 是否可达：
```bash
curl -s http://47.96.135.190:9100/metrics | head -5
# 应该返回 # HELP node_cpu_seconds_total ... 等指标
```

> ⚠️ 需要在阿里云安全组开放 9100 端口。

---

## 二、后端 /metrics 端点

已添加 `prometheus-fastapi-instrumentator`，自动暴露以下指标：

| 指标 | 说明 |
|------|------|
| `http_requests_total` | 请求总数（按 method/path/status 分） |
| `http_request_duration_seconds` | 请求延迟 |
| `http_request_size_bytes` | 请求大小 |
| `http_response_size_bytes` | 响应大小 |

验证：
```bash
curl http://47.96.135.190:32627/v1/health  # 触发一个请求
curl http://47.96.135.190:32627/metrics | grep http_request
```

---

## 三、本地 Prometheus 配置

在你 Mac 上的 `prometheus-mac/config/prometheus.yml` 添加：

```yaml
scrape_configs:
  # 已有的配置...

  # ── NCE 服务器 ──
  - job_name: "nce-system"
    scrape_interval: 30s
    static_configs:
      - targets: ["47.96.135.190:9100"]
        labels:
          instance: "nce-server"

  - job_name: "nce-backend"
    scrape_interval: 30s
    static_configs:
      - targets: ["47.96.135.190:32627"]
        metrics_path: "/metrics"
        labels:
          instance: "nce-backend"
```

重启本地 Prometheus：
```bash
cd /Users/dadaozei/Documents/ai_work/projects/prometheus-mac
./scripts/stop.sh && ./scripts/start.sh
```

---

## 四、Grafana Dashboard

### 推荐导入的 Dashboard

| Dashboard | ID | 说明 |
|-----------|-----|------|
| Node Exporter Full | 1860 | 系统指标全景 |
| FastAPI Application | 17711 | FastAPI 应用指标 |

导入方式：Grafana 网页 → **Dashboards** → **Import** → 输入 ID → 选择 Prometheus 数据源。

---

## 五、安全组配置

需要在阿里云控制台开放以下端口：

| 端口 | 用途 | 授权对象 |
|------|------|---------|
| 32627 | NCE 前端（已有） | 0.0.0.0/0 |
| 9100 | node_exporter | **你的 Mac IP** |

> ⚠️ 9100 端口不要对 0.0.0.0/0 开放，只对你自己的 IP。

---

## 六、升级路径到方案 A

当需要 7×24 监控时，升级到方案 A：

1. 注册 Grafana Cloud 账号
2. 部署 Grafana Alloy（替换 node_exporter）
3. 指标/日志推送到云端
4. 关闭本地 Prometheus

方案 B 的配置（node_exporter + /metrics）在方案 A 中仍然保留，只是数据推送目标变了。
