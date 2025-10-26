# 📋 配置指南

## 📝 两个配置文件的作用

### 1. `.env` 文件 - 敏感信息配置

**位置**：项目根目录 `/Users/cog/Desktop/💼工作文件/projects/arxiv_robot/.env`

**用途**：存储个人敏感信息
- 邮箱密码
- API密钥
- 个人邮箱地址

**特点**：
- ⚠️ 不提交到Git（已添加到.gitignore）
- 🔒 每个用户不同
- 📧 包含敏感信息

**创建方式**：
```bash
cp env_example.txt .env
```

**配置示例**：
```bash
# 邮件配置
EMAIL_HOST=smtp.163.com
EMAIL_PORT=465
EMAIL_USER=your_email@163.com
EMAIL_PASSWORD=your_password

# 收件人邮箱（支持多个，用逗号分隔）
RECIPIENT_EMAIL=email1@163.com,email2@qq.com,email3@gmail.com

# AI API配置（可选）
OPENAI_API_KEY=your_api_key
USE_AI_SUMMARY=true
```

**163邮箱配置步骤**：
1. 登录163邮箱
2. 设置 → POP3/SMTP/IMAP
3. 开启"SMTP服务"
4. 生成"客户端授权密码"
5. 使用授权密码（不是登录密码）

### 2. `configs/config.py` - 应用配置

**位置**：`configs/config.py`

**用途**：存储应用逻辑配置
- 关键词列表
- arXiv类别
- 爬取参数

**特点**：
- ✅ 可以提交到Git
- 🤝 团队成员共享
- 🔧 非敏感信息

**配置示例**：
```python
# arXiv类别
ARXIV_CATEGORIES = ["cs.AI", "cs.CV", "cs.LG", "cs.CL", "cs.NE", "cs.RO", "stat.ML"]

# 筛选关键词
KEYWORDS = [
    "machine learning",
    "deep learning", 
    "neural network",
    "artificial intelligence",
    "computer vision",
    "natural language processing",
    "transformer",
    "attention mechanism",
    "reinforcement learning",
    "diffusion",
    "large language model",
    "llm",
    "生成式AI",
    "深度学习"
]

# 排除关键词
EXCLUDE_KEYWORDS = [
    "survey",
    "review",
    "tutorial",
    "综述",
    "教程"
]

# 爬取设置
MAX_PAPERS_PER_CATEGORY = 50  # 每个类别最多爬取论文数
DAYS_BACK = 7  # 爬取最近几天的论文
```

## 🎯 为什么这样设计？

### ✅ 优点
1. **安全性**：敏感信息不暴露
2. **协作性**：团队成员可以共享应用配置
3. **灵活性**：每人有独立的敏感配置
4. **清晰性**：配置职责明确

### 📌 配置原则
| 配置项 | 类型 | 位置 | 是否提交Git |
|--------|------|------|------------|
| 邮箱密码 | 敏感 | .env | ❌ 否 |
| API密钥 | 敏感 | .env | ❌ 否 |
| 关键词 | 非敏感 | config.py | ✅ 是 |
| 类别 | 非敏感 | config.py | ✅ 是 |

## 🎯 为什么这样设计？

### ✅ 优点
1. **安全性**：敏感信息不暴露
2. **协作性**：团队成员可以共享应用配置
3. **灵活性**：每人有独立的敏感配置
4. **清晰性**：配置职责明确

### 📌 配置原则对比

| 配置项 | 类型 | 位置 | 是否提交Git | 特点 |
|--------|------|------|------------|------|
| 邮箱密码 | 敏感 | `.env` | ❌ 否 | 个人隐私 |
| API密钥 | 敏感 | `.env` | ❌ 否 | 个人密钥 |
| 收件人邮箱 | 敏感 | `.env` | ❌ 否 | 个人邮箱 |
| 关键词 | 非敏感 | `configs/config.py` | ✅ 是 | 共享配置 |
| 论文类别 | 非敏感 | `configs/config.py` | ✅ 是 | 共享配置 |
| 爬取参数 | 非敏感 | `configs/config.py` | ✅ 是 | 共享配置 |

## 🔧 如何配置

### 📧 首次配置

1. **创建.env文件**：
   ```bash
   cd /Users/cog/Desktop/💼工作文件/projects/arxiv_robot
   cp env_example.txt .env
   ```

2. **编辑.env文件**：
   ```bash
   # 163邮箱配置示例
   EMAIL_HOST=smtp.163.com
   EMAIL_PORT=465
   EMAIL_USER=your_email@163.com
   EMAIL_PASSWORD=your_client_authorization_password
   RECIPIENT_EMAIL=email1@163.com,email2@qq.com
   ```

3. **自定义关键词**（可选）：
   编辑 `configs/config.py` 文件，修改 `KEYWORDS` 列表

### 🎯 日常使用

- **修改邮箱配置**：编辑 `.env` 文件
- **修改关键词**：编辑 `configs/config.py` 文件
- **修改爬取参数**：编辑 `configs/config.py` 文件

### 🔍 查看配置

```bash
# 查看应用配置
cat configs/config.py

# 查看环境变量示例
cat env_example.txt

# 查看已配置的环境变量（不会显示敏感信息）
cat .env
```

## 📋 配置检查清单

- [ ] 已创建 `.env` 文件
- [ ] 已配置邮箱信息
- [ ] 已获取客户端授权密码（163邮箱）
- [ ] 已设置收件人邮箱
- [ ] （可选）已配置OpenAI API密钥
- [ ] （可选）已自定义关键词列表

## 🔗 相关文档

- [README.md](README.md) - 完整使用说明
- [env_example.txt](env_example.txt) - 环境变量示例
- [configs/config.py](configs/config.py) - 应用配置文件
