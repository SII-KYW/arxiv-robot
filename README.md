# arXiv论文爬取机器人

一个简洁的arXiv论文自动爬取和邮件推送工具。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置邮箱
复制环境变量示例文件：
```bash
cp template/env_example.txt .env && cp cp template/config.py ./configs/
```

编辑 `.env` 文件，填入您的邮箱信息：
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@gmail.com

# 可选：AI总结功能
OPENAI_API_KEY=your_openai_api_key
USE_AI_SUMMARY=true
```

### 3. 运行机器人

**测试邮件配置**：
```bash
python arxiv_robot.py test
```

**执行一次任务**：
```bash
python arxiv_robot.py run
```

**启动定时任务**（每天上午9点执行）：
```bash
python arxiv_robot.py
```

## 📧 邮件配置说明

### Gmail配置步骤：
1. 登录Gmail账户
2. 进入"管理您的Google账户" → "安全性"
3. 启用"两步验证"
4. 生成"应用专用密码"
5. 使用应用专用密码作为 `EMAIL_PASSWORD`

### 其他邮箱服务商：
- **QQ邮箱**: `smtp.qq.com:587`
- **163邮箱**: `smtp.163.com:587`
- **Outlook**: `smtp-mail.outlook.com:587`

## 🤖 AI总结功能

设置OpenAI API密钥后，机器人将使用AI生成更高质量的论文总结：

1. 注册OpenAI账户并获取API密钥
2. 在 `.env` 文件中设置 `OPENAI_API_KEY`
3. 设置 `USE_AI_SUMMARY=true`

## 📊 邮件内容示例

```
2024-10-24 每日精选 #4

标题: dInfer: An Efficient Inference Framework for Diffusion Language Models
摘要:
This paper aims to solve the lack of standardized and efficient inference frameworks...

核心问题：
这篇论文旨在解决基于扩散的大型语言模型缺乏标准化且高效推理框架的问题...

关键思路或结论：
提出dInfer框架，将推理流程分解为四个模块化组件，并结合算法创新与系统级优化...

发表时间: Thu, 23 Oct 2024 00:00:00 +0000
🔗 ArXiv 链接

[ℹ️ 状态更新 | 10:34:24]
✅ 2024-10-24 每日ArXiv论文监控任务完成！
总共抓取 300 篇新论文。
其中 4 篇通过关键词【diffusion】预筛。
最终精选推送 4 篇。
```

## 🔧 自定义配置

编辑 `configs/config.py` 文件中的配置：

```python
# arXiv类别
ARXIV_CATEGORIES = ["cs.AI", "cs.CV", "cs.LG", "cs.CL", "cs.NE", "cs.RO", "stat.ML"]

# 筛选关键词
KEYWORDS = [
    "machine learning", "deep learning", "neural network",
    "artificial intelligence", "computer vision", "natural language processing",
    "transformer", "attention mechanism", "reinforcement learning",
    "diffusion", "large language model", "llm", "generative ai",
    "foundation model", "multimodal"
]

# 排除关键词
EXCLUDE_KEYWORDS = ["survey", "review", "tutorial"]
```

详细配置说明请查看：[配置指南](docs/CONFIG_GUIDE.md)

## 📁 项目结构

```
arxiv_robot/
├── arxiv_robot.py          # 主程序入口
├── configs/
│   ├── __init__.py
│   └── config.py          # 应用配置（关键词、类别）
├── utils/
│   ├── __init__.py
│   ├── arxiv_crawler.py   # arXiv爬虫模块
│   ├── paper_filter.py    # 论文筛选模块
│   ├── ai_summarizer.py   # AI总结模块
│   └── email_sender.py     # 邮件发送模块
├── docs/
│   ├── CONFIG_GUIDE.md    # 详细配置指南
│   └── env_example.txt    # 环境变量示例
├── output/
│   └── arxiv_robot.log    # 运行日志
├── requirements.txt        # 依赖包
├── README.md             # 使用说明
├── .gitignore           # Git忽略文件
└── .env                 # 环境变量（需自行创建，不提交Git）
```

## 🐛 故障排除

### 常见问题：

1. **邮件发送失败**
   - 检查邮箱配置是否正确
   - 确认使用应用密码
   - 检查网络连接

2. **爬取失败**
   - 检查网络连接
   - 查看日志文件 `arxiv_robot.log`

3. **AI总结失败**
   - 检查OpenAI API密钥是否正确
   - 确认API余额充足

### 查看日志：
```bash
tail -f output/arxiv_robot.log
```

## 🎉 完成！

现在您的arXiv论文爬取机器人已经准备就绪！

- ✅ 自动爬取arXiv最新论文
- ✅ 智能关键词筛选
- ✅ AI高质量总结（可选）
- ✅ 自动邮件推送
- ✅ 定时任务支持

享受您的个性化论文推送服务！📚✨