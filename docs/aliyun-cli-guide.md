# 阿里云 CLI 安装与使用

> 用途：通过命令行管理阿里云资源（ECS、安全组等）
> 文档日期：2026-07-09

---

## 一、安装

### macOS

```bash
brew install aliyun-cli
```

### 验证

```bash
aliyun version
```

---

## 二、配置 AccessKey

### 获取 AccessKey

1. 登录 [RAM 控制台](https://ram.console.aliyun.com/)
2. 左侧菜单 → **身份管理** → **用户** → **创建用户**
3. 勾选 **「OpenAPI 调用访问」**（程序化访问）
4. 创建后**立即保存** AccessKey ID 和 AccessKey Secret（只显示一次）
5. 给用户授权 `AliyunECSFullAccess` 策略（或最小权限 `AliyunECSReadOnlyAccess` + 自定义安全组策略）

> ⚠️ 主账号 AccessKey 风险极高，建议用 RAM 子账号。

### 配置 CLI

```bash
aliyun configure
```

依次输入：
- `Access Key ID`: `your-access-key-id`
- `Access Key Secret`: `your-access-key-secret`
- `Default Region Id`: `cn-shanghai`（你的实例区域，可能是 `cn-hangzhou` 或 `cn-beijing`）
- `Default Language`: `zh`

配置保存在 `~/.aliyun/config.json`。

### 查看配置

```bash
aliyun configure list
```

---

## 三、常用命令

### 查看 ECS 实例

```bash
# 列出所有实例
aliyun ecs DescribeInstances --RegionId cn-shanghai

# 按实例 ID 查
aliyun ecs DescribeInstances --RegionId cn-shanghai --InstanceIds '["i-xxx"]'
```

### 查看安全组规则

```bash
# 先查实例属于哪个安全组
aliyun ecs DescribeInstances --RegionId cn-shanghai --InstanceIds '["i-xxx"]'

# 查安全组规则
aliyun ecs DescribeSecurityGroupAttribute --RegionId cn-shanghai --SecurityGroupId sg-xxx
```

### 添加入站规则（开放端口）

```bash
# 开放 TCP 32627 端口
aliyun ecs AuthorizeSecurityGroup \
  --RegionId cn-shanghai \
  --SecurityGroupId sg-xxx \
  --IpProtocol tcp \
  --PortRange 32627/32627 \
  --SourceCidrIp 0.0.0.0/0 \
  --Policy accept \
  --Priority 1 \
  --Description "NCE学习网站前端"
```

### 删除入站规则

```bash
aliyun ecs RevokeSecurityGroup \
  --RegionId cn-shanghai \
  --SecurityGroupId sg-xxx \
  --IpProtocol tcp \
  --PortRange 32627/32627 \
  --SourceCidrIp 0.0.0.0/0
```

---

## 四、快捷脚本：开放 NCE 端口

把以下内容存为 `scripts/open-nce-port.sh`：

```bash
#!/bin/bash
# 一键开放 NCE 学习网站端口

REGION="cn-shanghai"  # 改成你的实例区域
SG_ID="sg-xxx"        # 改成你的安全组 ID

echo "🔓 开放 TCP 32627 端口..."
aliyun ecs AuthorizeSecurityGroup \
  --RegionId "$REGION" \
  --SecurityGroupId "$SG_ID" \
  --IpProtocol tcp \
  --PortRange 32627/32627 \
  --SourceCidrIp 0.0.0.0/0 \
  --Policy accept \
  --Priority 1 \
  --Description "NCE学习网站前端(NodePort)"

if [ $? -eq 0 ]; then
  echo "✅ 规则已添加，端口 32627 已开放"
  echo "🌐 访问地址: http://47.96.135.190:32627"
else
  echo "❌ 添加失败，请检查 RegionId 和 SecurityGroupId"
fi
```

```bash
chmod +x scripts/open-nce-port.sh
./scripts/open-nce-port.sh
```

---

## 五、验证端口是否生效

```bash
# 从本地 Mac 测试
curl -v http://47.96.135.190:32627 --connect-timeout 5

# 或用 telnet
telnet 47.96.135.190 32627
```

看到 HTML 内容返回即为成功。

---

## 六、Region 对照

| 区域 | RegionId |
|------|----------|
| 华东1（杭州） | cn-hangzhou |
| 华东2（上海） | cn-shanghai |
| 华北2（北京） | cn-beijing |
| 华北1（青岛） | cn-qingdao |
| 华南1（深圳） | cn-shenzhen |

不确定自己的实例在哪个区域，可以：

```bash
aliyun ecs DescribeInstances | grep -E "RegionId|InstanceId|PrivateIpAddress"
```
