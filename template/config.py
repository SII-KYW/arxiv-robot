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

GLOABL_KEYWORDS = [
    
]

# 排除关键词
GLOBAL_EXCLUDE_KEYWORDS = [
    "survey",
    "review",
    "tutorial",
    "综述",
    "教程"
]

# group keywords
# format with keywords and exclude_keywords: 
# {"group_name": [[keywords], [exclude_keywords]] }
# format with only keywords: 
# {"group_name": [keywords]}
KEYWORDS = {
    "dllm": [
        "diffusion language model",
        "discrete diffusion model",
        "dllm",
        "discrete large language model",
        "diffusion"
    ],
    "video understanding": [
        "video",
        "video understanding",
        "video large language model",
        "video llm",
        "vllm",
        "vlm"
    ],
}


# 爬取设置
MAX_PAPERS_PER_CATEGORY = 5000  # 每个类别最多爬取论文数
DAYS_BACK = 7  # 爬取最近几天的论文（改为7天）

# 邮件设置
EMAIL_SUBJECT_PREFIX = "[arXiv日报]"
MAX_PAPERS_PER_GROUP = 5  # 每封邮件最多包含论文数

PROCESS_TIME = "00:01"