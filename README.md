# ✨ NovaApp-2API v2.0.0 ✨

<div align="center">

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![Docker Support](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![GitHub Repo stars](https://img.shields.io/github/stars/lzA6/novaapp-2api?style=social)](https://github.com/lzA6/novaapp-2api)

**🚀 一个将 NovaApp.ai 的强大功能无缝转换为兼容 OpenAI API 格式的超级代理！**  
**🎯 让你的所有工具、脚本和应用都能用上 NovaApp 的免费模型，就像拥有了一把通往新世界 AI 大门的万能钥匙！🔑**

</div>

---

## 🎯 核心理念：技术应是赋能，而非束缚

> "我们站在巨人的肩膀上，是为了看得更远，而不是为了成为巨人本身。"

这个项目的诞生，源于一个简单的信念：**分享与便利**。我们希望打破技术壁垒，让每一个热爱 AI 的人，无论你是资深开发者还是刚刚入门的小白，都能轻松、自由地驾驭强大的 AI 模型。

`novaapp-2api` 不仅仅是一堆代码，它是一种精神的体现：
*   **🔍 探索精神**：逆向工程和 API 适配的乐趣，让我们更深入地理解技术的本质
*   **❤️ 开源精神**：我们分享，我们共建，我们一起让这个世界变得更酷
*   **🛠️ 实用主义**：用最直接、最便捷的方式解决实际问题，让 AI 为我所用

我们希望当你读完这篇文档时，不仅能跑通这个项目，更能感受到一种 "原来我也可以" 的自信和喜悦！

---

## ✨ 功能亮点

<div align="center">

| 功能 | 描述 | 状态 |
|------|------|------|
| 🤖 OpenAI 格式兼容 | 完美模拟 `/v1/chat/completions` 和 `/v1/images/generations` 接口 | ✅ 已实现 |
| 🔄 多账号轮询 | 自动轮流使用多个 NovaApp 凭证，提高稳定性 | ✅ 已实现 |
| 🖼️ DALL-E 3 图像生成 | 支持高质量的图像创作，返回 `b64_json` 格式 | ✅ 已实现 |
| 💬 流式聊天响应 | 支持 Server-Sent Events (SSE) 流式输出 | ✅ 已实现 |
| 🐳 Docker 一键部署 | 一条命令即可启动整个服务 | ✅ 已实现 |
| 🎨 自带 Web UI | 内置前端页面，方便测试图像生成 | ✅ 已实现 |
| ⚡ 高性能异步架构 | 基于 FastAPI 和 HTTPX 构建，全异步 I/O | ✅ 已实现 |
| 🛡️ Cloudflare 绕过 | 集成 `cloudscraper` 库，提高请求成功率 | ✅ 已实现 |

</div>

---

## 🏗️ 系统架构总览

<div align="center">

```mermaid
flowchart TD
    A[📱 用户应用] --> B[🌐 Nginx 反向代理<br/>:8088端口]
    B --> C[⚡ FastAPI 应用<br/>:8000端口]
    
    C --> D{🎯 路由分发}
    D --> E[💬 聊天 completions<br/>/v1/chat/completions]
    D --> F[🖼️ 图像生成<br/>/v1/images/generations]
    
    E --> G[🔐 CredentialManager<br/>多账号轮询]
    F --> G
    
    G --> H[🛡️ NovaAppProvider<br/>核心业务逻辑]
    
    H --> I[🌀 Cloudscraper<br/>绕过防火墙]
    I --> J[🚀 NovaApp.ai API]
    
    J --> K[📥 响应处理]
    K --> L[🔄 格式转换<br/>OpenAI → NovaApp]
    
    L --> M[📤 返回结果]
    M --> A
    
    N[🔧 配置中心<br/>.env 文件] --> G
    N --> B
    N --> C
    
    O[🎨 Web UI<br/>静态文件] --> B

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style G fill:#fff3e0
    style H fill:#ffebee
    style I fill:#e0f2f1
    style J fill:#fce4ec
```

</div>

---

## 📁 项目文件结构

```
📦 nova-2api/
├── 🐳 部署文件
│   ├── 📄 .env                    # 环境变量配置文件
│   ├── 📄 Dockerfile              # Python 应用 Docker 构建
│   ├── 📄 docker-compose.yml      # 一键启动编排文件
│   └── 📄 nginx.conf              # Nginx 反向代理配置
├── 🔧 应用核心
│   ├── 📄 main.py                 # FastAPI 应用主入口
│   ├── 📄 requirements.txt        # Python 依赖包列表
│   └── 📂 app/                    # 主应用代码
│       ├── 📂 core/
│       │   ├── 📄 __init__.py
│       │   └── 📄 config.py       # Pydantic 配置模型
│       ├── 📂 providers/
│       │   ├── 📄 __init__.py
│       │   ├── 📄 base_provider.py
│       │   └── 📄 novaapp_provider.py  # 🔥 核心交互逻辑
│       └── 📂 utils/
│           └── 📄 sse_utils.py    # SSE 辅助函数
└── 🎨 前端界面
    └── 📂 static/                 # Web UI 静态文件
        ├── 📄 index.html          # 主页面
        ├── 📄 script.js           # 前端逻辑
        └── 📄 style.css           # 样式文件
```

---

## 🚀 快速开始

### 🎯 一键部署指南 (Docker)

假设你已经安装好了 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

#### 步骤 1: 克隆项目 🏠

```bash
git clone https://github.com/lzA6/novaapp-2api.git
cd novaapp-2api
```

#### 步骤 2: 配置凭证 🎟️

编辑 `.env` 文件，配置你的 NovaApp 凭证：

**如何获取凭证？**
1. 登录 [NovaApp.ai](https://chat.novaapp.ai/)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签页
4. 发送一条消息，找到 `chat` 请求
5. 复制请求头中的 `x_token` 和 `x_user_id`

**`.env` 配置示例：**
```env
# 🔐 安全配置
API_MASTER_KEY=your_super_secret_key_123

# 🌐 部署配置
NGINX_PORT=8088

# 🤖 NovaApp 凭证
# 格式: "x_token|x_user_id"
NOVAAPP_CREDENTIAL_1="你的x_token|你的x_user_id"
NOVAAPP_CREDENTIAL_2="另一个账号的x_token|另一个账号的x_user_id"
```

#### 步骤 3: 启动服务 🚀

```bash
docker-compose up -d --build
```

第一次构建需要几分钟，完成后服务将在后台运行。

#### 步骤 4: 测试验证 ✅

**API 测试：**
```bash
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_super_secret_key_123" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "你好，世界！"}],
    "stream": false
  }'
```

**Web UI 测试：**
访问 `http://localhost:8088/` 使用内置的图像生成测试界面。

---

## 🧠 技术深度解析

### 🏗️ 架构设计理念

`novaapp-2api` 是一个智能的 **"协议转换器"** + **"负载均衡器"**：

*   **🔄 协议转换**：将标准的 OpenAI API 请求转换为 NovaApp 的专有格式
*   **⚖️ 负载均衡**：在多账号间智能轮询，提高服务稳定性
*   **🛡️ 安全防护**：通过 Cloudscraper 绕过防火墙检测

### 📊 技术栈详解

<div align="center">

| 技术组件 | 角色定位 | 核心价值 | 学习曲线 |
|----------|----------|----------|----------|
| **🐳 Docker** | 环境隔离舱 | 解决环境一致性问题，一键部署 | ⭐⭐☆☆☆ |
| **🌐 Nginx** | 金牌门卫 | 反向代理、负载均衡、安全防护 | ⭐⭐☆☆☆ |
| **⚡ FastAPI** | 异步大脑 | 高性能 Web 框架，自动 API 文档 | ⭐⭐☆☆☆ |
| **🛡️ Cloudscraper** | 伪装大师 | 绕过 Cloudflare 等防火墙检测 | ⭐⭐⭐☆☆ |
| **🚀 HTTPX** | 异步信使 | 高性能异步 HTTP 客户端 | ⭐⭐⭐☆☆ |
| **📋 Pydantic** | 配置管家 | 数据验证和配置管理 | ⭐⭐☆☆☆ |
| **📝 Loguru** | 日志艺术家 | 优雅的日志记录和管理 | ⭐☆☆☆☆ |

</div>

### 🔧 核心模块工作原理

#### 🎪 CredentialManager - 智能凭证调度

```mermaid
graph LR
    A[请求到达] --> B[🔒 获取锁]
    B --> C[📊 轮询选择凭证]
    C --> D[🔑 返回当前凭证]
    D --> E[➡️ 指针移动到下一个]
    E --> F[🔓 释放锁]
    F --> G[✅ 返回凭证]
    
    style B fill:#ffebee
    style C fill:#e8f5e8
    style E fill:#e3f2fd
```

**技术特点：**
- 线程安全的轮询算法
- 支持动态凭证管理
- 自动循环，避免单点故障

#### 💬 聊天 completions - 流式传输引擎

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI
    participant N as NovaAppProvider
    participant S as NovaApp Server
    
    C->>F: POST /v1/chat/completions
    F->>N: chat_completion()
    N->>S: 建立流式连接
    Note over N,S: 使用 cloudscraper<br/>绕过防火墙
    
    loop 流式数据传输
        S->>N: data: {...}
        N->>F: yield SSE 数据块
        F->>C: 实时推送
    end
    
    S->>N: [DONE]
    N->>F: 关闭流
    F->>C: 传输完成
```

**技术亮点：**
- 基于 SSE (Server-Sent Events) 的实时流式传输
- 全异步处理，高并发性能优异
- 自动重连和错误处理机制

#### 🎨 图像生成 - 异步任务处理

```mermaid
stateDiagram-v2
    [*] --> 提交任务: generate_image()
    提交任务 --> 等待处理: 获取任务ID
    等待处理 --> 轮询状态: 启动异步轮询
    
    state 轮询状态 {
        [*] --> 查询进度
        查询进度 --> 处理中: 任务未完成
        处理中 --> 查询进度: 等待后重试
        查询进度 --> 生成完成: 任务完成
    }
    
    轮询状态 --> 获取结果: 所有任务完成
    获取结果 --> 下载图片: 获取下载令牌
    下载图片 --> 编码返回: Base64 编码
    编码返回 --> [*]: 返回结果集
```

**技术实现：**
- 两阶段异步处理：提交 + 轮询
- 并发任务管理：`asyncio.gather`
- 自动重试和超时控制

---

## 📈 项目路线图

### ✅ 已完成 (Phase 1: Foundation)
- [x] 核心 API 格式转换
- [x] 聊天和图像生成功能
- [x] Docker 容器化部署
- [x] 多账号轮询机制
- [x] 基础 Web UI

### 🚧 进行中 (Phase 2: Enhancement)
- [ ] 增强错误处理和重试机制
- [ ] 添加更多模型支持
- [ ] 性能优化和监控

### 📅 计划中 (Phase 3: Enterprise)
- [ ] 数据库存储凭证
- [ ] Web 管理后台
- [ ] 使用统计和分析
- [ ] 集群部署支持

---

## ❓ 常见问题解答

<details>
<summary><strong>🔒 这个项目安全吗？我的凭证会泄露吗？</strong></summary>

项目代码完全开源透明，凭证仅用于与 NovaApp 官方 API 通信。只要妥善保管 `.env` 文件并设置强密码的 `API_MASTER_KEY`，你的服务就是安全的。

</details>

<details>
<summary><strong>⚠️ 使用这个项目会被 NovaApp 封号吗？</strong></summary>

**存在一定风险**。这是基于逆向工程的非官方项目，可能违反服务条款。多账号轮询可以分散风险，但请合理使用，避免高频请求。

</details>

<details>
<summary><strong>💼 我可以用于商业项目吗？</strong></summary>

**不推荐**。由于依赖的非官方 API 的不稳定性，不适合用于严肃的商业项目。建议用于学习、研究和个人工具开发。

</details>

<details>
<summary><strong>🐛 遇到问题如何排查？</strong></summary>

1. 检查 Docker 容器状态：`docker-compose ps`
2. 查看应用日志：`docker-compose logs app`
3. 检查 Nginx 日志：`docker-compose logs nginx`
4. 验证 `.env` 配置格式是否正确

</details>

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论你是修复 Bug、添加功能还是改进文档，都是宝贵的贡献。

### 🎯 贡献流程

1. **Fork** 本仓库
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 **Pull Request**

### 📝 开发规范

- 遵循 Python PEP 8 编码规范
- 为新功能添加适当的测试用例
- 更新相关文档
- 确保 Docker 构建正常

---

## 📜 开源协议

本项目采用 **Apache 2.0** 开源协议。详细信息请参阅 [LICENSE](https://opensource.org/licenses/Apache-2.0) 文件。

---

<div align="center">

## 🎊 开始你的 NovaApp 之旅！

**🌟 如果这个项目对你有帮助，请给我们一个 Star！**  
**💝 你的支持是我们持续更新的最大动力！**

[![Star on GitHub](https://img.shields.io/github/stars/lzA6/novaapp-2api?style=for-the-badge&logo=github)](https://github.com/lzA6/novaapp-2api)

**Made with ❤️ by the Open Source Community**

**[https://github.com/lzA6/novaapp-2api](https://github.com/lzA6/novaapp-2api)**

</div>

---

<div align="center">

### 🎯 快速导航

[🚀 快速开始](#-快速开始) • [🏗️ 系统架构](#-系统架构总览) • [🧠 技术解析](#-技术深度解析) • [❓ 常见问题](#-常见问题解答) • [🤝 贡献指南](#-贡献指南)

</div>
