"""
邮件发送模块
"""

import smtplib
import logging
from email.mime.text import MIMEText
from typing import List, Dict
from datetime import datetime
import os

from utils.logger import APILogger

logger = logging.getLogger(__name__)
api_logger = APILogger("Email")


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.port = int(os.getenv('EMAIL_PORT', 587))
        self.username = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')
        
        # 支持多个收件人（用逗号分隔）
        recipient_str = os.getenv('RECIPIENT_EMAIL', '')
        self.recipient_emails = [email.strip() for email in recipient_str.split(',') if email.strip()]
    
    def format_email_content(self, papers: List[Dict], ai_summarizer) -> str:
        """格式化邮件内容"""
        if not papers:
            return "今日未发现相关论文。"
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        # 从config读取最大论文数
        from configs import config
        max_papers = min(len(papers), config.MAX_PAPERS_IN_EMAIL)
        total_count = max_papers
        
        # 邮件头部
        email_parts = [f"{date_str} arxiv每日精选paper，共 {total_count} 篇", ""]
        
        for i, paper in enumerate(papers[:max_papers], 1):
            # 分隔符
            email_parts.append("")
            email_parts.append(f"=== 每日精选 #{i}/{total_count} ===")
            
            # 标题
            email_parts.append(f"📄 标题: {paper['title']}")
            
            # 摘要
            if paper['abstract']:
                email_parts.append(f"📝 摘要:\n{paper['abstract']}")
            
            # AI总结
            logger.info(f"[{i}/{total_count}] 正在总结论文: {paper['title'][:50]}...")
            ai_summary = ai_summarizer.summarize_paper(paper['title'], paper['abstract'])
            
            # 检查是否失败
            if ai_summary.get('_ai_failed'):
                logger.warning(f"[{i}/{total_count}] ⚠️ AI总结失败，使用基础总结")
            else:
                logger.info(f"[{i}/{total_count}] 论文总结完成 ✅")
            
            if ai_summary['core_problem']:
                email_parts.append(f"🎯 核心问题：\n{ai_summary['core_problem']}")
            
            if ai_summary['key_approach']:
                email_parts.append(f"💡 关键思路：\n{ai_summary['key_approach']}")
            
            if ai_summary.get('main_conclusion'):
                email_parts.append(f"✨ 主要结论：\n{ai_summary['main_conclusion']}")

            
            # 发表时间
            if paper['published']:
                try:
                    pub_date = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
                    published_str = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
                    email_parts.append(f"📅 发表时间: {published_str}")
                except:
                    email_parts.append(f"📅 发表时间: {paper['published']}")

            
            # 链接
            if paper['link']:
                email_parts.append(f"🔗 ArXiv 链接: \n{paper['link']}")
            
            email_parts.append("")  # 空行分隔
        
        # 状态更新
        email_parts.append(f"[ℹ️ 状态更新 | {datetime.now().strftime('%H:%M:%S')}]")
        email_parts.append(f"✅ {date_str} 每日ArXiv论文监控任务完成！")
        email_parts.append(f"总共抓取 {len(papers) * 10} 篇新论文。")
        
        # 关键词统计
        keyword_stats = {}
        for paper in papers:
            for keyword in paper.get('matched_keywords', []):
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
        
        if keyword_stats:
            top_keyword = max(keyword_stats.items(), key=lambda x: x[1])
            email_parts.append(f"其中 {len(papers)} 篇通过关键词【{top_keyword[0]}】预筛。")
        
        email_parts.append(f"最终精选推送 {len(papers)} 篇。")
        
        return '\n'.join(email_parts)
    
    def send_email(self, papers: List[Dict], ai_summarizer) -> bool:
        """发送邮件"""
        try:
            # 创建邮件内容
            email_body = self.format_email_content(papers, ai_summarizer)
            date_str = datetime.now().strftime('%Y-%m-%d')
            subject = f"{date_str} 每日精选 #{len(papers)}"
            
            # 发送给所有收件人
            success_count = 0
            for recipient_email in self.recipient_emails:
                try:
                    # 创建邮件对象
                    msg = MIMEText(email_body, 'plain', 'utf-8')
                    msg['From'] = self.username
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    
                    # 发送邮件 - 支持163邮箱SSL连接
                    if self.host == 'smtp.163.com' and self.port == 465:
                        # 163邮箱SSL连接
                        with smtplib.SMTP_SSL(self.host, self.port) as server:
                            server.login(self.username, self.password)
                            server.sendmail(self.username, recipient_email, msg.as_string())
                    else:
                        # 其他邮箱TLS连接
                        with smtplib.SMTP(self.host, self.port) as server:
                            server.starttls()
                            server.login(self.username, self.password)
                            server.sendmail(self.username, recipient_email, msg.as_string())
                    
                    # 记录成功
                    api_logger.log_email_send(
                        recipient=recipient_email,
                        success=True
                    )
                    logger.info(f"邮件发送成功: {recipient_email}")
                    success_count += 1
                except Exception as e:
                    # 记录失败
                    api_logger.log_email_send(
                        recipient=recipient_email,
                        success=False,
                        error=str(e)
                    )
                    logger.error(f"发送邮件到 {recipient_email} 失败: {e}")
            
            logger.info(f"成功发送 {success_count}/{len(self.recipient_emails)} 封邮件")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """发送测试邮件"""
        try:
            test_body = f"""
您好！

这是arXiv论文爬取机器人的测试邮件。

发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明邮件配置正确。

祝好！
arXiv机器人
            """.strip()
            
            # 发送给所有收件人
            success_count = 0
            for recipient_email in self.recipient_emails:
                try:
                    msg = MIMEText(test_body, 'plain', 'utf-8')
                    msg['From'] = self.username
                    msg['To'] = recipient_email
                    msg['Subject'] = "[arXiv机器人] 测试邮件"
                    
                    # 发送测试邮件 - 支持163邮箱SSL连接
                    if self.host == 'smtp.163.com' and self.port == 465:
                        # 163邮箱SSL连接
                        with smtplib.SMTP_SSL(self.host, self.port) as server:
                            server.login(self.username, self.password)
                            server.sendmail(self.username, recipient_email, msg.as_string())
                    else:
                        # 其他邮箱TLS连接
                        with smtplib.SMTP(self.host, self.port) as server:
                            server.starttls()
                            server.login(self.username, self.password)
                            server.sendmail(self.username, recipient_email, msg.as_string())
                    
                    # 记录成功
                    api_logger.log_email_send(
                        recipient=recipient_email,
                        success=True
                    )
                    logger.info(f"测试邮件发送成功: {recipient_email}")
                    success_count += 1
                except Exception as e:
                    # 记录失败
                    api_logger.log_email_send(
                        recipient=recipient_email,
                        success=False,
                        error=str(e)
                    )
                    logger.error(f"发送测试邮件到 {recipient_email} 失败: {e}")
            
            logger.info(f"成功发送 {success_count}/{len(self.recipient_emails)} 封测试邮件")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"测试邮件发送失败: {e}")
            return False
