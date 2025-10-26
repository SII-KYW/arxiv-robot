"""
配置文件
"""

# arXiv配置
ARXIV_CATEGORIES = [
    "cs.AI",      # 人工智能
    "cs.CV",      # 计算机视觉
    "cs.LG",      # 机器学习
    "cs.CL",      # 计算语言学
    "cs.NE",      # 神经网络与进化计算
    "cs.RO",      # 机器人学
    "stat.ML"     # 统计机器学习
]

# 筛选关键词（支持中英文）
KEYWORDS = [
    # dllms
    "diffusion language model",
    "discrete diffusion model",
    "dllm",
    "discrete large language model",
    "diffusion"

    # # 基础AI关键词
    # "machine learning",
    # "deep learning", 
    # "neural network",
    # "artificial intelligence",
    # "computer vision",
    # "natural language processing",
    
    # # 热门技术
    # "transformer",
    # "attention mechanism",
    # "reinforcement learning",
    # "diffusion",
    # "large language model",
    # "llm",
    # "generative ai",
    # "foundation model",
    # "multimodal",
    # "gpt",
    # "bert",
    # "chatgpt",
    # "claude",
    # "gemini",
    
    # # 具体应用
    # "image generation",
    # "text generation",
    # "speech recognition",
    # "object detection",
    # "semantic segmentation",
    # "knowledge graph",
    # "recommendation system",
    # "anomaly detection",
    # "time series",
    # "graph neural network",
    # "gan",
    # "vae",
    # "autoencoder",
    
    # # 中文关键词
    # "机器学习",
    # "深度学习",
    # "神经网络",
    # "人工智能",
    # "计算机视觉",
    # "自然语言处理",
    # "扩散模型",
    # "大语言模型",
    # "生成式AI",
    # "多模态",
    # "图像生成",
    # "文本生成",
    # "语音识别",
    # "目标检测",
    # "语义分割",
    # "知识图谱",
    # "推荐系统",
    # "异常检测",
    # "时间序列",
    # "图神经网络"
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
MAX_PAPERS_PER_CATEGORY = 1  # 每个类别最多爬取论文数
DAYS_BACK = 1  # 爬取最近几天的论文（改为7天）

# 邮件设置
EMAIL_SUBJECT_PREFIX = "[arXiv日报]"
MAX_PAPERS_IN_EMAIL = 1  # 每封邮件最多包含论文数
