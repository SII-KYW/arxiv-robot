#!/usr/bin/env python3
"""
arXiv论文爬取机器人主程序
"""

import os
import sys
import logging
import time
from dotenv import load_dotenv

# 导入自定义模块
from utils.arxiv_crawler import ArxivCrawler
from utils.paper_filter import PaperFilter
from utils.ai_summarizer import AISummarizer
from utils.email_sender import EmailSender
from configs import config

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/arxiv_robot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ArxivRobot:
    """arXiv论文爬取机器人"""
    
    def __init__(self):
        # 验证配置
        self._validate_config()
        
        # 初始化组件
        self.crawler = ArxivCrawler(
            categories=config.ARXIV_CATEGORIES,
            max_papers_per_category=config.MAX_PAPERS_PER_CATEGORY
        )
        
        self.filter = PaperFilter(
            keywords=config.KEYWORDS,
            exclude_keywords=config.EXCLUDE_KEYWORDS
        )
        
        self.ai_summarizer = AISummarizer()
        self.email_sender = EmailSender()
    
    def _validate_config(self):
        """验证配置"""
        required_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"缺少必需配置: {', '.join(missing_vars)}")
            logger.error("请检查 .env 文件")
            sys.exit(1)
    
    def run(self) -> bool:
        """运行机器人"""
        try:
            logger.info("开始执行arXiv论文爬取任务...")
            
            # 1. 爬取论文
            papers = self.crawler.fetch_papers(days_back=config.DAYS_BACK)
            if not papers:
                logger.warning("未获取到任何论文")
                return True
            
            # 2. 筛选论文
            filtered_papers = self.filter.filter_papers(papers)
            if not filtered_papers:
                logger.info("未找到符合条件的论文")
                return True
            
            # 3. 发送邮件
            success = self.email_sender.send_email(filtered_papers, self.ai_summarizer)
            return success
            
        except Exception as e:
            logger.error(f"执行任务时出错: {e}")
            return False
    
    def test_email(self) -> bool:
        """测试邮件配置"""
        return self.email_sender.send_test_email()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        robot = ArxivRobot()
        
        if command == 'test':
            logger.info("执行邮件配置测试...")
            success = robot.test_email()
            sys.exit(0 if success else 1)
            
        elif command == 'run':
            logger.info("执行一次任务...")
            success = robot.run()
            sys.exit(0 if success else 1)
            
        elif command == 'help':
            print("""
arXiv论文爬取机器人使用说明:

python main.py test    - 测试邮件配置
python main.py run     - 执行一次任务
python main.py help    - 显示帮助信息
python main.py         - 启动定时任务

环境变量配置 (.env 文件):
- EMAIL_HOST: SMTP服务器地址
- EMAIL_PORT: SMTP端口
- EMAIL_USER: 发送邮箱
- EMAIL_PASSWORD: 邮箱密码或应用密码
- RECIPIENT_EMAIL: 接收邮箱
- OPENAI_API_KEY: OpenAI API密钥 (可选，用于AI总结)
- USE_AI_SUMMARY: 是否使用AI总结 (true/false)
            """)
            sys.exit(0)
    
    # 默认启动定时任务
    logger.info("启动定时任务...")
    
    try:
        import schedule
        robot = ArxivRobot()
        
        # 设置定时任务（每天上午9点执行）
        schedule.every().day.at("09:00").do(robot.run)
        
        logger.info("定时任务已设置，每天上午9点执行")
        logger.info("按 Ctrl+C 停止程序")
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
            
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except ImportError:
        logger.error("缺少schedule模块，请安装: pip install schedule")
        sys.exit(1)
    except Exception as e:
        logger.error(f"运行定时任务时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
