"""
邮件发送模块
"""

import smtplib
import logging
from email.mime.text import MIMEText
from typing import List, Dict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.port = int(os.getenv('EMAIL_PORT', 587))
        self.username = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    def format_email_content(self, papers: List[Dict], ai_summarizer) -> str:
        """格式化邮件内容"""
        if not papers:
            return "今日未发现相关论文。"
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        email_parts = [f"{date_str} 每日精选 #{len(papers)}", ""]
        
        for i, paper in enumerate(papers[:20], 1):  # 限制20篇
            # 标题
            email_parts.append(f"标题: {paper['title']}")
            
            # 摘要
            if paper['abstract']:
                email_parts.append(f"摘要:\n{paper['abstract']}")
            
            # AI总结
            ai_summary = ai_summarizer.summarize_paper(paper['title'], paper['abstract'])
            
            if ai_summary['core_problem']:
                email_parts.append(f"核心问题：\n{ai_summary['core_problem']}")
            
            if ai_summary['key_approach']:
                email_parts.append(f"关键思路或结论：\n{ai_summary['key_approach']}")
            
            # 发表时间
            if paper['published']:
                try:
                    pub_date = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
                    published_str = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
                    email_parts.append(f"发表时间: {published_str}")
                except:
                    email_parts.append(f"发表时间: {paper['published']}")
            
            # 链接
            if paper['link']:
                email_parts.append(f"🔗 ArXiv 链接")
            
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
            
            # 创建邮件对象
            msg = MIMEText(email_body, 'plain', 'utf-8')
            msg['From'] = self.username
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # 发送邮件 - 支持163邮箱SSL连接
            if self.host == 'smtp.163.com' and self.port == 465:
                # 163邮箱SSL连接
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.recipient_email, msg.as_string())
            else:
                # 其他邮箱TLS连接
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.recipient_email, msg.as_string())
            
            logger.info("邮件发送成功")
            return True
            
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
            
            msg = MIMEText(test_body, 'plain', 'utf-8')
            msg['From'] = self.username
            msg['To'] = self.recipient_email
            msg['Subject'] = "[arXiv机器人] 测试邮件"
            
            # 发送测试邮件 - 支持163邮箱SSL连接
            if self.host == 'smtp.163.com' and self.port == 465:
                # 163邮箱SSL连接
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.recipient_email, msg.as_string())
            else:
                # 其他邮箱TLS连接
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.recipient_email, msg.as_string())
            
            logger.info("测试邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"测试邮件发送失败: {e}")
            return False
