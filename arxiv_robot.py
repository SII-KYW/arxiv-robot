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
from utils.logger import setup_logger

log_path = os.path.join("logs", os.getenv("LOG_FILE", "arxiv_robot.log"))
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# 使用新的日志系统
setup_logger(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class ArxivRobot:
    """arXiv论文爬取机器人"""
    
    def __init__(self):
        # 验证配置
        self._validate_config()
        
        logger.info('\n\n'+"=" * 50)
        logger.info("📋 配置信息:")
        logger.info(f"  - arXiv类别: {len(config.ARXIV_CATEGORIES)} 个")
        logger.info(f"  - arXiv类别: \n{config.ARXIV_CATEGORIES}")
        logger.info(f"  - 每类爬取上限: {config.MAX_PAPERS_PER_CATEGORY} 篇")
        logger.info(f"  - 每组精选论文上限: {config.MAX_PAPERS_PER_GROUP} 篇")
        logger.info(f"  - 爬取天数: {config.DAYS_BACK} 天")
        logger.info(f"  - 筛选关键词组: {len(config.KEYWORDS)} 个")
        logger.info(f"  - 关键词组: \n{config.KEYWORDS}")
        logger.info(f"  - 排除全局关键词: {len(config.GLOBAL_EXCLUDE_KEYWORDS)} 个")
        logger.info(f"  - 排除全局关键词: \n{config.GLOBAL_EXCLUDE_KEYWORDS}")

        logger.info(f"  - 模型类型: {os.getenv('MODEL_TYPE')}")
        logger.info(f"  - 是否启用思考: {os.getenv('ENABLE_THINKING')}")
        logger.info(f"  - 是否启用AI总结: {os.getenv('USE_AI_SUMMARY')}")

        logger.info(f"  - 邮件接收人: \n{os.getenv('RECIPIENT_EMAIL')}")
        logger.info("=" * 50+"\n")
        
        # 初始化组件
        self.crawler = ArxivCrawler(
            categories=config.ARXIV_CATEGORIES,
            max_papers_per_category=config.MAX_PAPERS_PER_CATEGORY
        )
        
        self.filter = PaperFilter(
            keywords=config.KEYWORDS,
            global_keywords=config.GLOABL_KEYWORDS,
            global_exclude_keywords=config.GLOBAL_EXCLUDE_KEYWORDS,
        )
        
        self.ai_summarizer = AISummarizer()
        self.email_sender = EmailSender(
            max_paper_per_group=config.MAX_PAPERS_PER_GROUP
        )
    
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
            logger.info('\n'+"=" * 50)
            logger.info(f"📥 步骤1: 爬取论文 (最近{config.DAYS_BACK}天)")
            try:
                papers = self.crawler.fetch_papers(days_back=config.DAYS_BACK)
                if not papers:
                    logger.warning("⚠️ 未获取到任何论文，任务终止")
                    return True
                logger.info(f"✅ 爬取完成: {len(papers)} 篇论文")
            except Exception as e:
                logger.error(f"❌ 爬取失败: {e}")
                return False
            
            # 2. 筛选论文
            logger.info("=" * 50)
            # logger.info(f"🔍 步骤2: 筛选论文 (关键词数量: {len(config.KEYWORDS)}, 排除词: {len(config.EXCLUDE_KEYWORDS)})")
            logger.info(f"🔍 步骤2: 筛选论文 (关键词数量: {len(config.KEYWORDS)})")
            try:
                filtered_papers = self.filter.filter_papers(papers, ai_summarizer=self.ai_summarizer)
                if not filtered_papers:
                    logger.info("⚠️ 未找到符合条件的论文，任务终止")
                    return True
                # logger.info(f"✅ 筛选完成: {len(filtered_papers)} 篇相关论文")
                logger.info(f"✅ 筛选完成: {len([k for k, v in filtered_papers.items() if v])} 类相关论文")
            except Exception as e:
                logger.error(f"❌ 筛选失败: {e}")
                return False
            
            # 3. 总结论文并发送邮件
            logger.info("=" * 50)
            logger.info(f"📧 步骤3: 总结论文并发送邮件 (每个种类限制 {config.MAX_PAPERS_PER_GROUP} 篇)")
            try:
                success = self.email_sender.send_email(filtered_papers, ai_summarizer=self.ai_summarizer)
                if success:
                    logger.info(f"✅ 邮件发送完成")
                    logger.info("=" * 50)
                return success
            except Exception as e:
                logger.error(f"❌ 邮件发送失败: {e}")
                logger.info("=" * 50)
                return False
            
        except Exception as e:
            logger.error(f"执行任务时出错: {e}")
            logger.info("=" * 50)
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
        schedule.every().day.at(config.PROCESS_TIME).do(robot.run)
        
        logger.info(f"定时任务已设置，每天{config.PROCESS_TIME}执行")
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
